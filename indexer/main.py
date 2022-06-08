import asyncio
import base64
import json
from urllib.parse import urljoin

import requests
import websockets

from .config import get_settings
from .graph import add_graph_to_store

settings = get_settings()
resolver_urls = {}

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
    async for message in websocket:
        # Build a mapping of IRI to the registered resolver.
        iri_resolver_mapping = parse_register_resolver_message(message)

        # Index each IRI.
        for iri, resolver_id in iri_resolver_mapping.items():
            try:
                # Need a delay in case the resolver has not yet stored the data.
                # This will be solved when registering data with the resolver happens in a job queue.
                await asyncio.sleep(2)
                resolver_url = get_resolver_url(resolver_id)
                index_iri(resolver_url, iri)
                print(f"Indexed {iri}")
            except Exception as e:
                print(e)
                continue


def parse_register_resolver_message(message: str) -> dict:
    # Check the data type.
    result_data = json.loads(message).get("result", {}).get("data", {})
    if result_data.get("type") != "tendermint/event/Tx":
        return {}

    # Use the nested TX events instead of the high-level query events
    # because the TX events specify which resolver data was registered to.
    tx_events = result_data.get("value", {}).get("TxResult", {}).get("result", {}).get("events", [])

    # Parse the raw register resolver events.
    register_resolver_event_name = "regen.data.v1.EventRegisterResolver"
    register_resolver_events = [
        dict(map(decode_event_attribute, event.get("attributes")))
        for event in tx_events if event.get("type") == register_resolver_event_name
    ]

    # Return a dict mapping IRI to resolver ID. Remove extra parenthesis from the IRI and ID.
    return dict(map(
        lambda event: (event.get("iri").replace("\"", ''), event.get("id").replace("\"", '')),
        register_resolver_events
    ))


# Function to decode the base64 encoded key and value from Tx event attributes.
def decode_event_attribute(attribute: dict) -> tuple:
    return base64.b64decode(attribute.get("key")).decode('utf-8'), base64.b64decode(attribute.get("value")).decode('utf-8')


# Request graph data from the resolver and add to graph store.
def index_iri(resolver_url: str, iri: str):
    format = "application/ld+json"
    resource_url = f"{resolver_url.rstrip('/')}/{iri}"
    response = requests.get(resource_url, headers={"Accept": format})
    add_graph_to_store(iri, response.content, settings, format=format)


# Helper functions to get resolver URLs.
def get_resolver_url(resolver_id: int) -> str:
    if resolver_id not in resolver_urls:
        url = fetch_resolver_url(resolver_id)
        resolver_urls[resolver_id] = url
    return resolver_urls.get(resolver_id)


def fetch_resolver_url(resolver_id: int) -> str:
    api_url = urljoin(settings.REGEN_NODE_REST_URL, f"regen/data/v1/resolver/{resolver_id}")
    response = requests.get(api_url)
    return response.json().get("resolver", {}).get("url")


if __name__ == "__main__":
    asyncio.run(subscribe())