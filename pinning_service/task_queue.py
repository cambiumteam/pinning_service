import procrastinate
from functools import lru_cache
from .regen import anchor
from .config import Settings, get_settings

from sqlalchemy import select
import sqlalchemy
from .database import database, resources
import asyncio
import base64
from datetime import datetime, timezone
import traceback


settings = get_settings()

engine = sqlalchemy.create_engine(
    # settings.DATABASE_URL#, connect_args={"check_same_thread": False}
    settings.SQLALCHEMY_DATABASE_URI,
)


@lru_cache()
def get_task_queue():
    return procrastinate.App(
        connector=procrastinate.AiopgConnector(
            host=settings.POSTGRES_SERVER, 
            user=settings.POSTGRES_USER, 
            password=settings.POSTGRES_PASSWORD, 
            database=settings.POSTGRES_DB,
        ),
    )


task_queue = get_task_queue()


@task_queue.task(queue="tasks")
async def anchor_task(base64_hash: str) -> None:
    await database.connect()
    
    try:
        txhash = anchor(base64_hash)
    except Exception:
        # @TODO: log issue
        print(Exception)
        traceback.print_exc()
        txhash = None

    query = resources.update(
        resources.c.hash == base64.b64decode(base64_hash),
        {
            "txhash": txhash,
            "anchor_attempts": resources.c.anchor_attempts + 1,
            # @TODO: add UTC timezone
            "anchored_at": datetime.now(),
        },
    )
    await database.execute(query)


# @task_queue.task(queue="tasks")
# async def anchor_batch_task(base_64_hash: str) -> None:
#     await database.connect()

#     query = select(resources.c.hash).where(resources.c.anchor_attempts == 0)
#     database.fetch_all(query)


#     # update_query = resources.update()


async def anchor_deferred(base64_hash: str):
    async with get_task_queue().open_async():
            await anchor_task.defer_async(base64_hash=base64_hash)
