import base64
from typing import Any
import hashlib
from urllib.parse import urljoin

from fastapi import APIRouter, Body, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pyld import jsonld
import requests
from rdflib import ConjunctiveGraph
from rdflib.plugin import PluginException
from sqlalchemy import select

from .config import get_settings, Settings
from .database import database, resources
from .graph import add_graph_to_store
from .regen import anchor


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


# Create new resource.
@router.post("/resource")
async def post_resource(
        data: Any = Body(..., media_type='application/ld+json'),
        settings: Settings = Depends(get_settings),
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

    try:
        tx = anchor(base64_hash)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to anchor data on-chain: {e}")
        
    # Query regen node for the IRI.
    params = {
        "hash": base64_hash,
        "digest_algorithm": "DIGEST_ALGORITHM_BLAKE2B_256",
        "canonicalization_algorithm": "GRAPH_CANONICALIZATION_ALGORITHM_URDNA2015",
        "merkle_tree": "GRAPH_MERKLE_TREE_NONE_UNSPECIFIED",
    }
    try:
        api_url = urljoin(settings.REGEN_NODE_REST_URL, "regen/data/v1/iri-by-graph")
        res = requests.get(api_url, params)
        iri = res.json()["iri"]
    except Exception as e:
        raise HTTPException(status_code=503, detail="Failed to query regen node.")

    final = {
        "iri": iri,
        "hash": digest,
        "data": normalized,
    }
    try:
        query = resources.insert().values(**final)
        await database.execute(query)
    except Exception as e:
        # @TODO Improve handling of duplicate data.
        raise HTTPException(status_code=422, detail=e.args)

    if settings.USE_GRAPH_STORE:
        add_graph_to_store(iri, normalized, settings)

    return {"iri": iri, "hash": base64_hash, "data": normalized}