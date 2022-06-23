import pytest

from pinning_service.iri import to_iri, parse_iri
from pinning_service.content_hash import ContentHash


def test_to_iri(test_graph_content_hash: (ContentHash, str), test_raw_content_hash: (ContentHash, str)):

    # Test graph content hash.
    content_hash, iri = test_graph_content_hash
    parsed_iri = to_iri(content_hash)
    assert parsed_iri == iri

    # Test raw content hash.
    content_hash, iri = test_raw_content_hash
    with pytest.raises(ValueError, match="Only graph content hash is supported."):
        to_iri(content_hash)


def test_parse_iri(test_graph_content_hash: (ContentHash, str), test_raw_content_hash: (ContentHash, str)):

    # Test valid graph content hash.
    content_hash, iri = test_graph_content_hash
    parsed_content_hash = parse_iri(iri)
    assert parsed_content_hash == content_hash

    # Test raw data.
    content_hash, iri = test_raw_content_hash
    with pytest.raises(ValueError, match="Only graph content hash is supported."):
        parse_iri(iri)

    # Test invalid prefix.
    with pytest.raises(ValueError, match="Invalid IRI prefix."):
        parse_iri("cosmos:13toVgf5aZqSVSeJQv562xkkeoe3rr3bJWa29PHVKVf77VAkVMcDvVd.rdf")

    # Test invalid extension.
    with pytest.raises(ValueError, match="Invalid IRI extension."):
        parse_iri("regen:13toVgf5aZqSVSeJQv562xkkeoe3rr3bJWa29PHVKVf77VAkVMcDvVd")

    # Test invalid checksum, invalid hash.
    with pytest.raises(ValueError, match="Invalid IRI hash."):
        parse_iri("regen:23toVgf5aZqSVSeJQv562xkkeoe3rr3bJWa29PHVKVf77VAkVMcDvVd.rdf")

    # Test invalid version.
    with pytest.raises(ValueError, match="Invalid IRI version."):
        parse_iri("regen:esV713VcRqk5TWxDgKQjGSpN4aXL4a9XTzbWRduCMQDqq2zo3TtX.rdf")
