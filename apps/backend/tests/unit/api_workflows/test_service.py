"""Unit tests for API Workflows service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.api_workflows.schemas import (
    ApiWorkFlowCreateRequest,
    ApiWorkFlowResponse,
    ApiWorkFlowUpdateRequest,
)
from app.core.api_workflows.service import ApiWorkFlowService
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.shared.constants.app_constants import TaskTypes
from app.shared.exceptions.common import BadRequestException, NotFoundException


@pytest.fixture
def mock_repository():
    """Mock ApiWorkflowsRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    """Create service instance with mocked repository."""
    return ApiWorkFlowService(repository=mock_repository)


class TestApiWorkflowServiceCreate:
    """Test create_api_workflow method."""

    async def test_create_extraction_workflow_success(
        self, service, mock_repository, extraction_schema, pipeline_config
    ):
        """Test 15: Successfully create extraction workflow."""
        mock_repository.check_workflow_name_exists = AsyncMock()
        mock_workflow = MagicMock()
        mock_workflow.id = 1
        mock_workflow.name = "Test Extraction"
        mock_workflow.workflow_type = TaskTypes.EXTRACTION
        mock_workflow.pipeline_config = {}
        mock_workflow.json_schema = extraction_schema
        mock_workflow.additional_instruction = None
        mock_workflow.created_at = datetime.now()
        mock_repository.create_api_workflow = AsyncMock(return_value=mock_workflow)

        request = ApiWorkFlowCreateRequest(
            name="Test Extraction",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )

        result = await service.create_api_workflow(request, api_key_id=1)

        assert isinstance(result, ApiWorkFlowResponse)
        assert result.name == "Test Extraction"
        mock_repository.check_workflow_name_exists.assert_called_once()
        mock_repository.create_api_workflow.assert_called_once()

    async def test_create_classification_workflow_success(
        self, service, mock_repository, classification_schema, pipeline_config
    ):
        """Test 16: Successfully create classification workflow."""
        mock_repository.check_workflow_name_exists = AsyncMock()
        mock_workflow = MagicMock()
        mock_workflow.id = 2
        mock_workflow.name = "Test Classification"
        mock_workflow.workflow_type = TaskTypes.CLASSIFICATION
        mock_workflow.pipeline_config = {}
        mock_workflow.json_schema = classification_schema
        mock_workflow.additional_instruction = None
        mock_workflow.created_at = datetime.now()
        mock_repository.create_api_workflow = AsyncMock(return_value=mock_workflow)

        request = ApiWorkFlowCreateRequest(
            name="Test Classification",
            workflow_type=TaskTypes.CLASSIFICATION,
            json_schema=classification_schema,
            **pipeline_config,
        )

        result = await service.create_api_workflow(request, api_key_id=1)

        assert result.workflow_type == TaskTypes.CLASSIFICATION
        mock_repository.create_api_workflow.assert_called_once()

    async def test_create_summarization_workflow_success(
        self, service, mock_repository, summarization_schema, pipeline_config
    ):
        """Test 17: Successfully create summarization workflow."""
        mock_repository.check_workflow_name_exists = AsyncMock()
        mock_workflow = MagicMock()
        mock_workflow.id = 3
        mock_workflow.name = "Test Summarization"
        mock_workflow.workflow_type = TaskTypes.SUMMARIZATION
        mock_workflow.pipeline_config = {}
        mock_workflow.json_schema = summarization_schema
        mock_workflow.additional_instruction = None
        mock_workflow.created_at = datetime.now()
        mock_repository.create_api_workflow = AsyncMock(return_value=mock_workflow)

        request = ApiWorkFlowCreateRequest(
            name="Test Summarization",
            workflow_type=TaskTypes.SUMMARIZATION,
            json_schema=summarization_schema,
            **pipeline_config,
        )

        result = await service.create_api_workflow(request, api_key_id=1)

        assert result.workflow_type == TaskTypes.SUMMARIZATION

    async def test_create_workflow_duplicate_name(
        self, service, mock_repository, extraction_schema, pipeline_config
    ):
        """Test 18: Creating workflow with duplicate name raises BadRequestException."""
        mock_repository.check_workflow_name_exists = AsyncMock(
            side_effect=BadRequestException("An API workflow with this name already exists")
        )

        request = ApiWorkFlowCreateRequest(
            name="Duplicate Name",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )

        with pytest.raises(BadRequestException) as exc_info:
            await service.create_api_workflow(request, api_key_id=1)
        assert "already exists" in str(exc_info.value)


class TestApiWorkflowServiceGet:
    """Test get methods."""

    async def test_get_all_workflows_success(self, service, mock_repository):
        """Test 27: Get all workflows with pagination."""
        mock_workflow_1 = MagicMock()
        mock_workflow_1.id = 1
        mock_workflow_1.name = "Workflow 1"
        mock_workflow_1.workflow_type = TaskTypes.EXTRACTION
        mock_workflow_1.created_at = datetime.now()

        mock_workflow_2 = MagicMock()
        mock_workflow_2.id = 2
        mock_workflow_2.name = "Workflow 2"
        mock_workflow_2.workflow_type = TaskTypes.CLASSIFICATION
        mock_workflow_2.created_at = datetime.now()

        mock_workflows = [mock_workflow_1, mock_workflow_2]
        metadata = PaginationMetadata(
            page=1, page_size=10, total_items=2, total_pages=1, has_next=False, has_previous=False
        )
        mock_repository.get_all_api_workflows = AsyncMock(return_value=(mock_workflows, metadata))

        pagination = PaginationParams(page=1, page_size=10)
        result, meta = await service.get_all_api_workflows(api_key_id=1, page_params=pagination)

        assert len(result) == 2
        assert meta.total_items == 2
        mock_repository.get_all_api_workflows.assert_called_once_with(1, pagination)

    async def test_get_all_workflows_empty(self, service, mock_repository):
        """Test 28: Get all workflows returns empty list."""
        metadata = PaginationMetadata(
            page=1, page_size=10, total_items=0, total_pages=0, has_next=False, has_previous=False
        )
        mock_repository.get_all_api_workflows = AsyncMock(return_value=([], metadata))

        pagination = PaginationParams(page=1, page_size=10)
        result, meta = await service.get_all_api_workflows(api_key_id=1, page_params=pagination)

        assert len(result) == 0
        assert meta.total_items == 0

    async def test_get_workflow_by_id_success(self, service, mock_repository):
        """Test 31: Get workflow by ID successfully."""
        mock_workflow = MagicMock()
        mock_workflow.id = 1
        mock_workflow.name = "Test Workflow"
        mock_workflow.workflow_type = TaskTypes.EXTRACTION
        mock_workflow.pipeline_config = {}
        mock_workflow.json_schema = {}
        mock_workflow.additional_instruction = None
        mock_workflow.created_at = datetime.now()
        mock_repository.get_api_workflow_by_id = AsyncMock(return_value=mock_workflow)

        result = await service.get_api_workflow(workflow_id=1, api_key_id=1)

        assert result.id == 1
        assert result.name == "Test Workflow"
        mock_repository.get_api_workflow_by_id.assert_called_once_with(1, 1)

    async def test_get_workflow_not_found(self, service, mock_repository):
        """Test 32: Get workflow that doesn't exist raises NotFoundException."""
        mock_repository.get_api_workflow_by_id = AsyncMock(
            side_effect=NotFoundException("API workflow not found")
        )

        with pytest.raises(NotFoundException) as exc_info:
            await service.get_api_workflow(workflow_id=999, api_key_id=1)
        assert "not found" in str(exc_info.value)


class TestApiWorkflowServiceUpdate:
    """Test update_api_workflow method."""

    async def test_update_workflow_success(
        self, service, mock_repository, extraction_schema, pipeline_config
    ):
        """Test 34: Successfully update workflow."""
        mock_existing = MagicMock()
        mock_existing.id = 1
        mock_repository.get_api_workflow_by_id = AsyncMock(return_value=mock_existing)
        mock_repository.check_workflow_name_exists = AsyncMock()

        mock_updated = MagicMock()
        mock_updated.id = 1
        mock_updated.name = "Updated Name"
        mock_updated.workflow_type = TaskTypes.EXTRACTION
        mock_updated.pipeline_config = {}
        mock_updated.json_schema = extraction_schema
        mock_updated.additional_instruction = None
        mock_updated.created_at = datetime.now()
        mock_repository.update_api_workflow = AsyncMock(return_value=mock_updated)

        request = ApiWorkFlowUpdateRequest(
            name="Updated Name",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )

        result = await service.update_api_workflow(request, workflow_id=1, api_key_id=1)

        assert result.name == "Updated Name"
        mock_repository.update_api_workflow.assert_called_once()

    async def test_update_workflow_name_conflict(
        self, service, mock_repository, extraction_schema, pipeline_config
    ):
        """Test 35: Update with conflicting name raises BadRequestException."""
        mock_existing = MagicMock()
        mock_existing.id = 1
        mock_repository.get_api_workflow_by_id = AsyncMock(return_value=mock_existing)
        mock_repository.check_workflow_name_exists = AsyncMock(
            side_effect=BadRequestException("An API workflow with this name already exists")
        )

        request = ApiWorkFlowUpdateRequest(
            name="Existing Name",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )

        with pytest.raises(BadRequestException):
            await service.update_api_workflow(request, workflow_id=1, api_key_id=1)

    async def test_update_workflow_same_name(
        self, service, mock_repository, extraction_schema, pipeline_config
    ):
        """Test 36: Update with same name (no conflict) succeeds."""
        mock_existing = MagicMock()
        mock_existing.id = 1
        mock_existing.name = "Same Name"
        mock_repository.get_api_workflow_by_id = AsyncMock(return_value=mock_existing)
        mock_repository.check_workflow_name_exists = AsyncMock()  # No exception

        mock_updated = MagicMock()
        mock_updated.id = 1
        mock_updated.name = "Same Name"
        mock_updated.workflow_type = TaskTypes.EXTRACTION
        mock_updated.pipeline_config = {}
        mock_updated.json_schema = extraction_schema
        mock_updated.additional_instruction = None
        mock_updated.created_at = datetime.now()
        mock_repository.update_api_workflow = AsyncMock(return_value=mock_updated)

        request = ApiWorkFlowUpdateRequest(
            name="Same Name",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )

        result = await service.update_api_workflow(request, workflow_id=1, api_key_id=1)
        assert result.name == "Same Name"

    async def test_update_workflow_not_found(
        self, service, mock_repository, extraction_schema, pipeline_config
    ):
        """Test 37: Update non-existent workflow raises NotFoundException."""
        mock_repository.get_api_workflow_by_id = AsyncMock(
            side_effect=NotFoundException("API workflow not found")
        )

        request = ApiWorkFlowUpdateRequest(
            name="Updated Name",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )

        with pytest.raises(NotFoundException):
            await service.update_api_workflow(request, workflow_id=999, api_key_id=1)


class TestApiWorkflowServiceDelete:
    """Test delete_api_workflow method."""

    async def test_delete_workflow_success(self, service, mock_repository):
        """Test 39: Successfully soft delete workflow."""
        mock_workflow = MagicMock()
        mock_workflow.id = 1
        mock_repository.get_api_workflow_by_id = AsyncMock(return_value=mock_workflow)
        mock_repository.delete_api_workflow = AsyncMock()

        await service.delete_api_workflow(workflow_id=1, api_key_id=1)

        mock_repository.delete_api_workflow.assert_called_once_with(1, None)

    async def test_delete_workflow_not_found(self, service, mock_repository):
        """Test 40: Delete non-existent workflow raises NotFoundException."""
        mock_repository.get_api_workflow_by_id = AsyncMock(
            side_effect=NotFoundException("API workflow not found")
        )

        with pytest.raises(NotFoundException):
            await service.delete_api_workflow(workflow_id=999, api_key_id=1)
