"""Dependencies for pipeline routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_session import get_db_session
from app.core.pipelines.repository import PipelineRepository
from app.core.pipelines.service import PipelineService


def get_pipeline_service(
    session: AsyncSession = Depends(get_db_session),
) -> PipelineService:
    """Get pipeline service instance."""
    return PipelineService(PipelineRepository(session))


PipelineServiceDep = Annotated[PipelineService, Depends(get_pipeline_service)]
