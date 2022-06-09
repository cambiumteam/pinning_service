import json

from indexer.main import decode_event_attribute, parse_register_resolver_message


def test_decode_event_attribute(register_resolver_event: str):
    """
    Test decoding of base64 encoded event attribute values.
    """
    attributes = json.loads(register_resolver_event).get("attributes")

    # The first attribute is the ID.
    assert ("id", "\"2\"") == decode_event_attribute(attributes[0])

    # The second attribute is the IRI.
    iri = "regen:13toVh63Yv2jkcb6oM4iKQmtT8hP1cprapXengVYdTybhJSUSeyd94f.rdf"
    assert ("iri", f"\"{iri}\"") == decode_event_attribute(attributes[1])


def test_parse_register_resolver_message(register_resolver_tx_message: str):
    """
    Test parsing and IRI -> Resolver ID mapping from a Tx message with EventRegisterResolver.
    """
    iri_resolver_mapping = parse_register_resolver_message(register_resolver_tx_message)
    iri = "regen:13toVh63Yv2jkcb6oM4iKQmtT8hP1cprapXengVYdTybhJSUSeyd94f.rdf"
    assert iri in iri_resolver_mapping
    assert iri_resolver_mapping[iri] == '2'
