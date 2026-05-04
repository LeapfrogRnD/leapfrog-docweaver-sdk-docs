"""Main entry point for the document processor worker."""

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from config.settings import settings
from core.worker import Worker
from db.session import close_db, init_db
from fastapi import FastAPI
from utils.logger import log
from utils.metrics import ResourceMonitor

# Global worker instance
worker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    global worker

    log.info(f"Starting {settings.APP_NAME} - Environment: {settings.ENVIRONMENT}")

    def _mask(val):
        if not val:
            return "<not set>"
        s = str(val)
        if len(s) <= 8:
            return s
        return f"{s[:4]}...{s[-4:]}"

    try:
        azure_endpoint = getattr(settings, "AZURE_OCR_ENDPOINT", None) or "<not set>"
        azure_key = _mask(getattr(settings, "AZURE_OCR_API_KEY", None))
        openai_key = _mask(getattr(settings, "OPENAI_API_KEY", None))
        langfuse_secret = _mask(getattr(settings, "LANGFUSE_SECRET_KEY", None))
        langfuse_public = _mask(getattr(settings, "LANGFUSE_PUBLIC_KEY", None))
        langfuse_base = getattr(settings, "LANGFUSE_BASE_URL", None) or "<not set>"

        log.info(f"Startup config: AZURE_OCR_ENDPOINT={azure_endpoint}")
        log.info(f"Startup config: AZURE_OCR_API_KEY={azure_key}")
        log.info(f"Startup config: OPENAI_API_KEY={openai_key}")
        log.info(f"Startup config: LANGFUSE_SECRET_KEY={langfuse_secret}")
        log.info(f"Startup config: LANGFUSE_PUBLIC_KEY={langfuse_public}")
        log.info(f"Startup config: LANGFUSE_BASE_URL={langfuse_base}")
    except Exception:
        log.exception("Failed to read startup config values")

    await init_db()

    worker = Worker()
    worker_task = asyncio.create_task(worker.start())

    ResourceMonitor.log_metrics()

    yield

    log.info("Shutting down worker...")
    await worker.shutdown()

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

    # Close database
    await close_db()
    log.info("Shutdown complete")


# Create FastAPI app for health checks
app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint for ECS."""
    global worker

    if worker:
        return await worker.health_check()

    return {"status": "starting", "worker_id": settings.WORKER_ID}


@app.get("/metrics")
async def metrics():
    """Expose resource metrics for monitoring."""
    return ResourceMonitor.get_all_metrics()


async def main():
    """Main entry point."""
    # Run FastAPI with uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=settings.HEALTH_CHECK_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
