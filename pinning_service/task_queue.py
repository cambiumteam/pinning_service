import procrastinate
from functools import lru_cache
from datetime import datetime
import traceback

import sqlalchemy
from sqlalchemy import select

from .config import get_settings
from .database import database, resources
from .regen import anchor

settings = get_settings()

engine = sqlalchemy.create_engine(
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
async def anchor_batch_task() -> None:
    await database.connect()

    query = select([resources.c.hash]).where(resources.c.anchor_attempts == 0).limit(10)
    records = await database.fetch_all(query)

    if len(records) == 0:
        print("All resources have been processed")
        return

    hashes = [record.hash for record in records]
    b64_hashes = [b64encode(h).decode("utf-8") for h in hashes]
    print(f"Batch anchoring {b64_hashes}")

    try:
        txhash = anchor(b64_hashes)
    except Exception:
        # @TODO: log issue
        traceback.print_exc()
        txhash = None

    update_query = resources.update(
        resources.c.hash.in_(hashes),
        {
            "txhash": txhash,
            "anchor_attempts": resources.c.anchor_attempts + 1,
            # @TODO: add UTC timezone
            "anchored_at": datetime.now(),
        },
    )
    await database.execute(update_query)


async def anchor_batch_deferred():
    async with get_task_queue().open_async():
        await anchor_batch_task.defer_async()
