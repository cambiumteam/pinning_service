import base64
import binascii
from enum import IntEnum

from pydantic import BaseModel, root_validator, validator


class DigestAlgorithm(IntEnum):
    UNSPECIFIED = 0
    BLAKE2B_256 = 1


class GraphCanonicalizationAlgorithm(IntEnum):
    UNSPECIFIED = 0
    URDNA2015 = 1


class GraphMerkleTree(IntEnum):
    NONE_UNSPECIFIED = 0


class RawMediaType(IntEnum):
    UNSPECIFIED = 0
    TEXT_PLAIN = 1
    JSON = 2
    CSV = 3
    XML = 4
    PDF = 5
    TIFF = 16
    JPG = 17
    PNG = 18
    SVG = 19
    WEBP = 20
    AVIF = 21
    GIF = 22
    APNG = 23
    MPEG = 32
    MP4 = 33
    WEBM = 34
    OGG = 35


# Helper function to check if a string is base64.
# This isn't perfect but will catch invalid characters and string lengths.
def is_base64(hash: str) -> bool:
    try:
        base64.b64decode(hash)
        return True
    except binascii.Error:
        return False


# Pydantic validator function for content hash classes.
# The hash in content hash objects should be the base64 encoded string of
# data. This makes it easier to dump the content hash objects to json. If
# a content hash object is instantiated with bytes the base64 encoded
# string of the bytes will be stored instead.
def hash_bytes_validator(hash) -> str:
    if type(hash) == bytes:
        return base64.b64encode(hash).decode()
    if not is_base64(hash):
        raise ValueError("Hash must be the base64 encoded string.")
    return hash


class ContentHashGraph(BaseModel):
    hash: str
    _validate_bytes = validator('hash', allow_reuse=True, pre=True)(hash_bytes_validator)
    digest_algorithm: DigestAlgorithm
    canonicalization_algorithm: GraphCanonicalizationAlgorithm
    merkle_tree: GraphMerkleTree


class ContentHashRaw(BaseModel):
    hash: str
    _validate_bytes = validator('hash', allow_reuse=True, pre=True)(hash_bytes_validator)
    digest_algorithm: DigestAlgorithm
    media_type: RawMediaType


class ContentHash(BaseModel):
    raw: ContentHashRaw = None
    graph: ContentHashGraph = None

    @root_validator()
    def check_raw_or_graph(cls, values):
        if (values.get('raw') is None) and (values.get("graph") is None):
            raise ValueError('Raw or graph content hash is required.')
        return values
