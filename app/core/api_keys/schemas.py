"""API key schemas."""

from datetime import datetime

from pydantic import Field, HttpUrl

from app.core.common.schema import OrmResponseModel, RequestModel


class ApiKeyCreateRequest(RequestModel):
    """API key creation request schema."""

    secret_name: str = Field(..., description="Name/identifier for the API key")
    webhook_url: HttpUrl | None = Field(
        None,
        description="Optional webhook URL for API key events",
    )


class ApiKeyUpdateRequest(ApiKeyCreateRequest):
    """API key update request schema."""


class ApiKeyResponse(OrmResponseModel):
    """API key response schema."""

    id: int = Field(..., description="API key ID")
    secret_name: str = Field(..., description="Name/identifier for the API key")
    webhook_url: str | None = Field(
        None,
        description="Optional webhook URL for API key events",
    )
    is_active: bool = Field(..., description="Whether the API key is active")


class ApiKeyListResponse(OrmResponseModel):
    """API key list response schema (without secret_value)."""

    id: int = Field(..., description="API key ID")
    secret_name: str = Field(..., description="Name/identifier for the API key")
    secret_value: str | None = Field(None, description="The API key value")
    webhook_url: str | None = Field(
        None,
        description="Optional webhook URL for API key events",
    )
    created_by: int = Field(..., description="ID of the user who created the API key")
    is_active: bool = Field(..., description="Whether the API key is active")
    last_used_at: datetime | None = Field(None, description="Last time the API key was used")
    created_at: datetime = Field(..., description="API key creation timestamp")
