"""API key API dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_session import get_db_session
from app.core.api_keys.repository import ApiKeyRepository
from app.core.api_keys.service import ApiKeyService
from app.core.api_workflow_jobs.repository import ApiWorkflowJobsRepository
from app.core.task_workflow_job_runs.repository import TaskWorkflowJobRunsRepository


def get_api_key_service(
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeyService:
    """Get API key service instance."""
    return ApiKeyService(
        ApiKeyRepository(session),
        ApiWorkflowJobsRepository(session),
        TaskWorkflowJobRunsRepository(session),
    )


ApiKeyServiceDep = Annotated[ApiKeyService, Depends(get_api_key_service)]
