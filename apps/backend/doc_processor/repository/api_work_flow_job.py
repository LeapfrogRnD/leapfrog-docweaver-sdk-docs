from db.models import ApiWorkFlow, ApiWorkFlowJob
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class ApiWorkFlowJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_api_workflow_job_with_workflow(self, workflow_job_id: int):
        result = await self.session.execute(
            select(ApiWorkFlowJob)
            .options(joinedload(ApiWorkFlowJob.api_workflow).joinedload(ApiWorkFlow.api_key))
            .where(ApiWorkFlowJob.id == workflow_job_id)
        )
        return result.scalar_one_or_none()
