from datetime import datetime

from rdflib import URIRef, Literal, Dataset, BNode
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql

from config import Settings

# handle RDF BNodes
# see https://github.com/RDFLib/rdflib/blob/d3689cf8a9912a352d16570cc5adf74eb391c268/rdflib/plugins/stores/sparqlstore.py#L66
def bnode_ext(node):
    if isinstance(node, BNode):
        return '<bnode:b%s>' % node
    return _node_to_sparql(node)


# Create a sparql store.
# TODO: Determine if we can make the sparql store a dependency and reuse across requests.
def create_sparql_store(settings: Settings):
    return SPARQLUpdateStore(
        query_endpoint=f"{settings.GRAPH_DB_BASE_URL}/query",
        update_endpoint=f"{settings.GRAPH_DB_BASE_URL}/update",
        auth=(settings.GRAPH_DB_USERNAME, settings.GRAPH_DB_PASSWORD),
        node_to_sparql=bnode_ext
    )


def add_graph_to_store(iri, serialized_graph, settings: Settings, format='application/n-quads'):
    store = create_sparql_store(settings)
    ds = Dataset(store=store)
    # add named graph to dataset
    g = ds.add_graph(URIRef(f'{settings.GRAPH_DB_BASE_URL}/data/{iri}'))
    g.parse(data=serialized_graph, format=format)
    # add triple to default graph manifest
    ds.add((
        URIRef(f'{settings.GRAPH_DB_BASE_URL}/data/{iri}'),
        URIRef('http://purl.org/dc/elements/1.1/date'),
        Literal(datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")),
    ))