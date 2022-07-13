import procrastinate
from functools import lru_cache
import traceback

import sqlalchemy
from sqlalchemy import select

from .config import get_settings
from .database import database, resources, update_iris_txhash
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

    # Fetch resources that have no anchor attempts.
    query = select([resources.c.iri]).where(resources.c.txhash == None).limit(10)
    records = await database.fetch_all(query)

    if len(records) == 0:
        print("All resources have been processed")
        return

    # Collect IRIs and anchor.
    iris = [record.iri for record in records]
    try:
        txhash = anchor(iris)
    except Exception:
        # @TODO: log issue
        traceback.print_exc()
        txhash = None

    # @TODO: add UTC timezone
    await update_iris_txhash(iris, txhash)


async def anchor_batch_deferred():
    async with get_task_queue().open_async():
        await anchor_batch_task.defer_async()


async def get_task_list(**kwargs):
    app = await get_task_queue().open_async()
    return await app.job_manager.list_jobs_async(**kwargs)
