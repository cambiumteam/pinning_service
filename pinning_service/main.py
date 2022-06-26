from fastapi import FastAPI
import sqlalchemy
import uvicorn

from .config import get_settings
from .database import database, metadata
from .routing import router

# Settings dependency.
settings = get_settings()

# Create tables.
engine = sqlalchemy.create_engine(
    settings.SQLALCHEMY_DATABASE_URI#, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)

# Create FastAPI app.
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# Add routes to app.
app.include_router(router)


# Run app.
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
