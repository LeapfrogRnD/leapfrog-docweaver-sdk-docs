"""API workflow repository for database operations."""

from sqlalchemy import exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.common.repository import BaseRepository
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.db.models import ApiWorkFlow
from app.shared.exceptions.common import BadRequestException, NotFoundException


class ApiWorkflowsRepository(BaseRepository):
    """Repository for API workflow-related database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def check_workflow_name_exists(self, name: str, workflow_id: str | None = None) -> bool:
        """Check if an API workflow with the same name already exists"""
        stmt = select(
            exists().where(
                (func.lower(ApiWorkFlow.name) == name.lower().strip())
                & (ApiWorkFlow.id != workflow_id if workflow_id else True)
                & (ApiWorkFlow.deleted_at.is_(None))
            )
        )
        result = await self.session.execute(stmt)
        if result.scalar():
            raise BadRequestException("An API workflow with this name already exists")

    async def create_api_workflow(self, api_workflow_data: dict) -> ApiWorkFlow:
        """Create a new API workflow."""
        api_workflow = ApiWorkFlow(**api_workflow_data)
        self.session.add(api_workflow)
        await self.session.flush()
        return api_workflow

    async def get_api_workflow_by_id(
        self, workflow_id: int, api_key_id: int | None = None
    ) -> ApiWorkFlow | None:
        """Get API workflow by ID, optionally scoped by api_key_id."""
        stmt = select(ApiWorkFlow).where(ApiWorkFlow.id == workflow_id)
        if api_key_id is not None:
            stmt = stmt.where(ApiWorkFlow.api_key_id == api_key_id)
        result = await self.session.execute(stmt)
        api_workflow = result.scalar_one_or_none()
        if not api_workflow:
            raise NotFoundException("API workflow not found")
        return api_workflow

    async def get_api_workflow_by_name(
        self, name: str, api_key_id: int | None = None
    ) -> ApiWorkFlow | None:
        """Get API workflow by name, optionally scoped by api_key_id."""
        stmt = (
            select(ApiWorkFlow)
            .options(joinedload(ApiWorkFlow.api_key))
            .where(func.lower(ApiWorkFlow.name) == name.lower().strip())
            .where(ApiWorkFlow.deleted_at.is_(None))
            .execution_options(include_deleted=True)
        )
        if api_key_id is not None:
            stmt = stmt.where(ApiWorkFlow.api_key_id == api_key_id)
        result = await self.session.execute(stmt)
        api_workflow = result.scalar_one_or_none()
        if not api_workflow:
            raise NotFoundException("API workflow not found")
        return api_workflow

    async def get_all_api_workflows(
        self, api_key_id: int, params: PaginationParams
    ) -> tuple[list[ApiWorkFlow], PaginationMetadata]:
        """Get all API workflows for a specific API key."""
        stmt = (
            select(ApiWorkFlow)
            .where(ApiWorkFlow.api_key_id == api_key_id)
            .order_by(ApiWorkFlow.created_at.desc())
        )
        api_workflows, meta = await self.paginate(self.session, stmt, params)
        return api_workflows, meta

    async def update_api_workflow(self, workflow_id: int, payload: dict) -> ApiWorkFlow:
        """Update an API workflow by ID."""
        stmt = (
            update(ApiWorkFlow)
            .where(ApiWorkFlow.id == workflow_id)
            .values(**payload)
            .returning(ApiWorkFlow)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_api_workflow(self, workflow_id: int, user_id: int | None) -> None:
        """Soft delete an API workflow by ID."""
        api_workflow = await self.get_api_workflow_by_id(workflow_id, None)
        api_workflow.soft_delete(user_id)
        self.session.add(api_workflow)
        await self.session.flush()
