from os import environ

# Set the TESTING environ before importing the app.
environ['TESTING'] = 'True'

import pytest
from sqlalchemy_utils import create_database, drop_database
from fastapi.testclient import TestClient

from pinning_service.content_hash import ContentHash, ContentHashGraph, ContentHashRaw, DigestAlgorithm, GraphCanonicalizationAlgorithm, GraphMerkleTree, RawMediaType
from pinning_service.config import get_settings
from pinning_service.main import app


settings = get_settings()


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    url = settings.SQLALCHEMY_DATABASE_URI
    assert "test_" in url
    create_database(url)
    yield
    drop_database(url)


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


# Use same content hash from regen ledger source.
# https://github.com/regen-network/regen-ledger/blob/d7c114cd115f2231220a0083a32f17fdfed9508c/x/data/iri_test.go#L11
@pytest.fixture(scope="package")
def test_graph_content_hash() -> (ContentHash, str):
    content_hash_graph = ContentHashGraph(
        hash=b'abcdefghijklmnopqrstuvwxyz123456',
        digest_algorithm=DigestAlgorithm.BLAKE2B_256,
        canonicalization_algorithm=GraphCanonicalizationAlgorithm.URDNA2015,
        merkle_tree=GraphMerkleTree.NONE_UNSPECIFIED,
    )
    return ContentHash(graph=content_hash_graph), "regen:13toVgf5aZqSVSeJQv562xkkeoe3rr3bJWa29PHVKVf77VAkVMcDvVd.rdf"


@pytest.fixture(scope="package")
def test_raw_content_hash() -> (ContentHash, str):
    content_hash_raw = ContentHashRaw(
        hash=b'abcdefghijklmnopqrstuvwxyz123456',
        digest_algorithm=DigestAlgorithm.BLAKE2B_256,
        media_type=RawMediaType.UNSPECIFIED,
    )
    return ContentHash(raw=content_hash_raw), "regen:113gdjFKcVCt13Za6vN7TtbgMM6LMSjRnu89BMCxeuHdkJ1hWUmy.binA"


@pytest.fixture(scope="package")
def test_jsonld_document() -> (str, str):
    iri = "regen:13toVhbrVAb7VsP63rXcunZRrgefrBSx2x28yRH2gsEzcNdEo9MxuoN.rdf"
    raw = """
    {
      "@context": {
        "dc11": "http://purl.org/dc/elements/1.1/",
        "ex": "http://example.org/vocab#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "ex:contains": {
          "@type": "@id"
        }
      },
      "@graph": [
        {
          "@id": "http://example.org/library",
          "@type": "ex:Library",
          "ex:contains": "http://example.org/library/the-republic"
        },
        {
          "@id": "http://example.org/library/the-republic",
          "@type": "ex:Book",
          "ex:contains": "http://example.org/library/the-republic#introduction",
          "dc11:creator": "Plato",
          "dc11:title": "The Republic"
        },
        {
          "@id": "http://example.org/library/the-republic#introduction",
          "@type": "ex:Chapter",
          "dc11:description": "An introductory chapter on The Republic.",
          "dc11:title": "The Introduction"
        }
      ]
    }
    """
    return raw, iri