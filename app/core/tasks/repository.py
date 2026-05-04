"""Task repository for database operations."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.common.repository import BaseRepository
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.core.tasks.schemas import TaskListFilterParams
from app.db.models import Task, TaskApiWorkFlowJobRun, User
from app.shared.constants.app_constants import RunTypes, TaskStatus


class TaskRepository(BaseRepository):
    """Repository for task database operations."""

    def __init__(self, db_session: AsyncSession):
        super().__init__()
        self.db_session = db_session

    async def create_task(self, name: str, created_by: int) -> Task:
        task = Task(name=name, created_by=created_by)
        self.db_session.add(task)
        await self.db_session.commit()
        return task

    async def get_task_by_id(
        self, task_id: int, user: User | None = None
    ) -> Task | None:
        """Get task by ID, optionally filtered by user."""
        query = select(Task).options(
            selectinload(Task.user),
            selectinload(Task.pipeline),
            selectinload(Task.task_job_runs),
        )

        if user and user.id and not user.is_superuser:
            query = query.where(Task.id == task_id, Task.created_by == user.id)
        else:
            query = query.where(Task.id == task_id)

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def update_task(self, task: Task, update_data: dict[str, Any]) -> Task:
        """Update task with provided fields from dictionary."""
        for key, value in update_data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self.db_session.flush()
        return task

    async def get_all_tasks(
        self,
        pagination: PaginationParams,
        filters: TaskListFilterParams,
    ) -> tuple[list[tuple[Task, int | None]], PaginationMetadata]:
        """Get all tasks with filters and pagination, including user information.

        Dynamically calculates a rank for tasks whose latest job run status is
        QUEUED or PROCESSING using a window function (ROW_NUMBER).
        The rank is ordered by task creation time (oldest first) within these statuses.
        Tasks with other statuses will have rank=None.

        Returns:
            tuple containing:
                - list of tuples (Task, dynamic_rank) where dynamic_rank is int for queued/processing or None
                - PaginationMetadata
        """
        latest_run_cte = (
            select(
                TaskApiWorkFlowJobRun.task_id,
                TaskApiWorkFlowJobRun.status,
                TaskApiWorkFlowJobRun.created_at,
                TaskApiWorkFlowJobRun.updated_at,
                TaskApiWorkFlowJobRun.id.label("run_id"),
                func.row_number()
                .over(
                    partition_by=TaskApiWorkFlowJobRun.task_id,
                    order_by=TaskApiWorkFlowJobRun.created_at.desc(),
                )
                .label("rn"),
            )
            .where(
                TaskApiWorkFlowJobRun.task_id.is_not(None),
                TaskApiWorkFlowJobRun.run_type == RunTypes.TASK_WORKFLOW,
            )
            .cte("latest_runs")
        )

        # Filter to only the latest run (rn = 1)
        latest_job_run_subq = (
            select(
                latest_run_cte.c.task_id,
                latest_run_cte.c.status,
                latest_run_cte.c.created_at,
                latest_run_cte.c.updated_at,
                latest_run_cte.c.run_id,
            )
            .where(latest_run_cte.c.rn == 1)
            .subquery()
        )

        # Step 2: CTE with row_number only for queued/processing tasks (exclude soft-deleted tasks)
        queued_processing_ranks_cte = (
            select(
                latest_job_run_subq.c.task_id,
                func.row_number()
                .over(order_by=latest_job_run_subq.c.created_at.asc())
                .label("dynamic_rank"),
            )
            .join(Task, Task.id == latest_job_run_subq.c.task_id)
            .where(
                latest_job_run_subq.c.status.in_(
                    [
                        TaskStatus.QUEUED.value,
                        TaskStatus.PROCESSING.value,
                    ]
                ),
                Task.deleted_at.is_(None),
            )
            .cte("queued_processing_ranks")
        )

        # Step 3: Main query - only select what we need
        query = (
            select(
                Task,
                queued_processing_ranks_cte.c.dynamic_rank,
            )
            .outerjoin(latest_job_run_subq, latest_job_run_subq.c.task_id == Task.id)
            .outerjoin(
                queued_processing_ranks_cte,
                queued_processing_ranks_cte.c.task_id == Task.id,
            )
            .options(
                selectinload(Task.user),
                selectinload(Task.pipeline),
                selectinload(Task.task_job_runs),
            )
        )

        # Apply filters if provided
        if filters.status:
            query = query.where(latest_job_run_subq.c.status == filters.status.value)
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.filter(Task.name.ilike(pattern))

        # Order by task ID descending (most recent first)
        query = query.order_by(Task.id.desc())

        items, metadata = await self.paginate(
            self.db_session, query, pagination, get_all=True
        )

        return items, metadata

    async def delete_task(self, task: Task, user_id: int) -> None:
        """Delete a task."""
        task.soft_delete(user_id)
        self.db_session.add(task)
        await self.db_session.flush()

    async def duplicate_task(self, original_task: Task, user_id: int) -> Task:
        """Create a duplicate of an existing task with a new name."""
        duplicated_task = Task(
            name=original_task.name + " Copy",
            additional_instruction=original_task.additional_instruction,
            task_type=original_task.task_type,
            file_key=original_task.file_key,
            file_metadata=original_task.file_metadata,
            json_schema=original_task.json_schema,
            formatted_json_schema=original_task.formatted_json_schema,
            pipeline_id=original_task.pipeline_id,
            created_by=user_id,
            is_duplicated=True,
        )
        self.db_session.add(duplicated_task)
        await self.db_session.flush()
        return duplicated_task

    async def count_tasks_with_file_key(
        self, file_key: str, exclude_task_id: int | None = None
    ) -> int:
        """Return the number of non-deleted tasks that reference the given file_key.

        If exclude_task_id is provided, that task ID will be excluded from the count
        (useful when checking whether other tasks reference the same file).
        """
        query = select(func.count()).select_from(Task).where(Task.file_key == file_key)
        if exclude_task_id is not None:
            query = query.where(Task.id != exclude_task_id)
        result = await self.db_session.execute(query)
        return int(result.scalar_one())
