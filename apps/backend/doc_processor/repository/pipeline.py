"""Repository for fetching task and pipeline data from the database."""

from db.models import Task
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from utils.logger import log


class TaskRepository:
    """Repository for task-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_task_with_pipeline(self, task_id: int) -> Task | None:
        """
        Fetch a task by its ID with the associated pipeline configuration.
        Uses the foreign key relationship to load the pipeline in one query.

        Args:
            task_id: The task ID to fetch

        Returns:
            Task object with pipeline relationship loaded if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(Task).options(joinedload(Task.pipeline)).where(Task.id == task_id)
            )
            task = result.unique().scalar_one_or_none()

            if task:
                log.info(f"Found task {task_id}: {task.name}")
                if task.pipeline:
                    log.info(f"Task uses pipeline: {task.pipeline.name}")
                else:
                    log.warning(f"Task {task_id} has no associated pipeline")
            else:
                log.warning(f"Task {task_id} not found in database")

            return task
        except Exception as e:
            log.error(f"Error fetching task {task_id} with pipeline: {e}")
            raise

    async def update_task_status(
        self, task_id: int, status: str, result: dict | None = {}, failed_remarks: str | None = None
    ) -> bool:
        """
        Update the status of a task.

        Args:
            task_id: The task ID to update
            status: The new status value
            result: result
            error_message: Optional error message if status is FAILED

        Returns:
            True if update was successful, False otherwise
        """
        if result is None:
            result = {}
        try:
            query_result = await self.session.execute(select(Task).where(Task.id == task_id))
            task = query_result.scalar_one_or_none()
            if not task:
                log.warning(f"Task {task_id} not found for status update")
                return False
            task.status = status
            task.result = result
            task.failed_remarks = failed_remarks
            await self.session.flush()
            log.info(f"Updated task {task_id} status to {status}")
            return True
        except Exception as e:
            log.error(f"Error updating task {task_id} status: {e}")
            await self.session.rollback()
            raise

    async def decrement_task_rank(self) -> None:
        await self.session.execute(
            update(Task).where(Task.status == "queued").values(task_rank=Task.task_rank - 1)
        )
        await self.session.commit()
