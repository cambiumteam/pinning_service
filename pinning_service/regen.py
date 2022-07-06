import os
import json
from typing import NewType
from collections.abc import Iterable

from .config import get_settings
from .content_hash import ContentHash

settings = get_settings()

TxHash = NewType("TxHash", str)
IRI = NewType("IRI", str)
Address = NewType("Address", str)


def generate_anchor_tx(
    sender: Address,
    resolver_id: int,
    content_hashes: Iterable[ContentHash],
) -> dict:

    # Convert content_hash to dict so they can be json encoded.
    content_hashes_list = [content_hash.dict() for content_hash in content_hashes]

    return {
        "body": {
            "messages": [
                {
                    "@type": "/regen.data.v1.MsgRegisterResolver",
                    "manager": sender,
                    "resolver_id": resolver_id,
                    "content_hashes": content_hashes_list,
                }
            ],
        },
    }


def anchor(content_hashes: Iterable[ContentHash]) -> TxHash:

    # Build anchoring message
    tx = generate_anchor_tx(
        sender=settings.REGEN_KEY_ADDRESS,
        resolver_id=settings.REGEN_RESOLVER_ID,
        content_hashes=content_hashes,
    )

    # Execute transaction from service account
    flags = {
        "--from": settings.REGEN_SERVICE_KEY_ADDRESS,
        "--fee-account": settings.REGEN_KEY_ADDRESS,
        "--gas-prices": f"{settings.REGEN_GAS_PRICES_AMOUNT:f}{settings.REGEN_GAS_PRICES_DENOM}",
        "--broadcast-mode": "block",
        "--yes": "",
        "--chain-id": settings.REGEN_CHAIN_ID,
        "--node": settings.REGEN_NODE_TENDERMINT_RPC_URL,
        "--output": "json",
    }
    flags_str = str.join(" ", [f"{key} {val}" for key, val in flags.items()])
    regen_command = f"{settings.REGEN_CLI_COMMAND} regen tx authz exec /dev/stdin {flags_str} {settings.REGEN_KEYRING_ARGS}"
    execute_command = f"echo '{json.dumps(tx)}' | {regen_command}"
    try:
        tx_result = json.loads(os.popen(execute_command).read())
    except Exception:
        raise ValueError("Failed to execute transaction.")

    # Check the transaction result to ensure it was successful.
    return get_successful_txhash(tx_result)


def get_successful_txhash(tx_result: dict) -> TxHash:

    # Check that a valid code was returned.
    if tx_result["code"] != 0:
        raise ValueError(tx_result["raw_log"])

    # Check that the proper events happened.
    log = next(log for log in tx_result["logs"] if log["msg_index"] == 0)

    # Ensure data was anchored.
    try:
        next(
            event
            for event in log["events"]
            if event["type"] == "regen.data.v1.EventAnchor"
        )
    except StopIteration:
        raise ValueError(
            "No anchor event from transaction. The data may already be anchored."
        )

    # Ensure data was registered with the resolver.
    try:
        next(
            event
            for event in log["events"]
            if event["type"] == "regen.data.v1.EventRegisterResolver"
        )
    except StopIteration:
        raise ValueError("No register event from transaction.")

    return tx_result["txhash"]
