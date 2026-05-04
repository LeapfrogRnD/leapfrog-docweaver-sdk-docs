"""Application factory module with optional sub-app support."""

from fastapi import FastAPI

from app.api.middleware.api_key_middleware import (
    APIKeyMiddleware,
    add_api_key_middleware,
)
from app.api.middleware.cors import add_cors_middleware
from app.api.middleware.csrf import add_csrf_middleware
from app.api.middleware.error_handler import register_exception_handlers
from app.api.middleware.rate_limit import add_rate_limit_middleware
from app.api.middleware.security_headers import add_security_headers_middleware
from app.api.routes.router import main_router
from app.lifetime import lifespan


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="Leap DocWeaver API",
        description="OCR and document processing API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # middleware
    add_cors_middleware(application)
    add_csrf_middleware(application)
    add_rate_limit_middleware(application)

    add_api_key_middleware(application)
    add_security_headers_middleware(application)
    register_exception_handlers(application)

    application.include_router(main_router)

    return application
