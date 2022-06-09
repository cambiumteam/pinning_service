import pytest


@pytest.fixture(scope="package")
def register_resolver_event() -> str:
    return '''
    {
        "type": "regen.data.v1.EventRegisterResolver",
        "attributes": [
          {
            "key": "aWQ=",
            "value": "IjIi",
            "index": true
          },
          {
            "key": "aXJp",
            "value": "InJlZ2VuOjEzdG9WaDYzWXYyamtjYjZvTTRpS1FtdFQ4aFAxY3ByYXBYZW5nVllkVHliaEpTVVNleWQ5NGYucmRmIg==",
            "index": true
          }
        ]
      }
    '''


@pytest.fixture(scope="package")
def register_resolver_tx_message() -> str:
    return r'''
    {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "query": "tm.event='Tx' AND regen.data.v1.EventRegisterResolver.id = 2",
        "data": {
          "type": "tendermint/event/Tx",
          "value": {
            "TxResult": {
              "height": "4540",
              "tx": "CoMBCoABCiIvcmVnZW4uZGF0YS52MS5Nc2dSZWdpc3RlclJlc29sdmVyEloKLHJlZ2VuMWNwemV5OXg5NnJydnU3OWVtd2s0YXdyc3kwcmY5Mmw3YTNsdTM4EAIaKBImCiCaEgqpLvdnMSB5N/KnXoV11Rios+eMJsBDlg/S6hnlrhABGAESZApQCkYKHy9jb3Ntb3MuY3J5cHRvLnNlY3AyNTZrMS5QdWJLZXkSIwohArVUlpw9x1iJIpggUk7ifgq2w5e1Qub1LBYwsfKsNKnQEgQKAggBGHYSEAoKCgVzdGFrZRIBMhDAmgwaQBgOGbkX/fd0dhqE9kcML/5VbOG0yqwu+nHHOGrnfnONYwS/OpuM7UPyzwwHuuZ/q7EAPx1npLsXZ851jC0fe3A=",
              "result": {
                "data": "CiQKIi9yZWdlbi5kYXRhLnYxLk1zZ1JlZ2lzdGVyUmVzb2x2ZXI=",
                "log": "[{\"events\":[{\"type\":\"message\",\"attributes\":[{\"key\":\"action\",\"value\":\"/regen.data.v1.MsgRegisterResolver\"}]},{\"type\":\"regen.data.v1.EventRegisterResolver\",\"attributes\":[{\"key\":\"id\",\"value\":\"\\\"2\\\"\"},{\"key\":\"iri\",\"value\":\"\\\"regen:13toVh63Yv2jkcb6oM4iKQmtT8hP1cprapXengVYdTybhJSUSeyd94f.rdf\\\"\"}]}]}]",
                "gas_wanted": "200000",
                "gas_used": "59963",
                "events": [
                  {
                    "type": "coin_spent",
                    "attributes": [
                      {
                        "key": "c3BlbmRlcg==",
                        "value": "cmVnZW4xY3B6ZXk5eDk2cnJ2dTc5ZW13azRhd3JzeTByZjkybDdhM2x1Mzg=",
                        "index": true
                      },
                      {
                        "key": "YW1vdW50",
                        "value": "MnN0YWtl",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "coin_received",
                    "attributes": [
                      {
                        "key": "cmVjZWl2ZXI=",
                        "value": "cmVnZW4xN3hwZnZha20yYW1nOTYyeWxzNmY4NHoza2VsbDhjNWwwbWd1YWU=",
                        "index": true
                      },
                      {
                        "key": "YW1vdW50",
                        "value": "MnN0YWtl",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "transfer",
                    "attributes": [
                      {
                        "key": "cmVjaXBpZW50",
                        "value": "cmVnZW4xN3hwZnZha20yYW1nOTYyeWxzNmY4NHoza2VsbDhjNWwwbWd1YWU=",
                        "index": true
                      },
                      {
                        "key": "c2VuZGVy",
                        "value": "cmVnZW4xY3B6ZXk5eDk2cnJ2dTc5ZW13azRhd3JzeTByZjkybDdhM2x1Mzg=",
                        "index": true
                      },
                      {
                        "key": "YW1vdW50",
                        "value": "MnN0YWtl",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "message",
                    "attributes": [
                      {
                        "key": "c2VuZGVy",
                        "value": "cmVnZW4xY3B6ZXk5eDk2cnJ2dTc5ZW13azRhd3JzeTByZjkybDdhM2x1Mzg=",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "tx",
                    "attributes": [
                      {
                        "key": "ZmVl",
                        "value": "MnN0YWtl",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "tx",
                    "attributes": [
                      {
                        "key": "YWNjX3NlcQ==",
                        "value": "cmVnZW4xY3B6ZXk5eDk2cnJ2dTc5ZW13azRhd3JzeTByZjkybDdhM2x1MzgvMTE4",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "tx",
                    "attributes": [
                      {
                        "key": "c2lnbmF0dXJl",
                        "value": "R0E0WnVSZjk5M1IyR29UMlJ3d3YvbFZzNGJUS3JDNzZjY2M0YXVkK2M0MWpCTDg2bTR6dFEvTFBEQWU2NW4rcnNRQS9IV2VrdXhkbnpuV01MUjk3Y0E9PQ==",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "message",
                    "attributes": [
                      {
                        "key": "YWN0aW9u",
                        "value": "L3JlZ2VuLmRhdGEudjEuTXNnUmVnaXN0ZXJSZXNvbHZlcg==",
                        "index": true
                      }
                    ]
                  },
                  {
                    "type": "regen.data.v1.EventRegisterResolver",
                    "attributes": [
                      {
                        "key": "aWQ=",
                        "value": "IjIi",
                        "index": true
                      },
                      {
                        "key": "aXJp",
                        "value": "InJlZ2VuOjEzdG9WaDYzWXYyamtjYjZvTTRpS1FtdFQ4aFAxY3ByYXBYZW5nVllkVHliaEpTVVNleWQ5NGYucmRmIg==",
                        "index": true
                      }
                    ]
                  }
                ]
              }
            }
          }
        },
        "events": {
          "tx.signature": [
            "GA4ZuRf993R2GoT2Rwwv/lVs4bTKrC76ccc4aud+c41jBL86m4ztQ/LPDAe65n+rsQA/HWekuxdnznWMLR97cA=="
          ],
          "coin_received.receiver": [
            "regen17xpfvakm2amg962yls6f84z3kell8c5l0mguae"
          ],
          "coin_received.amount": [
            "2stake"
          ],
          "transfer.amount": [
            "2stake"
          ],
          "message.sender": [
            "regen1cpzey9x96rrvu79emwk4awrsy0rf92l7a3lu38"
          ],
          "tx.acc_seq": [
            "regen1cpzey9x96rrvu79emwk4awrsy0rf92l7a3lu38/118"
          ],
          "regen.data.v1.EventRegisterResolver.id": [
            "\"2\""
          ],
          "tm.event": [
            "Tx"
          ],
          "transfer.recipient": [
            "regen17xpfvakm2amg962yls6f84z3kell8c5l0mguae"
          ],
          "transfer.sender": [
            "regen1cpzey9x96rrvu79emwk4awrsy0rf92l7a3lu38"
          ],
          "tx.height": [
            "4540"
          ],
          "coin_spent.amount": [
            "2stake"
          ],
          "tx.hash": [
            "D5C9DD633A3A7F67803954D25F7FE2B9E973B5F4EEF5921DE39BA266939B4E7E"
          ],
          "message.action": [
            "/regen.data.v1.MsgRegisterResolver"
          ],
          "regen.data.v1.EventRegisterResolver.iri": [
            "\"regen:13toVh63Yv2jkcb6oM4iKQmtT8hP1cprapXengVYdTybhJSUSeyd94f.rdf\""
          ],
          "coin_spent.spender": [
            "regen1cpzey9x96rrvu79emwk4awrsy0rf92l7a3lu38"
          ],
          "tx.fee": [
            "2stake"
          ]
        }
      }
    }
    '''