from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import Settings
from app.db.database import DatabaseManager
from app.logger import logger
from app.providers.queues.factory import QueueProviderFactory
from app.providers.storage.factory import StorageProviderFactory


async def startup_event(app: FastAPI):
    settings = Settings.initialize()
    app.state.config = settings

    db_manager = DatabaseManager()
    await db_manager.initialize(settings)
    app.state.db_manager = db_manager
    logger.info("Database manager initialized")

    app.state.queue_provider = QueueProviderFactory.create(settings)

    app.state.storage_provider = StorageProviderFactory.create(settings=settings)


async def shutdown_event(app: FastAPI):
    if hasattr(app.state, "db_manager"):
        await app.state.db_manager.close()
        logger.info("Database manager closed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event(app)
    yield
    await shutdown_event(app)
