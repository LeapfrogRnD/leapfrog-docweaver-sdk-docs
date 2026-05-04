"""API key API routes."""

from fastapi import APIRouter, Depends, Path

from app.api.dependencies.auth import get_current_user
from app.api.routes.api_keys.dependencies import ApiKeyServiceDep
from app.core.api_keys.schemas import (
    ApiKeyCreateRequest,
    ApiKeyListResponse,
    ApiKeyResponse,
    ApiKeyUpdateRequest,
)
from app.core.common.schema import GenericListResponse, GenericResponse, PaginationParams
from app.core.integration_apis.schemas import IntegrationListResponse, IntegrationStatsResponse
from app.db.models import User

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("/", response_model=GenericResponse[ApiKeyResponse])
async def create_api_key(
    request: ApiKeyCreateRequest,
    api_key_service: ApiKeyServiceDep,
    user: User = Depends(get_current_user),
):
    """Generate a new API key."""
    api_key = await api_key_service.create_api_key(request, user)
    return GenericResponse[ApiKeyResponse](
        data=api_key,
    )


@router.put("/{api_key_id}", response_model=GenericResponse[ApiKeyResponse])
async def update_api_key(
    request: ApiKeyUpdateRequest,
    api_key_id: int,
    api_key_service: ApiKeyServiceDep,
    user: User = Depends(get_current_user),
):
    """Update a new API key."""
    api_key = await api_key_service.update_api_key(request, api_key_id, user)
    return GenericResponse[ApiKeyResponse](
        data=api_key,
    )


@router.get("/{api_key_id}", response_model=GenericResponse[ApiKeyResponse])
async def get_api_key(
    api_key_id: int,
    api_key_service: ApiKeyServiceDep,
    user: User = Depends(get_current_user),
):
    """Update a new API key."""
    api_key = await api_key_service.get_api_key(api_key_id, user)
    return GenericResponse[ApiKeyResponse](
        data=api_key,
    )


@router.get("/", response_model=GenericListResponse[ApiKeyListResponse])
async def get_api_keys(
    api_key_service: ApiKeyServiceDep,
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
):
    """Get all API keys"""
    api_keys, metadata = await api_key_service.get_all_api_keys(pagination, user)
    return GenericListResponse[ApiKeyListResponse](data=api_keys, metadata=metadata)


@router.delete("/{api_key_id}", response_model=GenericResponse[str])
async def delete_api_key(
    api_key_service: ApiKeyServiceDep,
    api_key_id: int = Path(..., description="ID of the API key to delete"),
    user: User = Depends(get_current_user),
):
    """Delete an API key."""
    await api_key_service.delete_api_key(api_key_id, user)
    return GenericResponse[str](data="API key deleted successfully")


@router.post("/{api_key_id}/regenerate-secret", response_model=GenericResponse[str])
async def regenerate_api_key_secret(
    api_key_service: ApiKeyServiceDep,
    api_key_id: int = Path(..., description="ID of the API key to regenerate secret for"),
    user: User = Depends(get_current_user),
):
    """Regenerate API key secret."""
    await api_key_service.regenerate_api_key_secret(api_key_id, user)
    return GenericResponse[str](data="API key secret regenerated successfully")


@router.patch("/{api_key_id}/toggle-status", response_model=GenericResponse[ApiKeyResponse])
async def toggle_api_key_status(
    api_key_service: ApiKeyServiceDep,
    api_key_id: int = Path(..., description="ID of the API key to toggle status"),
    user: User = Depends(get_current_user),
):
    """Toggle the active/inactive status of an API key."""
    api_key = await api_key_service.toggle_api_key_status(api_key_id, user)
    return GenericResponse[ApiKeyResponse](data=api_key)


@router.get(
    "/{api_key_id}/integrations", response_model=GenericListResponse[IntegrationListResponse]
)
async def get_integrations(
    api_key_service: ApiKeyServiceDep,
    api_key_id: int,
    pagination: PaginationParams = Depends(),
    _: User = Depends(get_current_user),
):
    """Delete an API key."""
    data, metadata = await api_key_service.get_all_integrations(api_key_id, pagination)
    return GenericListResponse[IntegrationListResponse](data=data, metadata=metadata)


@router.get(
    "/{api_key_id}/integrations/stats", response_model=GenericResponse[IntegrationStatsResponse]
)
async def get_integrations_stats(
    api_key_service: ApiKeyServiceDep,
    api_key_id: int,
    _: User = Depends(get_current_user),
):
    """Delete an API key."""
    data = await api_key_service.get_integration_stats(api_key_id)
    return GenericResponse[IntegrationStatsResponse](data=data)
