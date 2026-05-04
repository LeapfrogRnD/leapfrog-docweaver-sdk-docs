"""Health check routes."""

from fastapi import APIRouter, Depends

from app.api.dependencies.config import get_config
from app.api.routes.health.schemas import HealthResponse
from app.config.settings import Settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_config)):
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service=f"OCR API is running in {settings.mode} mode.",
        message="All systems operational",
    )
