import os
import subprocess
import json
from typing import NewType
from .config import get_settings

settings = get_settings()

TxHash = NewType('TxHash', str)
IRI = NewType('IRI', str)
Address = NewType('Address', str)


def generate_anchor_tx(sender: Address, b64_hash: bytes) -> dict:
    return {
        "body": {
            "messages": [{
                "@type": "/regen.data.v1.MsgAnchor",
                "sender": sender,
                "content_hash": {
                    "raw": None,
                    "graph": {
                        "hash": b64_hash.decode('utf-8'),
                        "digest_algorithm": "DIGEST_ALGORITHM_BLAKE2B_256",
                        "canonicalization_algorithm": "GRAPH_CANONICALIZATION_ALGORITHM_URDNA2015",
                        "merkle_tree": "GRAPH_MERKLE_TREE_NONE_UNSPECIFIED"
                    }
                }
            }],
            "memo": "",
            "timeout_height": "0",
            "extension_options": [],
            "non_critical_extension_options": []
        },
        "auth_info": {
            "signer_infos": [],
            "fee": {
                "amount": [],
                "gas_limit": "200000",
                "payer": "",
                "granter": ""
            }
        },
        "signatures": []
    }


def anchor(b64_hash: str) -> TxHash:
    # command = '''
    #     docker run --rm --network host \
    #         -v $(pwd)/docker/.testnets/keys:/regen-keys ghcr.io/cambiumteam/pinning_service:regen-test \
    #         regen tx data anchor regen:13toVgomo1yAFYxMXAVGn4AfgXdeNwgcbgTihpnua4mtdvNaxxZQeeF.rdf --from pinning-service-test -y \
    #         --keyring-backend test --keyring-dir /regen-keys/ \
    #         --chain-id chain-YsT5fv --node http://localhost:26657 \
    #         --gas auto --fees 2stake
    # '''
    # operation = f"tx data anchor {iri} --from {settings.REGEN_KEY_NAME}"
    chain_id = f"--chain-id {settings.REGEN_CHAIN_ID}"
    node = f"--node {settings.REGEN_NODE_TENDERMINT_RPC_URL}"
    output = "--output json"
    flags = f"{settings.REGEN_KEYRING_ARGS}  {chain_id} {node} {settings.REGEN_GAS_FEES_ARGS} {output}"
    # command = f"{settings.REGEN_CLI_COMMAND} {operation} {flags}"
    # try:
    #     tx = json.loads(os.system(command))
    tx = generate_anchor_tx(settings.REGEN_KEY_ADDRESS, b64_hash)
    print(tx)
    # sign_command = f"echo '{json.dumps(tx)}' | {settings.REGEN_CLI_COMMAND} regen tx sign /dev/stdin {chain_id} {node}"
    # sign_command = f"{settings.REGEN_CLI_COMMAND} sh -c 'echo \'{json.dumps(tx)}\' | regen tx sign /dev/stdin --from {settings.REGEN_KEY_ADDRESS} {settings.REGEN_KEYRING_ARGS} {chain_id} {node} {output}'"
    # sign_command = f"{settings.REGEN_CLI_COMMAND} sh -c 'regen tx sign /dev/stdin {chain_id} {node}'"
    # sign_command = f"{settings.REGEN_CLI_COMMAND} bash -c 'echo \'{json.dumps(tx)}\' | regen tx sign /dev/stdin {chain_id} {node} {output}'"
    sign_command = f"echo '{json.dumps(tx)}' | {settings.REGEN_CLI_COMMAND} regen tx sign /dev/stdin --from {settings.REGEN_KEY_ADDRESS} {settings.REGEN_KEYRING_ARGS} {chain_id} {node} {output}"
    print(sign_command)
    signed_tx = os.popen(sign_command).read()
    # signed_tx = subprocess.run([settings.REGEN_CLI_COMMAND, 'sh', '-c', f'echo \'{json.dumps(tx)}\' | regen tx sign /dev/stdin {chain_id} {node}' ], stdout=subprocess.PIPE, text=True)
    print('\n--------\n')
    print('hello', signed_tx)
    # broadcast_command = f"echo {signed_tx} | {settings.REGEN_CLI_COMMAND} tx broadcast /dev/stdin {chain_id} {node} {output}"
    # # @TODO: make use of regen config passing REGEN_HOME
    # result = json.loads(os.system(broadcast_command))
    # print(result)
    # return result


    # os.system(f'regen tx sign {args.tx} --from $({from_addr}) --multisig $({multisig_addr}) --chain-id {args.chain_id} --sign-mode={args.sign_mode} --node={args.node}')
# os.system(f'regen tx broadcast {args.tx_ms} --chain-id {args.chain_id} --node={args.node}')

