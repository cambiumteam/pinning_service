import os
import json
from typing import NewType
from collections.abc import Iterable

from .config import get_settings
from .content_hash import ContentHash

settings = get_settings()

TxHash = NewType('TxHash', str)
IRI = NewType('IRI', str)
Address = NewType('Address', str)


def generate_anchor_tx(sender: Address, resolver_id: int, content_hashes: Iterable[ContentHash]) -> dict:

    # Convert content_hash to dict so they can be json encoded.
    content_hashes_list = [content_hash.dict() for content_hash in content_hashes]

    return {
        "body": {
            "messages": [{
                "@type": "/regen.data.v1.MsgRegisterResolver",
                "manager": sender,
                "resolver_id": resolver_id,
                "content_hashes": content_hashes_list,
            }],
            "memo": "",
            "timeout_height": "0",
            "extension_options": [],
            "non_critical_extension_options": []
        },
        "auth_info": {
            "signer_infos": [],
            "fee": {
                "amount": [
                    {"denom": "stake", "amount": "2"},
                ],
                "gas_limit": "200000",
                "payer": "",
                "granter": ""
            }
        },
        "signatures": []
    }


def anchor(content_hashes: Iterable[ContentHash]) -> TxHash:

    # Build flags.
    chain_id = f"--chain-id {settings.REGEN_CHAIN_ID}"
    node = f"--node {settings.REGEN_NODE_TENDERMINT_RPC_URL}"
    output = "--output json"
    tx = generate_anchor_tx(settings.REGEN_KEY_ADDRESS, settings.REGEN_RESOLVER_ID, content_hashes)
    sign_command = f"echo '{json.dumps(tx)}' | {settings.REGEN_CLI_COMMAND} regen tx sign /dev/stdin --from {settings.REGEN_KEY_ADDRESS} {settings.REGEN_KEYRING_ARGS} {chain_id} {node} {output}"

    # Sign the transaction.
    try:
        signed_tx = json.loads(os.popen(sign_command).read())
    except Exception:
        raise ValueError("Failed to sign transaction.")

    # Broadcast transaction.
    # @TODO: make use of regen config passing REGEN_HOME
    broadcast_command = f"echo '{json.dumps(signed_tx)}' | {settings.REGEN_CLI_COMMAND} regen tx broadcast /dev/stdin --broadcast-mode block {chain_id} {node} {output}"
    try:
        tx_result = json.loads(os.popen(broadcast_command).read())
    except Exception:
        raise ValueError("Failed to broadcast transaction.")

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
        next(event for event in log["events"] if event["type"] == "regen.data.v1.EventAnchor")
    except StopIteration:
        raise ValueError("No anchor event from transaction. The data may already be anchored.")

    # Ensure data was registered with the resolver.
    try:
        next(event for event in log["events"] if event["type"] == "regen.data.v1.EventRegisterResolver")
    except StopIteration:
        raise ValueError("No register event from transaction.")

    return tx_result["txhash"]
