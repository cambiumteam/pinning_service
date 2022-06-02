import os
import json
from typing import NewType
from .config import get_settings

settings = get_settings()

TxHash = NewType('TxHash', str)
IRI = NewType('IRI', str)
Address = NewType('Address', str)


def generate_anchor_tx(sender: Address, resolver_id: int, b64_hash: str) -> dict:
    return {
        "body": {
            "messages": [{
                "@type": "/regen.data.v1.MsgRegisterResolver",
                "manager": sender,
                "resolver_id": resolver_id,
                "content_hashes": [
                  {
                    "raw": None,
                    "graph": {
                      "hash": b64_hash,
                      "digest_algorithm": "DIGEST_ALGORITHM_BLAKE2B_256",
                      "canonicalization_algorithm": "GRAPH_CANONICALIZATION_ALGORITHM_URDNA2015",
                      "merkle_tree": "GRAPH_MERKLE_TREE_NONE_UNSPECIFIED"
                    }
                  }
                ]
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


def anchor(b64_hash: bytes) -> dict:

    # Build flags.
    chain_id = f"--chain-id {settings.REGEN_CHAIN_ID}"
    node = f"--node {settings.REGEN_NODE_TENDERMINT_RPC_URL}"
    output = "--output json"
    tx = generate_anchor_tx(settings.REGEN_KEY_ADDRESS, settings.REGEN_RESOLVER_ID, b64_hash.decode('utf-8'))
    sign_command = f"echo '{json.dumps(tx)}' | {settings.REGEN_CLI_COMMAND} regen tx sign /dev/stdin --from {settings.REGEN_KEY_ADDRESS} {settings.REGEN_KEYRING_ARGS} {chain_id} {node} {output}"

    # Sign the transaction.
    try:
        signed_tx = json.loads(os.popen(sign_command).read())
    except Exception:
        raise ValueError("Failed to sign transaction.")

    # Broadcast transaction.
    # @TODO: make use of regen config passing REGEN_HOME
    broadcast_command = f"echo '{json.dumps(signed_tx)}' | {settings.REGEN_CLI_COMMAND} regen tx broadcast /dev/stdin {chain_id} {node} {output}"
    try:
        result = json.loads(os.popen(broadcast_command).read())
    except Exception:
        raise ValueError("Failed to broadcast transaction.")

    return result


def get_successful_txhash(tx_result: dict) -> TxHash:
    if tx_result["code"] != 0:
        raise ValueError('Invalid transactions result code')
    
    return tx_result["txhash"]
