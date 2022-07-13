from fastapi import FastAPI
import sqlalchemy
import uvicorn

from .config import get_settings
from .database import database, create_tables
from .routing import router
from .health import router as health_router
from .task_queue import get_task_queue

# Settings dependency.
settings = get_settings()

# Create FastAPI app.
app = FastAPI()


@app.on_event("startup")
async def database_startup():
    create_tables()
    await database.connect()


@app.on_event("startup")
async def task_queue_startup():
    async with get_task_queue().open_async() as task_queue:
        if not await task_queue.check_connection_async():
            await task_queue.schema_manager.apply_schema_async()


@app.on_event("shutdown")
async def database_shutdown():
    await database.disconnect()


# Add routes to app.
app.include_router(router)
app.include_router(health_router)


# Run app.
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
