"""Pipeline API routes."""

from fastapi import APIRouter, Depends, Path

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.config import get_config
from app.api.routes.pipelines.dependencies import PipelineServiceDep
from app.config.settings import Settings
from app.core.common.schema import (
    GenericListResponse,
    GenericResponse,
    PaginationParams,
)
from app.core.pipelines.schemas import (
    PipelineConfigsResponse,
    PipelineCreateRequest,
    PipelineResponse,
    PipelineUpdateRequest,
    StatsResponse,
)
from app.db.models import User

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.get("/stats", response_model=GenericResponse[StatsResponse])
async def get_task_stats(
    pipeline_service: PipelineServiceDep,
    _: User = Depends(get_current_user),
):
    """
    Get pipeline statistics.

    Returns statistics for all pipelines including:
    - Total number of pipelines
    - Last updated date
    """
    stats = await pipeline_service.get_stats()
    return GenericResponse[StatsResponse](data=stats)


@router.get("/configs", response_model=GenericResponse[PipelineConfigsResponse])
async def get_pipeline_configs(
    pipeline_service: PipelineServiceDep,
    config: Settings = Depends(get_config),
    _: User = Depends(get_current_user),
):
    """Get available pipeline configuration options."""
    configs = pipeline_service.get_configs(config)
    return GenericResponse[PipelineConfigsResponse](data=configs)


@router.post("/", response_model=GenericResponse[PipelineResponse])
async def create_pipeline(
    request: PipelineCreateRequest,
    pipeline_service: PipelineServiceDep,
    current_user: User = Depends(get_current_user),
):
    """Create a new pipeline."""
    pipeline = await pipeline_service.create_pipeline(request, current_user)
    return GenericResponse[PipelineResponse](data=pipeline)


@router.get("/", response_model=GenericListResponse[PipelineResponse])
async def get_pipelines(
    pipeline_service: PipelineServiceDep,
    query_params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Get all pipelines with pagination."""
    pipelines, metadata = await pipeline_service.get_all_pipelines(
        query_params, current_user
    )
    return GenericListResponse[PipelineResponse](data=pipelines, metadata=metadata)


@router.get("/{pipeline_id}", response_model=GenericResponse[PipelineResponse])
async def get_pipeline(
    pipeline_service: PipelineServiceDep,
    pipeline_id: int = Path(..., description="ID of the pipeline to retrieve"),
    current_user: User = Depends(get_current_user),
):
    """Get pipeline by ID."""
    pipeline = await pipeline_service.get_pipeline_by_id(pipeline_id, current_user)
    return GenericResponse[PipelineResponse](data=pipeline)


@router.put("/{pipeline_id}", response_model=GenericResponse[PipelineResponse])
async def update_pipeline(
    request: PipelineUpdateRequest,
    pipeline_service: PipelineServiceDep,
    pipeline_id: int = Path(..., description="ID of the pipeline to update"),
    current_user: User = Depends(get_current_user),
):
    """Update pipeline by ID."""
    pipeline = await pipeline_service.update_pipeline(
        pipeline_id, request, current_user
    )
    return GenericResponse[PipelineResponse](data=pipeline)


@router.patch(
    "/{pipeline_id}/toggle-status", response_model=GenericResponse[PipelineResponse]
)
async def toggle_pipeline_status(
    pipeline_service: PipelineServiceDep,
    pipeline_id: int = Path(..., description="ID of the pipeline to toggle status"),
    current_user: User = Depends(get_current_user),
):
    """Toggle pipeline active status."""
    pipeline = await pipeline_service.toggle_pipeline_status(pipeline_id, current_user)
    return GenericResponse[PipelineResponse](data=pipeline)


@router.post(
    "/{pipeline_id}/duplicate", response_model=GenericResponse[PipelineResponse]
)
async def duplicate_pipeline(
    pipeline_service: PipelineServiceDep,
    pipeline_id: int = Path(..., description="ID of the pipeline to duplicate"),
    current_user: User = Depends(get_current_user),
):
    """Duplicate an existing pipeline with a new name."""
    pipeline = await pipeline_service.duplicate_pipeline(pipeline_id, current_user)
    return GenericResponse[PipelineResponse](data=pipeline)


@router.delete("/{pipeline_id}", response_model=GenericResponse[str])
async def delete_pipeline(
    pipeline_service: PipelineServiceDep,
    pipeline_id: int = Path(..., description="ID of the pipeline to delete"),
    current_user: User = Depends(get_current_user),
):
    """Delete pipeline by ID."""
    await pipeline_service.delete_pipeline(pipeline_id, current_user)
    return GenericResponse[str](data="Pipeline deleted successfully")
