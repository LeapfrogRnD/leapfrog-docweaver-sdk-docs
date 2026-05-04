from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.common.repository import BaseRepository
from app.db.models import ApiWorkFlow, ApiWorkFlowJob, Task, TaskApiWorkFlowJobRun
from app.shared.constants.app_constants import RunTypes
from doc_processor.shared.constants.app_constants import TaskStatus


class TaskWorkflowJobRunsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create_task_workflow_job_run(self, payload: dict) -> TaskApiWorkFlowJobRun:
        workflow_job_run = TaskApiWorkFlowJobRun(**payload)
        self.session.add(workflow_job_run)
        await self.session.flush()
        return workflow_job_run

    async def update_task_workflow_job_run(
        self, job_run_id: int, payload: dict
    ) -> TaskApiWorkFlowJobRun:
        stmt = (
            update(TaskApiWorkFlowJobRun)
            .where(TaskApiWorkFlowJobRun.id == job_run_id)
            .values(**payload)
            .returning(TaskApiWorkFlowJobRun)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_in_progress_tasks_count(self, run_type: RunTypes) -> int:
        result = await self.session.execute(
            select(func.count(TaskApiWorkFlowJobRun.id)).where(
                TaskApiWorkFlowJobRun.status.in_([TaskStatus.QUEUED, TaskStatus.PROCESSING]),
                TaskApiWorkFlowJobRun.run_type == run_type,
            )
        )
        return result.scalar_one()

    async def fetch_latest_job_run(self, task_id: int, payload: dict):
        latest_job_run_subq = (
            select(TaskApiWorkFlowJobRun.id)
            .where(TaskApiWorkFlowJobRun.task_id == task_id)
            .order_by(TaskApiWorkFlowJobRun.created_at.desc())  # latest first
            .limit(1)
            .scalar_subquery()
        )

        stmt = (
            update(TaskApiWorkFlowJobRun)
            .where(TaskApiWorkFlowJobRun.id == latest_job_run_subq)
            .values(**payload)
            .returning(TaskApiWorkFlowJobRun)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_task_workflow_job_run_by_task_id(
        self, task_id: int, payload: dict
    ) -> TaskApiWorkFlowJobRun:
        return await self.fetch_latest_job_run(task_id, payload)

    async def get_job_run_count_by_task_id(self, task_id: int) -> int:
        result = await self.session.execute(
            select(func.count(TaskApiWorkFlowJobRun.id)).where(
                TaskApiWorkFlowJobRun.task_id == task_id
            )
        )
        return result.scalar_one()

    async def decrement_job_rank(self, run_type: RunTypes) -> None:
        await self.session.execute(
            update(TaskApiWorkFlowJobRun)
            .where(
                TaskApiWorkFlowJobRun.status == TaskStatus.QUEUED,
                TaskApiWorkFlowJobRun.run_type == run_type,
            )
            .values(job_rank=TaskApiWorkFlowJobRun.job_rank - 1)
        )

    async def get_stats(self, api_key_id: int | None = None) -> dict[str, int]:
        """
        Get task or API-key stats by latest job run.
        - If api_key_id is provided, returns stats for jobs under that API key (distinct by api_workflow_job_id).
        - Otherwise, returns stats for tasks (distinct by task_id), excluding deleted tasks.
        """
        run = TaskApiWorkFlowJobRun

        subq = select(run)

        if api_key_id is not None:
            job = aliased(ApiWorkFlowJob)
            workflow = aliased(ApiWorkFlow)

            subq = (
                subq.join(job, run.api_workflow_job_id == job.id)
                .join(workflow, job.api_workflow_id == workflow.id)
                .where(workflow.api_key_id == api_key_id)
            )

            distinct_col = run.api_workflow_job_id
            order_col = run.created_at.desc()

        else:
            task = aliased(Task)
            subq = subq.join(task, run.task_id == task.id).where(run.task_id.isnot(None))
            distinct_col = run.task_id
            order_col = run.created_at.desc()

        latest_subq = subq.distinct(distinct_col).order_by(distinct_col, order_col).subquery()

        stmt = select(latest_subq.c.status, func.count().label("count")).group_by(
            latest_subq.c.status
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        stats = {
            "total": 0,
            "draft": 0,
            "ready": 0,
            "processing": 0,
            "queued": 0,
            "completed": 0,
            "failed": 0,
        }

        for status, count in rows:
            stats[status] = count
            stats["total"] += count

        return stats

    async def get_queued_processing_job_runs(self) -> list[TaskApiWorkFlowJobRun]:
        run = TaskApiWorkFlowJobRun

        subq = select(TaskApiWorkFlowJobRun).join(Task, run.task_id == Task.id).where(
            run.task_id.isnot(None),
            run.status.in_([TaskStatus.QUEUED, TaskStatus.PROCESSING]),
)
        distinct_col = run.task_id
        order_col = run.created_at.desc()

        latest_subq = subq.distinct(distinct_col).order_by(distinct_col, order_col).subquery()

        stmt = select(latest_subq.c.status, func.count().label("count")).group_by(
            latest_subq.c.status
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return {
            "processing": 0,
            "queued": 0,
            **dict(rows),
        }
