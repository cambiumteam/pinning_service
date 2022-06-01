from functools import lru_cache

from pydantic import BaseSettings, validator, AnyHttpUrl


class Settings(BaseSettings):

    class Config:
        env_file = '.env'

    DATABASE_URL: str

    REGEN_NODE_REST_URL: AnyHttpUrl
    REGEN_NODE_TENDERMINT_RPC_URL: AnyHttpUrl
    REGEN_KEYRING_ARGS: str = None
    REGEN_CHAIN_ID: str = None
    REGEN_KEY_NAME: str = None
    REGEN_KEY_ADDRESS: str = None
    REGEN_RESOLVER_ID: int = None
    REGEN_CLI_COMMAND: str = None
    REGEN_GAS_FEES_ARGS: str = None


    GRAPH_DB_BASE_URL: AnyHttpUrl = None
    GRAPH_DB_USERNAME: str = None
    GRAPH_DB_PASSWORD: str = None
    USE_GRAPH_STORE: bool = False
    @validator("USE_GRAPH_STORE", pre=True)
    def get_use_graph_store(cls, v, values):
        return bool(
            values.get("GRAPH_DB_BASE_URL")
            and values.get("GRAPH_DB_USERNAME")
            and values.get("GRAPH_DB_PASSWORD")
        )


# Settings dependency.
@lru_cache()
def get_settings():
    return Settings()
