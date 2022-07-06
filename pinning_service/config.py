from functools import lru_cache

from pydantic import BaseSettings, validator, AnyHttpUrl, PostgresDsn


class Settings(BaseSettings):

    class Config:
        env_file = '.env'

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    # SQLALCHEMY_POOL_SIZE: int = 10
    # SQLALCHEMY_MAX_OVERFLOW: int = 15
    SQLALCHEMY_DATABASE_URI: PostgresDsn = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v, values):
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )


    REGEN_NODE_REST_URL: AnyHttpUrl
    REGEN_NODE_TENDERMINT_RPC_URL: AnyHttpUrl
    REGEN_KEYRING_ARGS: str = None
    REGEN_CHAIN_ID: str = None
    REGEN_KEY_ADDRESS: str = None
    REGEN_SERVICE_KEY_ADDRESS: str = None
    REGEN_RESOLVER_ID: int = None
    REGEN_CLI_COMMAND: str = None
    REGEN_GAS_PRICES_AMOUNT: float = None
    REGEN_GAS_PRICES_DENOM: str = None


# Settings dependency.
@lru_cache()
def get_settings():
    return Settings()
