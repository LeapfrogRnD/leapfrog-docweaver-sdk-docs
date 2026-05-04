"""Dependencies for process-now routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.config import get_config
from app.api.dependencies.db_session import get_db_session
from app.config.settings import Settings
from app.core.pipelines.repository import PipelineRepository
from app.core.process_now.service import ProcessNowService
from app.providers.storage.local_storage import LocalStorage


def get_process_now_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
) -> ProcessNowService:
    """Instantiate ProcessNowService always using local storage."""
    local_storage = LocalStorage(storage_path=settings.local_storage_path)
    return ProcessNowService(
        pipeline_repository=PipelineRepository(session),
        storage=local_storage,
        settings=settings,
    )


ProcessNowServiceDep = Annotated[ProcessNowService, Depends(get_process_now_service)]
