import datetime
from typing import Any

from fastapi import UploadFile
from pydantic import Field

from app.core.common.schema import OrmResponseModel, RequestModel
from app.core.pipelines.schemas import BasePipelineRequest
from app.shared.constants.app_constants import TaskStatus


class IntegrationPipelineConfig(BasePipelineRequest):
    """Schema for pipeline configuration details in integration requests."""


class IntegrationRequest(RequestModel):
    s3_file_uri: str | None = Field(None, description="S3 URI of the file to integrate with")
    file: UploadFile | None = Field(
        None, description="File to integrate with (if not using S3 URI)"
    )
    workflow_name: str = Field(..., description="Name of the workflow to execute")


class IntegrationResponse(OrmResponseModel):
    integration_job_id: str
    status: str


class PollIntegrationResponse(OrmResponseModel):
    integration_job_id: str
    integration_type: str
    status: str | None = None
    result: list[dict[str, Any]] | None = None
    failed_remarks: str | None = None


class IntegrationListResponse(OrmResponseModel):
    """Integrations list item response schema."""

    job_id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: TaskStatus = Field(..., description="Current task status")
    type: str | None = Field(None, description="Task type")
    rank: int | None = Field(None, description="Task rank for ordering in pipeline")
    created_at: datetime.datetime = Field(..., description="Task creation timestamp")


class IntegrationStatsResponse(OrmResponseModel):
    """Integrations statistics response schema."""

    total: int = Field(..., description="Total number of integrations")
    draft: int = Field(..., description="Number of integrations in draft status")
    ready: int = Field(..., description="Number of integrations in ready status")
    processing: int = Field(..., description="Number of integrations in processing status")
    queued: int = Field(..., description="Number of integrations in queued status")
    completed: int = Field(..., description="Number of integrations in completed status")
    failed: int = Field(..., description="Number of integrations in failed status")
