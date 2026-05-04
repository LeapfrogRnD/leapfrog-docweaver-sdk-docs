"""Task service for business logic."""

import uuid

from app.config.settings import Settings
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.core.pipelines.repository import PipelineRepository
from app.core.task_workflow_job_runs.repository import TaskWorkflowJobRunsRepository
from app.core.tasks.repository import TaskRepository
from app.core.tasks.schemas import (
    PresignedUrlRequest,
    PresignedUrlResponse,
    TaskConfigurationRequest,
    TaskDetailResponse,
    TaskExecuteResponse,
    TaskListFilterParams,
    TaskListResponse,
    TaskNameRequest,
    TaskResponse,
    TaskResultResponse,
    TaskStatsResponse,
)
from app.db.models import Task, User
from app.providers.queues.base import QueueProvider
from app.providers.storage.base import StorageInterface
from app.shared.constants.app_constants import (
    FileUploadStatus,
    Roles,
    RunTypes,
    TaskStatus,
    TaskTypes,
)
from app.shared.exceptions.common import (
    ForbiddenException,
    NotFoundException,
    PipelineConflictException,
)
from app.shared.utils.schema_converters import (
    convert_classification_schema_to_json_schema,
    convert_extraction_schema_to_json_schema,
)


class TaskService:
    """Service for task business logic."""

    def __init__(
        self,
        task_repository: TaskRepository,
        pipeline_repository=PipelineRepository,
        task_workflow_run_repository=TaskWorkflowJobRunsRepository,
        storage=StorageInterface,
        queue_provider=QueueProvider,
        settings=Settings,
    ):
        self.task_repository = task_repository
        self.pipeline_repository = pipeline_repository
        self.task_workflow_run_repository = task_workflow_run_repository
        self.storage = storage
        self.queue_provider = queue_provider
        self.settings = settings

    async def create_or_update_task_name(
        self, request: TaskNameRequest, user: User
    ) -> Task:
        job_run_payload = {
            "run_type": RunTypes.TASK_WORKFLOW,
            "status": TaskStatus.DRAFT,
        }
        if request.task_id:
            task = await self._get_task_by_id(request.task_id, user)
            self._check_task_execution(task, user)

            update_data = {"name": request.name}
            await self.task_repository.update_task(task, update_data)
            await self.task_workflow_run_repository.update_task_workflow_job_run_by_task_id(
                task.id,
                {
                    "task_id": task.id,
                    **job_run_payload,
                },
            )
        else:
            task = await self.task_repository.create_task(request.name, user.id)
            await self.task_workflow_run_repository.create_task_workflow_job_run(
                {
                    "task_id": task.id,
                    **job_run_payload,
                }
            )
        return TaskResponse.model_validate(task)

    async def generate_presigned_upload_url(
        self,
        task_id: int,
        payload: PresignedUrlRequest,
        user: User,
    ) -> PresignedUrlResponse:

        task = await self._get_task_by_id(task_id, user)
        self._check_task_execution(task, user)

        file_key = f"tasks/{task_id}/{uuid.uuid4()!s}.{payload.filename.rsplit('.', maxsplit=1)[-1]}"
        data = await self.storage.generate_presigned_upload_url(
            file_key=file_key, content_type=payload.file_metadata.content_type
        )
        await self.task_repository.update_task(
            task,
            {
                "file_metadata": {
                    "file_name": payload.filename,
                    "file_size": payload.file_metadata.file_size,
                    "content_type": payload.file_metadata.content_type,
                },
                "file_status": FileUploadStatus.PENDING,
            },
        )
        return PresignedUrlResponse(
            url=data["url"],
            file_key=data.get("file_key", file_key),
        )

    async def confirm_doc_upload(self, task_id: int, file_key: str, user: User) -> None:
        task = await self._get_task_by_id(task_id, user)
        self._check_task_execution(task, user)
        if task.file_status is None:
            raise ForbiddenException("Document upload not initiated for this task")

        await self.storage.confirm_upload(file_key)
        if task.file_key and task.file_key != file_key:
            await self.storage.delete(task.file_key)
        await self.task_repository.update_task(
            task,
            {
                "file_key": file_key,
                "file_metadata": {
                    **task.file_metadata,
                    "file_path": f"s3://{self.settings.aws_s3_bucket_name}/{file_key}",
                },
                "file_status": FileUploadStatus.UPLOADED,
            },
        )

    async def update_task_configuration(
        self, task_id: int, request: TaskConfigurationRequest, user: User
    ) -> TaskResponse:
        task = await self._get_task_by_id(task_id, user)
        self._check_task_execution(task, user)

        pipeline = await self.pipeline_repository.get_pipeline_by_id(
            request.pipeline_id
        )

        if not pipeline:
            raise NotFoundException("Associated pipeline not found")
        formatted_json_schema = None
        if request.task_type == TaskTypes.EXTRACTION:
            formatted_json_schema = convert_extraction_schema_to_json_schema(
                request.json_schema
            )
        if request.task_type == TaskTypes.CLASSIFICATION:
            formatted_json_schema = convert_classification_schema_to_json_schema(
                request.json_schema
            )

        update_data = {
            "formatted_json_schema": formatted_json_schema,
            "task_metadata": {
                "enable_context": request.enable_context,
            },
            **request.model_dump(exclude_unset=True),
        }

        task = await self.task_repository.update_task(task, update_data)
        await self.task_workflow_run_repository.update_task_workflow_job_run_by_task_id(
            task.id,
            {
                "status": TaskStatus.READY,
            },
        )
        return TaskResponse.model_validate(task)

    async def execute_task(self, task_id: int, user: User) -> TaskExecuteResponse:
        task = await self._get_task_by_id(task_id, user)
        if not task.pipeline.is_active:
            raise PipelineConflictException()
        if (
            task.lastest_job_run
            and task.lastest_job_run.status == TaskStatus.DRAFT
            and task.file_status != FileUploadStatus.UPLOADED
        ):
            raise ForbiddenException(
                f"task_workflow_run_repositoryDocument upload is not completed for this task | current_status: {task.lastest_job_run.status}"
            )

        self._check_task_execution(task, user)

        if task.lastest_job_run and task.lastest_job_run.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
        ]:
            job_run = (
                await self.task_workflow_run_repository.create_task_workflow_job_run(
                    {
                        "task_id": task.id,
                        "run_type": RunTypes.TASK_WORKFLOW,
                        "status": TaskStatus.QUEUED,
                    }
                )
            )
        else:
            job_run = await self.task_workflow_run_repository.update_task_workflow_job_run_by_task_id(
                task.id, {"status": TaskStatus.QUEUED}
            )

        if self.queue_provider is None:
            raise ValueError("queue provider not initialized")

        await self.task_repository.db_session.commit()

        try:
            await self.queue_provider.send_message(
                message_body={"job_run_id": job_run.id},
            )
        except Exception as e:
            await self.task_workflow_run_repository.update_task_workflow_job_run(
                job_run.id, {"status": TaskStatus.FAILED, "failed_remarks": str(e)}
            )
            await self.task_repository.db_session.commit()
            raise

        response = (
            await self.task_workflow_run_repository.get_queued_processing_job_runs()
        )
        return TaskExecuteResponse.model_validate(response)

    async def get_all_tasks(
        self,
        params: PaginationParams,
        filters: TaskListFilterParams,
    ) -> tuple[list[TaskListResponse], PaginationMetadata]:
        """Get all tasks with filters and pagination, irrespective of roles."""
        tasks_with_ranks, metadata = await self.task_repository.get_all_tasks(
            pagination=params,
            filters=filters,
        )
        task_responses = []
        for task, dynamic_rank in tasks_with_ranks:
            task_response = TaskListResponse.model_validate(task)
            if task.user:
                task_response.created_by_fullname = task.user.full_name
            task_response.status = (
                task.lastest_job_run.status if task.lastest_job_run else None
            )
            # Use the dynamically calculated rank instead of job_rank from DB
            task_response.task_rank = dynamic_rank
            task_response.updated_at = task.lastest_job_run.updated_at or task.updated_at
            task_responses.append(task_response)

        return task_responses, metadata

    async def get_task_detail(self, task_id: int, _: User) -> TaskDetailResponse:
        task = await self.task_repository.get_task_by_id(task_id, None)
        document_preview_url = None

        if task.file_key:
            document_preview_url = await self.storage.generate_presigned_download_url(
                file_key=task.file_key
            )
        response = TaskDetailResponse.model_validate(task)
        response.pipeline_name = task.pipeline.name if task.pipeline else None
        response.document_preview_url = document_preview_url
        response.status = task.lastest_job_run.status if task.lastest_job_run else None
        response.failed_remarks = (
            task.lastest_job_run.failed_remarks if task.lastest_job_run else None
        )
        if task.task_metadata and "enable_context" in task.task_metadata:
            response.enable_context = task.task_metadata["enable_context"]
        return response

    async def get_task_results(self, task_id: int, _: User) -> TaskResultResponse:
        task = await self.task_repository.get_task_by_id(task_id, None)
        document_preview_url = None
        if task.file_key:
            document_preview_url = await self.storage.generate_presigned_download_url(
                file_key=task.file_key
            )
        response = TaskResultResponse.model_validate(task)
        results = []
        if task.lastest_job_run.result:
            for item in task.lastest_job_run.result:
                pg_no = item.get("pages", {}).get("start", 0) + 1
                # TODO  just a quick fix for this time need to update this in doc_processor
                result = item.get("result", {})
                if "input_text_length" in result:
                    del result["input_text_length"]
                if task.task_type != "summarization":
                    result = result.get("data", {})
                result = result or {}
                flattened = {
                    "pg_no": pg_no,
                    **result,
                }
                results.append(flattened)
        response.document_preview_url = document_preview_url
        response.updated_at=task.lastest_job_run.updated_at
        response.result = results
        response.status = task.lastest_job_run.status if task.lastest_job_run else None
        return response

    async def delete_task(self, task_id: int, user: User) -> None:
        """Delete a task."""
        task = await self._get_task_by_id(task_id, user)
        self._check_task_execution(task, user)

        await self.task_repository.delete_task(task, user.id)
        if task.file_key and not task.is_duplicated:
            other_refs = await self.task_repository.count_tasks_with_file_key(
                task.file_key, exclude_task_id=task.id
            )
            if other_refs == 0:
                await self.storage.delete(task.file_key)

    async def upload_file(
        self,
        task_id: int,
        file_key: str,
        file: bytes,
        user: User,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> None:
        """Direct file upload accepting raw bytes for local storage.

        Args:
            task_id: ID of the task to attach the file to.
            file_key: Desired storage key/path for the uploaded file.
            file: Raw bytes of the file.
            user: Current user performing the upload.
            filename: Optional original filename to store in metadata.
            content_type: Optional MIME type of the uploaded file.
        """
        task = await self._get_task_by_id(task_id, user)
        self._check_task_execution(task, user)

        await self.storage.upload(file, file_key, content_type=content_type)

        if task.file_key and task.file_key != file_key:
            await self.storage.delete(task.file_key)

        await self.task_repository.update_task(
            task,
            {
                "status": TaskStatus.DRAFT,
                "file_key": file_key,
                "file_status": FileUploadStatus.UPLOADED,
                "file_metadata": {
                    "file_name": filename,
                    "file_size": len(file),
                    "content_type": content_type,
                    "file_path": f"/{file_key}",
                    "storage_mode": self.settings.storage_mode,
                },
            },
        )

    async def delete_task_file(self, task_id: int, user: User) -> None:
        """Delete a task file."""
        task = await self._get_task_by_id(task_id, user)
        self._check_task_execution(task, user)
        await self.storage.delete(task.file_key) if task.file_key else None
        await self.task_repository.update_task(
            task, {"file_key": None, "status": TaskStatus.DRAFT, "file_metadata": None}
        )

    async def duplicate_task(self, task_id: int, user: User) -> TaskResponse:
        """Duplicate an existing task with a new name."""
        original_task = await self.task_repository.get_task_by_id(task_id, None)
        self._check_task_execution(original_task, user)

        task = await self.task_repository.duplicate_task(
            original_task=original_task, user_id=user.id
        )
        await self.task_workflow_run_repository.create_task_workflow_job_run(
            {
                "task_id": task.id,
                "run_type": RunTypes.TASK_WORKFLOW,
                "status": TaskStatus.DRAFT,
            }
        )
        return TaskResponse.model_validate(task)

    async def _get_task_by_id(self, task_id: int, user: User) -> Task:
        """Get task by ID for the current user."""
        task = await self.task_repository.get_task_by_id(task_id, user)
        if not task:
            raise NotFoundException("Task not found")

        if user.role == Roles.ADMIN:
            return task

        if task.created_by != user.id:
            raise ForbiddenException("You don't have permission to view this task")

        return task

    def _check_task_execution(self, task: Task, user: User | None = None) -> None:
        superuser = user and user.is_superuser
        if (
            task.lastest_job_run
            and task.lastest_job_run.status
            in [
                TaskStatus.PROCESSING,
                TaskStatus.QUEUED,
            ]
            and not superuser
        ):
            raise ForbiddenException(
                f"Task is being processed | current_status: {task.lastest_job_run.status}"
            )

    async def get_task_stats(self) -> TaskStatsResponse:
        """Get task statistics."""
        stats = await self.task_workflow_run_repository.get_stats()
        return TaskStatsResponse(**stats)
