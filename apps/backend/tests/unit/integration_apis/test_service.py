"""Unit tests for Integration APIs service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.integration_apis.schemas import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.core.integration_apis.service import IntegrationService
from app.shared.constants.app_constants import TaskStatus, TaskTypes
from app.shared.exceptions.common import (
    ForbiddenException,
    NotFoundException,
)


@pytest.fixture
def mock_repositories():
    """Mock all repositories."""
    return {
        "integration_repo": AsyncMock(),
        "workflow_repo": AsyncMock(),
        "job_repo": AsyncMock(),
        "job_run_repo": AsyncMock(),
    }


@pytest.fixture
def mock_storage():
    """Mock storage interface."""
    storage = AsyncMock()
    storage.upload = AsyncMock()
    return storage


@pytest.fixture
def mock_queue():
    """Mock queue provider."""
    queue = AsyncMock()
    queue.send_message = AsyncMock()
    return queue


@pytest.fixture
def mock_settings():
    """Mock settings."""
    settings = MagicMock()
    settings.aws_s3_bucket_name = "test-bucket"
    return settings


@pytest.fixture
def service(mock_repositories, mock_storage, mock_queue, mock_settings):
    """Create service instance with mocked dependencies."""
    return IntegrationService(
        repository=mock_repositories["integration_repo"],
        api_workflow_repository=mock_repositories["workflow_repo"],
        api_workflow_job_repository=mock_repositories["job_repo"],
        task_workflow_job_runs_repository=mock_repositories["job_run_repo"],
        settings=mock_settings,
        storage=mock_storage,
        queue_provider=mock_queue,
    )


class TestIntegrationServiceCreate:
    """Test create_integration method."""

    async def test_create_integration_with_file_upload(
        self,
        service,
        mock_repositories,
        mock_storage,
        mock_queue,
        mock_api_key_secret,
        mock_api_workflow,
        mock_api_workflow_job,
        mock_task_workflow_job_run,
        mock_upload_file,
    ):
        """Test 1: Create integration with file upload."""
        # Setup mocks
        mock_api_workflow.api_key_id = 1
        mock_repositories["workflow_repo"].get_api_workflow_by_name = AsyncMock(
            return_value=mock_api_workflow
        )
        mock_repositories["job_repo"].create_api_workflow_job = AsyncMock(
            return_value=mock_api_workflow_job
        )
        mock_repositories["job_run_repo"].create_task_workflow_job_run = AsyncMock(
            return_value=mock_task_workflow_job_run
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)
        mock_repositories["integration_repo"].session.commit = AsyncMock()

        request = IntegrationRequest(
            workflow_name="test_workflow",
            file=mock_upload_file,
        )

        result = await service.create_integration(request, mock_api_key_secret)

        assert isinstance(result, IntegrationResponse)
        assert result.status == TaskStatus.QUEUED
        mock_storage.upload.assert_called_once()
        mock_queue.send_message.assert_called_once()

    async def test_create_integration_with_s3_uri(
        self,
        service,
        mock_repositories,
        mock_queue,
        mock_api_key_secret,
        mock_api_workflow,
        mock_api_workflow_job,
        mock_task_workflow_job_run,
    ):
        """Test 2: Create integration with S3 URI."""
        mock_api_workflow.api_key_id = 1
        mock_repositories["workflow_repo"].get_api_workflow_by_name = AsyncMock(
            return_value=mock_api_workflow
        )
        mock_repositories["job_repo"].create_api_workflow_job = AsyncMock(
            return_value=mock_api_workflow_job
        )
        mock_repositories["job_run_repo"].create_task_workflow_job_run = AsyncMock(
            return_value=mock_task_workflow_job_run
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)
        mock_repositories["integration_repo"].session.commit = AsyncMock()

        request = IntegrationRequest(
            workflow_name="test_workflow",
            s3_file_uri="s3://test-bucket/test.pdf",
        )

        result = await service.create_integration(request, mock_api_key_secret)

        assert isinstance(result, IntegrationResponse)
        assert result.status == TaskStatus.QUEUED
        mock_queue.send_message.assert_called_once()

    async def test_create_integration_wrong_api_key(
        self, service, mock_repositories, mock_api_key_secret, mock_api_workflow
    ):
        """Test 3: Wrong API key for workflow raises ForbiddenException."""
        mock_api_workflow.api_key_id = 999  # Different from api_key_secret.api_key_id (1)
        mock_repositories["workflow_repo"].get_api_workflow_by_name = AsyncMock(
            return_value=mock_api_workflow
        )

        request = IntegrationRequest(
            workflow_name="test_workflow",
            s3_file_uri="s3://test-bucket/test.pdf",
        )

        with pytest.raises(ForbiddenException) as exc_info:
            await service.create_integration(request, mock_api_key_secret)
        assert "does not have access" in str(exc_info.value)

    async def test_create_integration_deleted_api_key(
        self, service, mock_repositories, mock_api_key_secret, mock_api_workflow
    ):
        """Test 4: Deleted API key raises ForbiddenException."""
        mock_api_workflow.api_key_id = 1
        mock_deleted_key = MagicMock()
        mock_deleted_key.deleted_at = datetime.now()
        mock_api_workflow.api_key = mock_deleted_key

        mock_repositories["workflow_repo"].get_api_workflow_by_name = AsyncMock(
            return_value=mock_api_workflow
        )

        request = IntegrationRequest(
            workflow_name="test_workflow",
            s3_file_uri="s3://test-bucket/test.pdf",
        )

        with pytest.raises(ForbiddenException) as exc_info:
            await service.create_integration(request, mock_api_key_secret)
        assert "has been deleted" in str(exc_info.value)

    async def test_create_integration_workflow_not_found(
        self, service, mock_repositories, mock_api_key_secret
    ):
        """Test 5: Workflow not found raises NotFoundException."""
        mock_repositories["workflow_repo"].get_api_workflow_by_name = AsyncMock(
            side_effect=NotFoundException("API workflow not found")
        )

        request = IntegrationRequest(
            workflow_name="nonexistent_workflow",
            s3_file_uri="s3://test-bucket/test.pdf",
        )

        with pytest.raises(NotFoundException):
            await service.create_integration(request, mock_api_key_secret)

    async def test_create_integration_queue_not_initialized(
        self,
        mock_repositories,
        mock_storage,
        mock_settings,
        mock_api_key_secret,
        mock_api_workflow,
        mock_api_workflow_job,
        mock_task_workflow_job_run,
    ):
        """Test 6: Queue provider not initialized raises ValueError."""
        service = IntegrationService(
            repository=mock_repositories["integration_repo"],
            api_workflow_repository=mock_repositories["workflow_repo"],
            api_workflow_job_repository=mock_repositories["job_repo"],
            task_workflow_job_runs_repository=mock_repositories["job_run_repo"],
            settings=mock_settings,
            storage=mock_storage,
            queue_provider=None,  # Not initialized
        )

        mock_api_workflow.api_key_id = 1
        mock_repositories["workflow_repo"].get_api_workflow_by_name = AsyncMock(
            return_value=mock_api_workflow
        )
        mock_repositories["job_repo"].create_api_workflow_job = AsyncMock(
            return_value=mock_api_workflow_job
        )
        mock_repositories["job_run_repo"].create_task_workflow_job_run = AsyncMock(
            return_value=mock_task_workflow_job_run
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)

        request = IntegrationRequest(
            workflow_name="test_workflow",
            s3_file_uri="s3://test-bucket/test.pdf",
        )

        with pytest.raises(ValueError) as exc_info:
            await service.create_integration(request, mock_api_key_secret)
        assert "queue provider not initialized" in str(exc_info.value)


class TestIntegrationServicePoll:
    """Test poll_integration_task method."""

    async def test_poll_queued_status(self, service, mock_repositories, mock_api_key_secret):
        """Test 8: Poll integration with QUEUED status."""
        mock_workflow = MagicMock()
        mock_workflow.api_key_id = 1
        mock_workflow.workflow_type = TaskTypes.EXTRACTION

        mock_job = MagicMock()
        mock_job.api_job_id = "test123"
        mock_job.api_workflow = mock_workflow

        mock_run = MagicMock()
        mock_run.status = TaskStatus.QUEUED
        mock_run.result = None
        mock_run.failed_remarks = None
        mock_run.created_at = datetime.now()

        mock_job.api_workflow_job_runs = [mock_run]

        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            return_value=mock_job
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=5)

        result = await service.poll_integration_task("test123", mock_api_key_secret)

        assert result.status == TaskStatus.QUEUED
        assert result.result is None

    async def test_poll_completed_extraction_status(
        self, service, mock_repositories, mock_api_key_secret
    ):
        """Test 9: Poll completed extraction with results."""
        mock_workflow = MagicMock()
        mock_workflow.api_key_id = 1
        mock_workflow.workflow_type = TaskTypes.EXTRACTION

        mock_job = MagicMock()
        mock_job.api_job_id = "test123"
        mock_job.api_workflow = mock_workflow

        mock_run = MagicMock()
        mock_run.status = TaskStatus.COMPLETED
        mock_run.job_rank = 1
        mock_run.result = [
            {
                "pages": {"start": 0, "end": 0},
                "result": {"data": {"invoice_number": "INV-001", "amount": 100.50}},
            },
            {
                "pages": {"start": 1, "end": 1},
                "result": {"data": {"invoice_number": "INV-002", "amount": 200.75}},
            },
        ]
        mock_run.failed_remarks = None
        mock_run.created_at = datetime.now()

        mock_job.api_workflow_job_runs = [mock_run]

        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            return_value=mock_job
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)

        result = await service.poll_integration_task("test123", mock_api_key_secret)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert len(result.result) == 2
        assert result.result[0]["pg_no"] == 1
        assert result.result[0]["invoice_number"] == "INV-001"
        assert result.result[1]["pg_no"] == 2

    async def test_poll_completed_summarization_status(
        self, service, mock_repositories, mock_api_key_secret
    ):
        """Test 10: Poll completed summarization with results."""
        mock_workflow = MagicMock()
        mock_workflow.api_key_id = 1
        mock_workflow.workflow_type = TaskTypes.SUMMARIZATION

        mock_job = MagicMock()
        mock_job.api_job_id = "test123"
        mock_job.api_workflow = mock_workflow

        mock_run = MagicMock()
        mock_run.status = TaskStatus.COMPLETED
        mock_run.job_rank = 1
        mock_run.result = [
            {"result": {"generation_response": "This is a summary of the document."}}
        ]
        mock_run.failed_remarks = None
        mock_run.created_at = datetime.now()

        mock_job.api_workflow_job_runs = [mock_run]

        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            return_value=mock_job
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)

        result = await service.poll_integration_task("test123", mock_api_key_secret)

        assert result.status == TaskStatus.COMPLETED
        assert result.result is not None
        assert len(result.result) == 1
        assert "summary" in result.result[0]
        assert result.result[0]["summary"] == "This is a summary of the document."

    async def test_poll_failed_status(self, service, mock_repositories, mock_api_key_secret):
        """Test 11: Poll failed integration returns failed_remarks."""
        mock_workflow = MagicMock()
        mock_workflow.api_key_id = 1
        mock_workflow.workflow_type = TaskTypes.EXTRACTION

        mock_job = MagicMock()
        mock_job.api_job_id = "test123"
        mock_job.api_workflow = mock_workflow

        mock_run = MagicMock()
        mock_run.status = TaskStatus.FAILED
        mock_run.job_rank = 1
        mock_run.result = None
        mock_run.failed_remarks = "File processing error"
        mock_run.created_at = datetime.now()

        mock_job.api_workflow_job_runs = [mock_run]

        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            return_value=mock_job
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)

        result = await service.poll_integration_task("test123", mock_api_key_secret)

        assert result.status == TaskStatus.FAILED
        assert result.failed_remarks == "File processing error"

    async def test_poll_no_job_runs(self, service, mock_repositories, mock_api_key_secret):
        """Test 12: Poll with no job runs returns None status."""
        mock_workflow = MagicMock()
        mock_workflow.api_key_id = 1
        mock_workflow.workflow_type = TaskTypes.EXTRACTION

        mock_job = MagicMock()
        mock_job.api_job_id = "test123"
        mock_job.api_workflow = mock_workflow
        mock_job.api_workflow_job_runs = []  # No runs

        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            return_value=mock_job
        )
        mock_repositories["job_run_repo"].get_in_progress_tasks_count = AsyncMock(return_value=0)

        result = await service.poll_integration_task("test123", mock_api_key_secret)

        assert result.status is None
        assert result.result is None

    async def test_poll_wrong_api_key(self, service, mock_repositories, mock_api_key_secret):
        """Test 13: Poll with wrong API key raises Forbidden Exception."""
        mock_workflow = MagicMock()
        mock_workflow.api_key_id = 999  # Different from api_key_secret.api_key_id (1)

        mock_job = MagicMock()
        mock_job.api_job_id = "test123"
        mock_job.api_workflow = mock_workflow

        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            return_value=mock_job
        )

        with pytest.raises(ForbiddenException) as exc_info:
            await service.poll_integration_task("test123", mock_api_key_secret)
        assert "Unauthorized access" in str(exc_info.value)

    async def test_poll_job_not_found(self, service, mock_repositories, mock_api_key_secret):
        """Test 14: Poll non-existent job raises NotFoundException."""
        mock_repositories["job_repo"].get_api_workflow_job_by_api_job_id = AsyncMock(
            side_effect=NotFoundException("Job not found")
        )

        with pytest.raises(NotFoundException):
            await service.poll_integration_task("nonexistent", mock_api_key_secret)
