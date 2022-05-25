import base64
from typing import Any
import hashlib

from fastapi import FastAPI, Body, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pyld import jsonld
from rdflib import ConjunctiveGraph
from rdflib.plugin import PluginException
import sqlalchemy
from sqlalchemy import select
import uvicorn

from config import get_settings, Settings
from database import database, metadata, resources
from graph import add_graph_to_store

# Settings dependency.
settings = get_settings()

# Create tables.
engine = sqlalchemy.create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

# Create FastAPI app.
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Default JSONLD response class.
# This prevents application/json being shown as default.
class JsonLdResponse(Response):
    media_type = "application/ld+json"


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


@app.get('/resources', response_class=JSONResponse)
async def get_resources():
    data = await database.fetch_all(query=select(resources))
    resp = jsonable_encoder([{
        'iri': resource.iri,
        'hash': base64.urlsafe_b64encode(resource.hash),
        'data': resource.data,
    } for resource in data])
    return JSONResponse(resp)


# Get resource by IRI.
@app.get("/resource/{iri}", response_class=JsonLdResponse, responses=responses)
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
@app.post("/resource")
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
    base64_hash = base64.urlsafe_b64encode(digest)

    # Get the IRI.
    # @TODO Query regen for the IRI.
    iri = f"regen:{base64_hash.decode()[0:10]}.rdf"

    if settings.USE_GRAPH_STORE:
        add_graph_to_store(iri, normalized, settings)

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
        return HTTPException(status_code=422, detail=e.args)

    return {"iri": iri, "hash": base64_hash, "data": normalized}


# Run app.
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
