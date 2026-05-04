"""Shared API schemas."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed error information for field-level errors."""

    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standardized error response format."""

    path: str | None = Field(None, description="Request path that caused the error")
    status_code: int = Field(..., description="HTTP status code")
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    detail: str | None = Field(None, description="Additional error details")
