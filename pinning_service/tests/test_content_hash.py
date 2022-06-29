import pytest

from pydantic import ValidationError

from pinning_service.content_hash import ContentHash, ContentHashRaw, DigestAlgorithm, RawMediaType


def test_empty_content_hash():

    # Test that a content hash cannot be empty.
    with pytest.raises(ValidationError, match="Raw or graph content hash is required."):
        ContentHash(raw=None, graph=None)


def test_content_hash_hash():

    # Test that bytes are correctly saved in the base64 encoding.
    hash_bytes = b'abc'
    encoded_hash = "YWJj"
    raw = ContentHashRaw(hash=hash_bytes, digest_algorithm=DigestAlgorithm.UNSPECIFIED, media_type=RawMediaType.UNSPECIFIED)
    assert raw.hash == encoded_hash

    # Test that the correct encoded hash is kept.
    raw = ContentHashRaw(hash=encoded_hash, digest_algorithm=DigestAlgorithm.UNSPECIFIED, media_type=RawMediaType.UNSPECIFIED)
    assert raw.hash == encoded_hash

    # Test a hash string that is not long enough.
    with pytest.raises(ValidationError, match="Hash must be the base64 encoded string."):
        ContentHashRaw(hash="123", digest_algorithm=DigestAlgorithm.UNSPECIFIED, media_type=RawMediaType.UNSPECIFIED)

    # Test a hash string with an invalid character.
    with pytest.raises(ValidationError, match="Hash must be the base64 encoded string."):
        ContentHashRaw(hash="123?", digest_algorithm=DigestAlgorithm.UNSPECIFIED, media_type=RawMediaType.UNSPECIFIED)
