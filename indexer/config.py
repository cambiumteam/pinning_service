from functools import lru_cache

from pydantic import BaseSettings, AnyUrl, AnyHttpUrl


class AnyWsUrl(AnyUrl):
    allowed_schemes = ['ws']


class Settings(BaseSettings):

    class Config:
        env_file = '.env'

    REGEN_NODE_REST_URL: AnyHttpUrl
    REGEN_NODE_TENDERMINT_WS_URL: AnyWsUrl

    REGEN_RESOLVER_ID: int

    GRAPH_DB_BASE_URL: AnyHttpUrl
    GRAPH_DB_USERNAME: str
    GRAPH_DB_PASSWORD: str
    USE_GRAPH_STORE: bool


# Settings dependency.
@lru_cache()
def get_settings():
    return Settings()
