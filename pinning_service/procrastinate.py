import procrastinate
from functools import lru_cache
from .regen import anchor
from .config import Settings, get_settings

from sqlalchemy import select
import sqlalchemy
from .database import database, resources
import asyncio
import base64


settings = get_settings()

engine = sqlalchemy.create_engine(
    # settings.DATABASE_URL#, connect_args={"check_same_thread": False}
    settings.SQLALCHEMY_DATABASE_URI,
)


@lru_cache()
def get_pc_app():
    return procrastinate.App(
        connector=procrastinate.AiopgConnector(
            host="localhost", user="postgres", password="postgres"
        ),
    )


pc_app = get_pc_app()


@pc_app.task(queue="tasks")
async def anchor_task(base64_hash: str):
    await database.connect()

    try:
        txhash = anchor(base64_hash)
    except Exception:
        # @TODO: log issue
        print(Exception)
        txhash = None

    query = resources.update(
        resources.c.hash == base64.b64decode(base64_hash),
        {
            "txhash": txhash,
            "anchor_attempts": resources.c.anchor_attempts + 1,
        },
    )
    await database.execute(query)


# export PYTHONPATH=.
# procrastinate --app=pinning_service.procrastinate.pc_app schema --apply
# procrastinate --app=pinning_service.procrastinate.pc_app healthchecks
# procrastinate --app=pinning_service.procrastinate.pc_app worker


# async def anchor_deferred(b64_hash: str):
#     print('hello')
#     async with get_pc_app().open_async():
#             await anchor_task.defer_async(base64_hash=base64_hash.decode("utf-8"))
