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


# Settings dependency.
@lru_cache()
def get_settings():
    return Settings()
