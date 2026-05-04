"""Worker that receives messages from SQS and prints hello."""

import asyncio
import os

import httpx
from config.settings import settings
from db.session import AsyncSessionLocal
from repository.api_work_flow_job import ApiWorkFlowJobRepository
from repository.pipeline import TaskRepository
from repository.task_workflow_run import TaskWorkFlowJobRunRepository
from services.mapper import task_mapper
from services.sqs_service import SQSReceiver, sqs_receiver
from shared.constants.app_constants import RunTypes, TaskStatus, TaskTypes
from utils.logger import log

from core.exceptions import LeapXProcessingException


class Worker:
    """Main worker that receives messages from SQS."""

    def __init__(self):
        self.sqs_receiver = sqs_receiver
        self.dlq_receiver: SQSReceiver | None = None
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TASKS)
        self.active_tasks: set[asyncio.Task] = set()
        self.dlq_listener_task: asyncio.Task | None = None

        ecs_task_id = os.getenv("ECS_TASK_ID")
        if ecs_task_id:
            settings.WORKER_ID = ecs_task_id
            log.info(f"Worker ID set to ECS task ID: {ecs_task_id}")
        log.info(
            f"Worker initialized with MAX_CONCURRENT_TASKS={settings.MAX_CONCURRENT_TASKS}"
        )

    async def _initialize_dlq_receiver(self):
        dlq_url = settings.SQS_DLQ_URL
        if dlq_url:
            log.info(f"Using explicit DLQ URL from settings: {dlq_url}")
        else:
            dlq_url = await asyncio.to_thread(self.sqs_receiver.resolve_dead_letter_queue_url)

        if not dlq_url:
            log.warning(
                "DLQ URL not configured. Could not derive from SQS_QUEUE_URL via "
                "RedrivePolicy or naming fallback (<queue>%s), so DLQ listener is disabled.",
                settings.SQS_DLQ_SUFFIX,
            )
            return

        self.dlq_receiver = SQSReceiver(dlq_url)
        log.info(f"Resolved DLQ URL for listener: {dlq_url}")

    async def _start_dlq_listener(self):
        if not self.dlq_receiver:
            return

        log.info("Starting DLQ listener")
        try:
            await self.dlq_receiver.start_receiving(self._handle_dlq_message)
        except asyncio.CancelledError:
            log.info("DLQ listener cancelled")
        except Exception as e:
            log.error(f"DLQ listener failed: {e}")

    async def _handle_dlq_message(self, message: dict, receipt_handle: str):
        job_run_id = message.get("job_run_id")
        if not job_run_id:
            log.error(f"DLQ message missing job_run_id: {message}")
            await self.dlq_receiver.delete_message(receipt_handle)
            return

        try:
            async with AsyncSessionLocal() as session:
                job_run_repo = TaskWorkFlowJobRunRepository(session)
                job = await job_run_repo.get_task_workflow_run_by_id(job_run_id)
                if not job:
                    log.warning(f"DLQ job run {job_run_id} not found in database")
                elif job.status in [TaskStatus.QUEUED, TaskStatus.PROCESSING]:
                    await job_run_repo.update_task_workflow_run(
                        job_run_id,
                        TaskStatus.FAILED,
                        {},
                        "Moved to DLQ after max retries. Likely worker crash or repeated runtime failure.",
                    )
                    log.warning(f"Marked job run {job_run_id} as failed from DLQ")
                else:
                    log.info(
                        "Skipping DLQ failure update for job run %s with terminal status %s",
                        job_run_id,
                        job.status,
                    )
                await session.commit()
        except Exception as e:
            log.error(f"Failed to mark DLQ job run {job_run_id} as failed: {e}")
        finally:
            await self.dlq_receiver.delete_message(receipt_handle)

    async def start(self):
        """Start the worker."""
        log.info(f"Starting worker {settings.WORKER_ID}")

        try:
            await self._initialize_dlq_receiver()
            if self.dlq_receiver:
                self.dlq_listener_task = asyncio.create_task(self._start_dlq_listener())
            await self.sqs_receiver.start_receiving(self.handle_message)
        except asyncio.CancelledError:
            log.info("Worker cancelled")
        finally:
            if self.dlq_receiver:
                self.dlq_receiver.stop_receiving()
            if self.dlq_listener_task:
                self.dlq_listener_task.cancel()
                await asyncio.gather(self.dlq_listener_task, return_exceptions=True)
            if self.active_tasks:
                log.info(
                    f"Waiting for {len(self.active_tasks)} active tasks to complete..."
                )
                await asyncio.gather(*self.active_tasks, return_exceptions=True)

    async def handle_message(self, message: dict, receipt_handle: str):
        """
        Handle a received message.

        Args:
            message: The message body as a dict (should contain task_id)
            receipt_handle: SQS receipt handle for deleting the message
        """
        task = asyncio.create_task(
            self._process_message_with_semaphore(message, receipt_handle)
        )
        self.active_tasks.add(task)
        task.add_done_callback(self.active_tasks.discard)

    async def _process_message_with_semaphore(self, message: dict, receipt_handle: str):
        """
        Process a message with semaphore-based concurrency control.

        Args:
            message: The message body as a dict (should contain task_id)
            receipt_handle: SQS receipt handle for deleting the message
        """
        async with self.semaphore:
            log.info(
                f"Acquired semaphore. Active tasks: {settings.MAX_CONCURRENT_TASKS - self.semaphore._value}/{settings.MAX_CONCURRENT_TASKS}"
            )
            await self._process_task(message, receipt_handle)

    async def _process_task(self, message: dict, receipt_handle: str):
        """
        Process a single task.

        Args:
            message: The message body as a dict (should contain task_id)
            receipt_handle: SQS receipt handle for deleting the message
        """
        log.info(f"Received message: {message}")
        job_run_id = message.get("job_run_id")
        try:
            if not job_run_id:
                err_msg = "No job_run_id found in SQS message"
                log.error(err_msg)
                raise LeapXProcessingException(err_msg)  # noqa: TRY301

            async with AsyncSessionLocal() as session:
                job_run_repo = TaskWorkFlowJobRunRepository(session)
                webhook_url: str | None = None
                job = await job_run_repo.get_task_workflow_run_by_id(job_run_id)

                if not job:
                    err_msg = f"Job run {job_run_id} not found in database"
                    log.error(err_msg)
                    raise LeapXProcessingException(err_msg)  # noqa: TRY301

                await job_run_repo.update_task_workflow_run(
                    job_run_id, TaskStatus.PROCESSING
                )
                await session.commit()

                if job.run_type not in [RunTypes.API_WORKFLOW, RunTypes.TASK_WORKFLOW]:
                    err_msg = (
                        f"Unknown run type: {job.run_type} for job run {job_run_id}"
                    )
                    log.error(err_msg)
                    raise LeapXProcessingException(err_msg)  # noqa: TRY301

                if job.run_type == RunTypes.API_WORKFLOW:
                    api_workflow_job_repo = ApiWorkFlowJobRepository(session)
                    api_workflow_job = (
                        await api_workflow_job_repo.get_api_workflow_job_with_workflow(
                            job.api_workflow_job_id
                        )
                    )
                    if not api_workflow_job:
                        err_msg = f"API workflow job {job.api_workflow_job_id} not found in database"
                        log.error(err_msg)
                        raise LeapXProcessingException(err_msg)  # noqa: TRY301

                    if (
                        api_workflow_job.api_workflow
                        and api_workflow_job.api_workflow.api_key
                    ):
                        webhook_url = api_workflow_job.api_workflow.api_key.webhook_url

                    task_type = api_workflow_job.api_workflow.workflow_type
                    document_path = (
                        api_workflow_job.file_metadata.get("file_path")
                        if api_workflow_job.file_metadata
                        else None
                    )
                    execution_config = api_workflow_job.execution_config
                    log.info(
                        f"Processing API workflow job {job.api_workflow_job_id}: type={task_type}, document={document_path}"
                    )
                if job.run_type == RunTypes.TASK_WORKFLOW:
                    task_repo = TaskRepository(session)
                    task = await task_repo.get_task_with_pipeline(job.task_id)

                    if not task:
                        err_msg = f"Task {job.task_id} not found in database"
                        log.error(err_msg)
                        raise LeapXProcessingException(err_msg)  # noqa: TRY301

                    task_type = task.task_type
                    document_path = (
                        task.file_metadata.get("file_path")
                        if task.file_metadata
                        else None
                    )
                    log.info(
                        f"Processing task workflow job {job_run_id} for task {job.task_id}: type={task_type}, document={document_path}"
                    )
                    execution_config = task.execution_config

                if task_type not in task_mapper:
                    raise LeapXProcessingException(
                        f"Unknown task type: {task_type}"
                    )  # noqa: TRY301

                result = await task_mapper[task_type](document_path, execution_config)
                if isinstance(result, list) and len(result) > 0:
                    response = result[0]
                    keys = response.get("result").keys()
                    if "data" in keys and not isinstance(
                        response.get("result").get("data"), dict
                    ):
                        result[0]["result"] = {
                            "data": {
                                "Message": "The document doesn't have valid content"
                            }
                        }

                    if (
                        "generation_response" in keys
                        and response.get("result").get("generation_response") == ""
                    ):
                        result[0]["result"][
                            "generation_response"
                        ] = "The document doesn't have valid content"

                if not result:
                    raise LeapXProcessingException(  # noqa: TRY301
                        f"failed to process the result for task type: {task_type}"
                    )
                await job_run_repo.update_task_workflow_run(
                    job_run_id, TaskStatus.COMPLETED, result
                )
                await session.commit()

                log.info(f"job {job.id} completed successfully")
                await self.trigger_webhook(
                    webhook_url,
                    {
                        "integration_id": job_run_id,
                        "status": TaskStatus.COMPLETED,
                        "result": self.parse_result(result, task_type),
                    },
                )

        except Exception as e:
            log.error(f"Error processing job {job_run_id}: {e}")
            try:
                async with AsyncSessionLocal() as session:
                    job_run_repo = TaskWorkFlowJobRunRepository(session)
                    await job_run_repo.update_task_workflow_run(
                        job_run_id, TaskStatus.FAILED, {}, str(e)
                    )
                    job = await job_run_repo.get_task_workflow_run_by_id(job_run_id)
                    await session.commit()
                    await self.trigger_webhook(
                        webhook_url,
                        {
                            "integration_id": job_run_id,
                            "status": TaskStatus.FAILED,
                            "failed_remarks": str(e),
                        },
                    )
            except Exception as update_error:
                log.error(f"Failed to update job run status: {update_error}")

        # Delete the message after processing
        await self.sqs_receiver.delete_message(receipt_handle)

    async def shutdown(self):
        """Gracefully shutdown the worker."""
        log.info("Shutting down worker...")
        self.sqs_receiver.stop_receiving()
        if self.dlq_receiver:
            self.dlq_receiver.stop_receiving()

        # Wait for active tasks with timeout
        if self.active_tasks:
            log.info(
                f"Waiting for {len(self.active_tasks)} active tasks to complete..."
            )
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_tasks, return_exceptions=True),
                    timeout=settings.SHUTDOWN_TIMEOUT,
                )
            except TimeoutError:
                log.warning(
                    f"Shutdown timeout reached. Cancelling {len(self.active_tasks)} remaining tasks."
                )
                for task in self.active_tasks:
                    task.cancel()

        if self.dlq_listener_task:
            self.dlq_listener_task.cancel()
            await asyncio.gather(self.dlq_listener_task, return_exceptions=True)

        log.info("Worker shutdown complete")

    async def health_check(self) -> dict:
        """Return worker health status."""
        return {
            "status": "healthy",
            "worker_id": settings.WORKER_ID,
            "max_concurrent_tasks": settings.MAX_CONCURRENT_TASKS,
            "active_tasks": len(self.active_tasks),
            "available_slots": self.semaphore._value,
        }

    async def trigger_webhook(self, webhook_url: str, payload: dict):
        if webhook_url:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.post(webhook_url, json=payload)
            except Exception as e:
                log.error(f"Webhook delivery failed: {e}")

    def parse_result(self, result: any, workflow_type: str) -> dict:
        results = []
        for item in result:
            if workflow_type == TaskTypes.SUMMARIZATION:
                flattened = {
                    "summary": item.get("result", {}).get("generation_response", {}),
                }
            else:
                data = (item or {}).get("result", {})
                data = (data or {}).get("data", {}) or {
                    "generation": "The system could not find any content"
                }
                pg_no = item.get("pages", {}).get("start", 0) + 1
                flattened = {
                    "pg_no": pg_no,
                    **data,
                }
            results.append(flattened)
        return results
