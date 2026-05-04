"""Pipeline repository for database operations."""

from sqlalchemy import Sequence, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.common.repository import BaseRepository
from app.core.common.schema import (
    DataResultStatus,
    PaginationMetadata,
    PaginationParams,
)
from app.db.models import Pipeline, Task, User


class PipelineRepository(BaseRepository):
    """Repository for pipeline-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pipeline(self, pipeline_data: dict) -> Pipeline:
        """Create a new pipeline."""
        pipeline = Pipeline(**pipeline_data)
        self.session.add(pipeline)
        await self.session.commit()
        await self.session.refresh(pipeline)
        return pipeline

    async def get_stats(
        self,
    ) -> int:
        """Return the number of non-deleted tasks that reference the given file_key.

        If exclude_task_id is provided, that task ID will be excluded from the count
        (useful when checking whether other tasks reference the same file).
        """
        subquery = (
            select(Pipeline.updated_at)
            .order_by(desc(Pipeline.updated_at))
            .limit(1)
            .scalar_subquery()
        )

        query = select(func.count(), subquery).select_from(Pipeline)

        result = await self.session.execute(query)
        return result.one_or_none()

    async def get_pipeline_by_id(self, pipeline_id: int) -> Pipeline | None:
        """Get pipeline by ID."""
        stmt = select(Pipeline).where(Pipeline.id == pipeline_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pipeline_by_name(self, name: str) -> Pipeline | None:
        """Get pipeline by name."""
        stmt = select(Pipeline).where(Pipeline.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_pipelines(
        self, params: PaginationParams, _: User
    ) -> tuple[Sequence[Pipeline], PaginationMetadata]:
        """Get all pipelines with optional status filtering and pagination."""

        stmt = (
            select(Pipeline)
            .options(selectinload(Pipeline.user))
            .order_by(Pipeline.created_at.desc())
        )

        if params.status != DataResultStatus.all:
            is_active = params.status == DataResultStatus.active
            stmt = stmt.where(Pipeline.is_active == is_active)

        if params.search:
            stmt = stmt.where(Pipeline.name.ilike(f"%{params.search}%"))
        # if current_user.role != Roles.ADMIN:
        #     stmt = stmt.where(or_(Pipeline.is_default, Pipeline.created_by == current_user.id))

        pipelines, meta = await self.paginate(self.session, stmt, params)
        return pipelines, meta

    async def update_pipeline(
        self, pipeline_id: int, update_data: dict
    ) -> Pipeline | None:
        """Update pipeline by ID."""
        pipeline = await self.get_pipeline_by_id(pipeline_id)
        if pipeline:
            for key, value in update_data.items():
                if value is not None:
                    setattr(pipeline, key, value)
            await self.session.commit()
            await self.session.refresh(pipeline)
            return pipeline
        return None

    async def delete_pipeline(self, pipeline_id: int, user_id: int) -> bool:
        """Delete a pipeline by ID."""
        pipeline = await self.get_pipeline_by_id(pipeline_id)
        if pipeline:
            pipeline.soft_delete(user_id)
            self.session.add(pipeline)
            await self.session.flush()
            return True
        return False

    async def toggle_pipeline_status(self, pipeline_id: int) -> Pipeline | None:
        """Toggle pipeline active status."""
        pipeline = await self.get_pipeline_by_id(pipeline_id)
        if pipeline:
            pipeline.is_active = not pipeline.is_active
            await self.session.commit()
            await self.session.refresh(pipeline)
            return pipeline
        return None

    async def duplicate_pipeline(
        self, pipeline_id: int, created_by: int
    ) -> Pipeline | None:
        """Duplicate a pipeline with a new name."""
        original_pipeline = await self.get_pipeline_by_id(pipeline_id)
        if not original_pipeline:
            return None

        # Create new pipeline with copied data
        pipeline_data = {
            "name": original_pipeline.name + " Copy",
            "description": original_pipeline.description,
            "is_active": original_pipeline.is_active,
            "ocr_provider": original_pipeline.ocr_provider,
            "parsing_method": original_pipeline.parsing_method,
            "vlm_model": original_pipeline.vlm_model,
            "vlm_model_provider": original_pipeline.vlm_model_provider,
            "llm_model": original_pipeline.llm_model,
            "llm_model_provider": original_pipeline.llm_model_provider,
            "created_by": created_by,
        }

        new_pipeline = Pipeline(**pipeline_data)
        self.session.add(new_pipeline)
        await self.session.commit()
        await self.session.refresh(new_pipeline)
        return new_pipeline

    async def pipeline_exists_by_name(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """Check if pipeline exists by name, optionally excluding a specific ID."""
        stmt = select(Pipeline).where(Pipeline.name == name)
        if exclude_id:
            stmt = stmt.where(Pipeline.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def task_exists(self, pipeline_id: str) -> bool:
        """Check if task exists for deleting pipeline"""
        stmt = select(Task).where(Task.pipeline_id == pipeline_id)
        result = await self.session.execute(stmt)
        return result.scalar() is not None
