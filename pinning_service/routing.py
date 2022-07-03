import base64
from datetime import datetime
from typing import Any
import hashlib
import traceback

from fastapi import APIRouter, Body, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pyld import jsonld
from rdflib import ConjunctiveGraph
from rdflib.plugin import PluginException
from sqlalchemy import select

from .content_hash import ContentHash, ContentHashGraph, DigestAlgorithm, GraphCanonicalizationAlgorithm, GraphMerkleTree
from .database import database, resources
from .task_queue import anchor_batch_deferred
from .iri import to_iri


# JSONLD response class.
# This prevents application/json being shown as default.
class JsonLdResponse(Response):
    media_type = "application/ld+json"


# Start an API router.
router = APIRouter()


# Get all resources.
@router.get('/resources', response_class=JSONResponse)
async def get_resources():
    data = await database.fetch_all(query=select(resources))
    resp = jsonable_encoder([{
        'iri': resource.iri,
        'hash': base64.urlsafe_b64encode(resource.hash),
        'data': resource.data,
        'txhash': resource.txhash,
    } for resource in data])
    return JSONResponse(resp)


# Define additional response content types.
responses = {
    200: {
        "content": {
            "application/ld+json": {"schema": {"type": "object"}},
            "text/turtle": {"schema": {"type": "string"}},
            "application/n-quads": {"schema": {"type": "string"}},
        },
        "description": "Serialized RDF data",
    },
}


# Get resource by IRI.
@router.get("/resource/{iri}", response_class=JsonLdResponse, responses=responses)
async def get_resource(iri: str, request: Request):

    # Query data by IRI.
    query = select(resources.c.data).where(resources.columns.iri==iri)
    data = await database.fetch_val(query)
    if data is None:
        raise HTTPException(status_code=404)

    # Serialize to the requested format.
    try:
        accept = request.headers.get("accept")
        graph = ConjunctiveGraph()
        graph.parse(data=data, format="application/n-quads")
        serialized = graph.serialize(format=accept)
    # Return 406 if the format is not supported.
    except PluginException:
        raise HTTPException(status_code=406)

    return Response(serialized, media_type=accept)


@router.get("/resource/{iri}/status", response_class=JSONResponse)
async def get_resource_status(iri: str, request: Request):
    query = select(resources.c.anchor_attempts, resources.c.txhash).where(
        resources.c.iri == iri
    )
    data = await database.fetch_one(query)
    if data is None:
        raise HTTPException(status_code=404)

    status = "pending"

    if data.anchor_attempts > 4 and data.txhash is None:
        status = "failure"
    elif data.txhash is not None:
        status = "success"

    # @TODO: add pinned_at, anchored_at ?  
    response = jsonable_encoder({ 
        "status": status,  
    })
    return JSONResponse(response)


async def resource_exists(digest: bytes) -> bool:
    query = select(resources.c.iri).where(resources.c.hash == digest)
    iri = await database.fetch_val(query)
    return bool(iri)


# Create new resource.
@router.post("/resource", status_code=201)
async def post_resource(
        data: Any = Body(..., media_type='application/ld+json'),
):

    # Canonicalization.
    try:
        normalized = jsonld.normalize(data, {
            'format': 'application/n-quads',
            'algorithm': 'URDNA2015'
        })
    # Raise validation error.
    except jsonld.JsonLdError as e:
        raise HTTPException(status_code=422, detail=e.details)

    # Hash.
    binary = normalized.encode('utf-8')
    digest = hashlib.blake2b(binary, digest_size=32).digest()
    base64_hash = base64.b64encode(digest)

    # Build content hash and generate IRI.
    try:
        content_hash_graph = ContentHashGraph(
            hash=digest,
            digest_algorithm=DigestAlgorithm.BLAKE2B_256,
            canonicalization_algorithm=GraphCanonicalizationAlgorithm.URDNA2015,
            merkle_tree=GraphMerkleTree.NONE_UNSPECIFIED,
        )
        content_hash = ContentHash(graph=content_hash_graph)
        iri = to_iri(content_hash)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid content hash: {e}")

    # Check if resource is already pinned
    try:
        exists = await resource_exists(digest)
    except Exception:
        # @TODO: should this just return a 302 and return the resource that was already pinned?
        # @TODO: what if the resource already exists, but has failed? seems like we should provide a try again
        traceback.print_exc()
        # Database error
        raise HTTPException(status_code=503, detail=f"Failed to pin resource")
    
    if exists:
            raise HTTPException(status_code=409, detail=f"Resource {iri} already exists")
        
    # Pin resource to database    
    final = {
        "iri": iri,
        "hash": digest,
        "data": normalized,
        "txhash": None,
        "anchor_attempts": 0,
        # @TODO: store UTC timezone info
        "pinned_at": datetime.now(),
    }
    try:
        query = resources.insert().values(**final)
        await database.execute(query)
    except Exception as e:
        # @TODO Improve handling of duplicate data.
        raise HTTPException(status_code=422, detail=e.args)

    # Anchor the data on-chain.
    try:
        await anchor_batch_deferred()

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to anchor data on-chain: {e}")

    # Return response
    return {
        "iri": iri, 
        "hash": base64_hash, 
        "data": normalized, 
        "txhash": None,
        "anchor_attempts": 0,
        "pinned_at": final["pinned_at"]
    }

