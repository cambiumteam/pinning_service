import asyncio
import json
from urllib.parse import urljoin

import requests
import websockets

from .config import get_settings
from .graph import add_graph_to_store

settings = get_settings()


# Subscribe to register resolver events.
async def subscribe():
    subscription = {
        "jsonrpc": "2.0",
        "method": "subscribe",
        "id": 1,
        "params": {
            "query": f"tm.event='Tx' AND regen.data.v1.EventRegisterResolver.id = {settings.REGEN_RESOLVER_ID}",
        }
    }

    # Open a websocket connection and reconnect if the connection closes.
    async for websocket in websockets.connect(settings.REGEN_NODE_TENDERMINT_WS_URL):
        try:
            await websocket.send(json.dumps(subscription))
            await listen(websocket)
        except websockets.ConnectionClosed:
            await asyncio.sleep(5)
            continue


# Listen and index newly registered data.
async def listen(websocket):
    resolver_urls = {}
    async for message in websocket:

        # Non result message, subscription response.
        result = json.loads(message).get("result", {})
        if "events" not in result:
            continue

        # Get all resolver ids the data was registered to.
        resolver_ids = [int(resolver_id.replace("\"", '')) for resolver_id in result.get("events", {}).get("regen.data.v1.EventRegisterResolver.id", [])]

        # Query to get each resolvers URL.
        for resolver_id in resolver_ids:
            if resolver_urls.get(resolver_id, None) is not None:
                continue
            try:
                resolver_urls[resolver_id] = get_resolver_url(resolver_id)
            except Exception as e:
                print(e)
                continue

        # TODO: What if data is registered to multiple resolvers in the same tx?
        resolver_id = resolver_ids.pop()
        resolver_url = resolver_urls.get(resolver_id)

        # Index each IRI that was anchored.
        event_name = "regen.data.v1.EventRegisterResolver.iri"
        for iri in result.get("events", {}).get(event_name, []):
            iri = iri.replace("\"", '')
            try:
                index_iri(resolver_url, iri)
                print(f"Indexed {iri}")
            except Exception as e:
                print(e)
                continue


# Request graph data from the resolver and add to graph store.
def index_iri(resolver_url: str, iri: str):
    format = "application/ld+json"
    resource_url = f"{resolver_url.rstrip('/')}/{iri}"
    response = requests.get(resource_url, headers={"Accept": format})
    add_graph_to_store(iri, response.content, settings, format=format)


# Helper function to get resolver URLs.
def get_resolver_url(resolver_id: int) -> str:
    api_url = urljoin(settings.REGEN_NODE_REST_URL, f"regen/data/v1/resolver/{resolver_id}")
    response = requests.get(api_url)
    return response.json().get("resolver", {}).get("url")


if __name__ == "__main__":
    asyncio.run(subscribe())