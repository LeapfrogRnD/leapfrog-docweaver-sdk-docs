from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.config import get_config
from app.api.dependencies.db_session import get_db_session
from app.api.dependencies.queue import QueueProviderDep
from app.api.dependencies.storage import StorageDep
from app.config.settings import Settings
from app.core.api_workflow_jobs.repository import ApiWorkflowJobsRepository
from app.core.api_workflows.repository import ApiWorkflowsRepository
from app.core.integration_apis.repository import IntegrationRepository
from app.core.integration_apis.service import IntegrationService
from app.core.task_workflow_job_runs.repository import (
    TaskWorkflowJobRunsRepository,
)


def get_integration_service(
    storage: StorageDep,
    queue_provider: QueueProviderDep,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
) -> IntegrationService:
    """Get task service instance."""
    return IntegrationService(
        IntegrationRepository(session),
        ApiWorkflowsRepository(session),
        ApiWorkflowJobsRepository(session),
        TaskWorkflowJobRunsRepository(session),
        settings,
        storage,
        queue_provider,
    )


IntegrationServiceDep = Annotated[IntegrationService, Depends(get_integration_service)]
