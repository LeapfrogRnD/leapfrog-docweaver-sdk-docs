"""Dependencies for api workflow routes."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_session import get_db_session
from app.core.api_workflows.repository import ApiWorkflowsRepository
from app.core.api_workflows.service import ApiWorkFlowService


def get_api_workflow_service(
    session: AsyncSession = Depends(get_db_session),
) -> ApiWorkFlowService:
    """Get workflow service instance."""
    return ApiWorkFlowService(ApiWorkflowsRepository(session))


ApiWorkFlowServiceDep = Annotated[ApiWorkFlowService, Depends(get_api_workflow_service)]
