from db.models import TaskApiWorkFlowJobRun
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class TaskWorkFlowJobRunRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_task_workflow_run_by_id(self, job_run_id: int):
        result = await self.session.execute(
            select(TaskApiWorkFlowJobRun).where(TaskApiWorkFlowJobRun.id == job_run_id)
        )
        return result.scalar_one_or_none()

    async def update_task_workflow_run(
        self,
        job_run_id: int,
        status: str,
        result: dict | None = {},
        failed_remarks: str | None = None,
    ):
        await self.session.execute(
            update(TaskApiWorkFlowJobRun)
            .where(TaskApiWorkFlowJobRun.id == job_run_id)
            .values(status=status, result=result, failed_remarks=failed_remarks)
            .returning(TaskApiWorkFlowJobRun)
        )
        await self.session.flush()
