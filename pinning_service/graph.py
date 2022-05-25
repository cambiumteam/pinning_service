from datetime import datetime

from rdflib import URIRef, Literal, Dataset


def add_graph_to_store(iri, serialized_graph, store, base_url, format='application/n-quads'):
    ds = Dataset(store=store)
    # add named graph to dataset
    g = ds.add_graph(URIRef(f'{base_url}/data/{iri}'))
    g.parse(data=serialized_graph, format=format)
    # add triple to default graph manifest
    ds.add((
        URIRef(f'{base_url}/data/{iri}'),
        URIRef('http://purl.org/dc/elements/1.1/date'),
        Literal(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
    ))