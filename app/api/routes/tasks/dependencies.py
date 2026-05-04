"""Task API dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.config import get_config
from app.api.dependencies.db_session import get_db_session
from app.api.dependencies.queue import QueueProviderDep
from app.api.dependencies.storage import StorageDep
from app.config.settings import Settings
from app.core.pipelines.repository import PipelineRepository
from app.core.task_workflow_job_runs.repository import TaskWorkflowJobRunsRepository
from app.core.tasks.repository import TaskRepository
from app.core.tasks.service import TaskService


def get_task_service(
    storage: StorageDep,
    queue_provider: QueueProviderDep,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
) -> TaskService:
    """Get task service instance."""
    return TaskService(
        TaskRepository(session),
        PipelineRepository(session),
        TaskWorkflowJobRunsRepository(session),
        storage,
        queue_provider,
        settings,
    )


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
