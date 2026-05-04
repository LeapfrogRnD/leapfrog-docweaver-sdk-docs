import secrets
import uuid

from app.config.settings import Settings
from app.core.api_workflow_jobs.repository import (
    ApiWorkflowJobsRepository,
)
from app.core.api_workflows.repository import ApiWorkflowsRepository
from app.core.common.service import BaseService
from app.core.integration_apis.repository import IntegrationRepository
from app.core.integration_apis.schemas import (
    IntegrationRequest,
    IntegrationResponse,
    PollIntegrationResponse,
)
from app.core.task_workflow_job_runs.repository import (
    TaskWorkflowJobRunsRepository,
)
from app.db.models import ApiKeySecrets
from app.providers.queues.base import QueueProvider
from app.providers.storage.base import StorageInterface
from app.shared.constants.app_constants import RunTypes, TaskStatus, TaskTypes
from app.shared.exceptions.common import (
    ForbiddenException,
)


class IntegrationService(BaseService):
    """Service for integration-related business logic."""

    def __init__(
        self,
        repository: IntegrationRepository,
        api_workflow_repository: ApiWorkflowsRepository,
        api_workflow_job_repository: ApiWorkflowJobsRepository,
        task_workflow_job_runs_repository: TaskWorkflowJobRunsRepository,
        settings=Settings,
        storage=StorageInterface,
        queue_provider=QueueProvider,
    ):
        super().__init__()
        self.repository = repository
        self.api_workflow_repository = api_workflow_repository
        self.api_workflow_job_repository = api_workflow_job_repository
        self.task_workflow_job_runs_repository = task_workflow_job_runs_repository
        self.settings = settings
        self.storage = storage
        self.queue_provider = queue_provider

    async def create_integration(
        self, request: IntegrationRequest, api_key_secret: ApiKeySecrets
    ) -> IntegrationResponse:
        """Create a new integration job."""
        workflow = await self.api_workflow_repository.get_api_workflow_by_name(
            request.workflow_name
        )

        if workflow.api_key_id != api_key_secret.api_key_id:
            raise ForbiddenException("API key does not have access to this workflow")

        if workflow.api_key and workflow.api_key.deleted_at is not None:
            raise ForbiddenException("The API key associated with this workflow has been deleted")

        api_job_id = secrets.token_urlsafe(8).replace("_", "").replace("-", "")
        if request.s3_file_uri:
            file_path = request.s3_file_uri

        if request.file:
            file_content = await request.file.read()
            file_key = f"integrations/{api_job_id}/{uuid.uuid4()!s}.{request.file.filename.rsplit('.', maxsplit=1)[-1]}"
            await self.storage.upload(
                content=file_content,
                filename=file_key,
                content_type=request.file.content_type,
            )
            file_path = f"s3://{self.settings.aws_s3_bucket_name}/{file_key}"

        workflow_job = await self.api_workflow_job_repository.create_api_workflow_job(
            {
                "api_workflow_id": workflow.id,
                "api_job_id": api_job_id,
                "api_secret_id": api_key_secret.id,
                "file_metadata": {"file_path": file_path},
            }
        )
        job_run = await self.task_workflow_job_runs_repository.create_task_workflow_job_run(
            {
                "run_type": RunTypes.API_WORKFLOW,
                "api_workflow_job_id": workflow_job.id,
                "status": TaskStatus.QUEUED,
            }
        )

        if self.queue_provider is None:
            raise ValueError("queue provider not initialized")

        await self.repository.session.commit()

        try:
            await self.queue_provider.send_message(
                message_body={"job_run_id": job_run.id},
            )
        except Exception as e:
            await self.task_workflow_job_runs_repository.update_task_workflow_job_run(
                job_run.id, {"status": TaskStatus.FAILED, "failed_remarks": str(e)}
            )
            await self.repository.session.commit()
            raise

        return IntegrationResponse(
            integration_job_id=workflow_job.api_job_id, status=job_run.status
        )

    async def poll_integration_task(
        self, job_id: str, api_key_secret: ApiKeySecrets
    ) -> PollIntegrationResponse:
        """Poll the status of an integration task."""

        job = await self.api_workflow_job_repository.get_api_workflow_job_by_api_job_id(job_id)

        if job.api_workflow.api_key_id != api_key_secret.api_key_id:
            raise ForbiddenException("Unauthorized access to the integration job")

        latest_run = (
            max(job.api_workflow_job_runs, key=lambda s: s.created_at)
            if job.api_workflow_job_runs
            else None
        )
        results = None

        if latest_run and latest_run.result:
            results = []
            for item in latest_run.result:
                if job.api_workflow.workflow_type == TaskTypes.SUMMARIZATION:
                    flattened = {
                        "summary": item.get("result", {}).get("generation_response", {}),
                    }
                else:
                    pg_no = item.get("pages", {}).get("start", 0) + 1
                    flattened = {
                        "pg_no": pg_no,
                        **item.get("result", {}).get("data", {}),
                    }
                results.append(flattened)

        return PollIntegrationResponse(
            integration_job_id=job.api_job_id,
            integration_type=job.api_workflow.workflow_type,
            status=latest_run.status if latest_run else None,
            result=results,
            failed_remarks=latest_run.failed_remarks if latest_run else None,
        )
