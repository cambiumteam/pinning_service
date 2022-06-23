import pytest

from pinning_service.content_hash import ContentHash, ContentHashGraph, ContentHashRaw, DigestAlgorithm, GraphCanonicalizationAlgorithm, GraphMerkleTree, RawMediaType


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