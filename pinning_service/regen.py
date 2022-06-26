import os
import json
from typing import NewType
from .config import get_settings
from collections.abc import Iterable


settings = get_settings()

TxHash = NewType('TxHash', str)
IRI = NewType('IRI', str)
Address = NewType('Address', str)


def generate_content_hash(b64_hash: str) -> dict:
    return {
        "raw": None,
        "graph": {
            "hash": b64_hash,
            "digest_algorithm": "DIGEST_ALGORITHM_BLAKE2B_256",
            "canonicalization_algorithm": "GRAPH_CANONICALIZATION_ALGORITHM_URDNA2015",
            "merkle_tree": "GRAPH_MERKLE_TREE_NONE_UNSPECIFIED"
        }
    }

def generate_anchor_tx(sender: Address, resolver_id: int, b64_hashes: Iterable[str]) -> dict:
    content_hashes = [generate_content_hash(b64_hash) for b64_hash in b64_hashes]
    print(b64_hashes)
    return {
        "body": {
            "messages": [{
                "@type": "/regen.data.v1.MsgRegisterResolver",
                "manager": sender,
                "resolver_id": resolver_id,
                "content_hashes": content_hashes,
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


def anchor(b64_hashes: Iterable[str]) -> TxHash:

    # Build flags.
    chain_id = f"--chain-id {settings.REGEN_CHAIN_ID}"
    node = f"--node {settings.REGEN_NODE_TENDERMINT_RPC_URL}"
    output = "--output json"
    tx = generate_anchor_tx(settings.REGEN_KEY_ADDRESS, settings.REGEN_RESOLVER_ID, b64_hashes)
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
