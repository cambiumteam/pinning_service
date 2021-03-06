# Pinning Service

A combination pinning service, resolver and indexer for the [data module](https://docs.regen.network/modules/data/) on [Regen Ledger](https://github.com/regen-network/regen-ledger).

*Note: This project is under active development!*

## Features

This application provides services to add supporting data for credit classes, projects, and credit batches that are created and managed using the ecocredit module on Regen Ledger.

For more information see the [Data module](https://docs.regen.network/modules/data/) and [Concepts](https://docs.regen.network/modules/data/01_concepts.html) documentation.

### Pinning service

The pinning service facilitates the processing and anchoring RDF graph data on-chain:

- A JSON-LD document is sent to the pinning service where it is canonicalized and procssed into a [Content Hash](https://docs.regen.network/modules/data/01_concepts.html#content-hash).
- The content hash is [anchored](https://docs.regen.network/modules/data/01_concepts.html#anchor) on-chain to provide "secure timestamping".
- An [IRI](https://docs.regen.network/modules/data/01_concepts.html#iri) is generated to uniquely identify the data.
- The anchored data is registered with the resolver. The original canonicalized data is stored in the pinning service database for later retrieval.

### Resolver

A [resolver](https://docs.regen.network/modules/data/01_concepts.html#resolver) is used to retrieve data that has been stored off chain and anchored on chain. The pinning service can be used to retrieve the data it has anchored on-chain. Graph data that is provided by the resolver can be requested in multiple serialization formats.

### Indexer

Graph data that is anchored on-chain can optionally be indexed into an [Apache Jena](https://jena.apache.org/) graph database for more efficient retrieval and querying of data.

## Development


### Localnet

The `Makefile` includes commands to start and configure a localnet for testing locally:

`make localnet-start`: Start an existing or init a new localnet.
`make localnet-configure`: Configure the localnet with keys and manager -> service account grants.
`make localnet-stop`: Stop the localnet.
`make localnet-clean`: Destroy the localnet, keys and data.
`make -C localnet register-resolver`: Register data to the resolver using the service account. Can be used for testing.