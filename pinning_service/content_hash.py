from enum import IntEnum

from pydantic import BaseModel, root_validator


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


class ContentHashGraph(BaseModel):
    hash: bytes
    digest_algorithm: DigestAlgorithm
    canonicalization_algorithm: GraphCanonicalizationAlgorithm
    merkle_tree: GraphMerkleTree


class ContentHashRaw(BaseModel):
    hash: bytes
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

