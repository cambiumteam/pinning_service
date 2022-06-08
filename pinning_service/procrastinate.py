import procrastinate
from functools import lru_cache
from .regen import anchor
from .config import Settings, get_settings

# from sqlalchemy import select
# from .database import database, resources


settings = get_settings()

# engine = sqlalchemy.create_engine(
#     settings.DATABASE_URL#, connect_args={"check_same_thread": False}
# )

@lru_cache()
def get_pc_app():
    return procrastinate.App(
        connector=procrastinate.AiopgConnector(
            host="localhost",
            user="postgres",
            password="postgres"
        ),
    )

pc_app = get_pc_app()

@pc_app.task(queue="tasks")
def anchor_task(base64_hash: str):

    # @TODO: error handling, running inside worker
    txhash = anchor(base64_hash)
    print(txhash)
    # @TODO: update db resource entry with txhash

# export PYTHONPATH=.
# procrastinate --app=pinning_service.procrastinate.pc_app schema --apply
# procrastinate --app=pinning_service.procrastinate.pc_app healthchecks
# procrastinate --app=pinning_service.procrastinate.pc_app worker
