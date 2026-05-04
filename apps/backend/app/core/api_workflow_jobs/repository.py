from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.common.repository import BaseRepository
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.db.models import ApiWorkFlow, ApiWorkFlowJob, TaskApiWorkFlowJobRun
from app.shared.exceptions.common import NotFoundException


class ApiWorkflowJobsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def create_api_workflow_job(self, job_payload: dict) -> ApiWorkFlowJob:
        workflow_job = ApiWorkFlowJob(**job_payload)
        self.session.add(workflow_job)
        await self.session.flush()
        return workflow_job

    async def get_api_workflow_job_by_api_job_id(self, api_job_id: str) -> ApiWorkFlowJob:
        result = await self.session.execute(
            select(ApiWorkFlowJob)
            .options(joinedload(ApiWorkFlowJob.api_workflow))
            .options(selectinload(ApiWorkFlowJob.api_workflow_job_runs))
            .where(ApiWorkFlowJob.api_job_id == api_job_id)
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise NotFoundException(f"ApiWorkFlowJob with api_job_id {api_job_id} not found")
        return job

    async def get_api_workflow_job_with_runs(self, job_id: int) -> ApiWorkFlowJob:
        result = await self.session.execute(
            select(ApiWorkFlowJob)
            .options(joinedload(ApiWorkFlowJob.api_workflow_job_runs))
            .where(ApiWorkFlowJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def get_all_api_workflow_jobs_by_api_key_id(
        self, api_key_id: int, params: PaginationParams
    ) -> tuple[list[ApiWorkFlowJob], PaginationMetadata]:
        query = (
            select(ApiWorkFlowJob)
            .options(
                joinedload(ApiWorkFlowJob.api_workflow),
                selectinload(ApiWorkFlowJob.api_workflow_job_runs),
            )
            .order_by(ApiWorkFlowJob.id.desc())
            .where(ApiWorkFlowJob.api_workflow.has(ApiWorkFlow.api_key_id == api_key_id))
        )
        if params.search:
            query = query.where(
                ApiWorkFlowJob.api_workflow.has(ApiWorkFlow.name.ilike(f"%{params.search}%"))
                | ApiWorkFlowJob.api_job_id.ilike(f"%{params.search}%")
            )

        if params.status and params.status != "all":
            query = query.where(ApiWorkFlowJob.api_workflow_job_runs.any(TaskApiWorkFlowJobRun.status == params.status))
        integrations, metadata = await self.paginate(self.session, query, params)
        return integrations, metadata
