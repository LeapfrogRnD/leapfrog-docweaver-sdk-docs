"""Health route schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    message: str = Field(..., description="Health message")
