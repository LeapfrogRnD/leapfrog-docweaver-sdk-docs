"""Unit tests for API Workflows schemas validation."""

import pytest
from pydantic import ValidationError

from app.core.api_workflows.schemas import (
    ApiWorkFlowCreateRequest,
    ApiWorkFlowUpdateRequest,
)
from app.shared.constants.app_constants import TaskTypes


class TestApiWorkflowSchemaValidation:
    """Test schema validation for API workflows."""

    def test_valid_extraction_schema(self, extraction_schema, pipeline_config):
        """Test 19: Valid extraction schema passes validation."""
        request = ApiWorkFlowCreateRequest(
            name="Test Extraction Workflow",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )
        assert request.name == "Test Extraction Workflow"
        assert request.workflow_type == TaskTypes.EXTRACTION

    def test_valid_classification_schema(self, classification_schema, pipeline_config):
        """Test 16: Valid classification schema passes validation."""
        request = ApiWorkFlowCreateRequest(
            name="Test Classification Workflow",
            workflow_type=TaskTypes.CLASSIFICATION,
            json_schema=classification_schema,
            **pipeline_config,
        )
        assert request.name == "Test Classification Workflow"
        assert request.workflow_type == TaskTypes.CLASSIFICATION

    def test_valid_summarization_schema(self, pipeline_config):
        """Test 17: Valid summarization schema passes validation."""
        request = ApiWorkFlowCreateRequest(
            name="Test Summarization Workflow",
            workflow_type=TaskTypes.SUMMARIZATION,
            json_schema={},
            **pipeline_config,
        )
        assert request.name == "Test Summarization Workflow"
        assert request.workflow_type == TaskTypes.SUMMARIZATION

    def test_invalid_workflow_type(self, extraction_schema, pipeline_config):
        """Test 19: Invalid workflow_type raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type="invalid_type",
                json_schema=extraction_schema,
                **pipeline_config,
            )
        assert "Invalid workflow type" in str(exc_info.value)

    def test_extraction_empty_extractors_array(self, pipeline_config):
        """Test 21: Empty extractors array fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type=TaskTypes.EXTRACTION,
                json_schema=[],
                **pipeline_config,
            )
        assert "cannot be empty" in str(exc_info.value)

    def test_extraction_extractor_missing_required_keys(self, pipeline_config):
        """Test 22: Extractor missing required keys fails validation."""
        invalid_schemas = [
            [{"name": "test"}],
        ]

        for schema in invalid_schemas:
            with pytest.raises(ValidationError) as exc_info:
                ApiWorkFlowCreateRequest(
                    name="Test Workflow",
                    workflow_type=TaskTypes.EXTRACTION,
                    json_schema=schema,
                    **pipeline_config,
                )
            assert "missing required keys" in str(exc_info.value)

    def test_extraction_extractor_not_object(self, pipeline_config):
        """Test edge case: Extractor is not an object."""
        with pytest.raises((ValidationError, TypeError)) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type=TaskTypes.EXTRACTION,
                json_schema=["not_an_object"],
                **pipeline_config,
            )
        assert any("valid dictionary" in err["msg"] for err in exc_info.value.errors())

    def test_classification_empty_classifiers_array(self, pipeline_config):
        """Test edge case: Empty classifiers array fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type=TaskTypes.CLASSIFICATION,
                json_schema=[],
                **pipeline_config,
            )
        assert "cannot be empty" in str(exc_info.value)

    def test_classification_classifier_missing_category(self, pipeline_config):
        """Test 24: Classifier missing 'category' field fails."""
        with pytest.raises(ValidationError) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type=TaskTypes.CLASSIFICATION,
                json_schema=[
                    {
                        "fields": [
                            {
                                "name": "invoice",
                                "title": "Invoice",
                                "description": "Invoice doc",
                                "example": "Example",
                            }
                        ]
                    }
                ],
                **pipeline_config,
            )
        assert "missing 'category' field" in str(exc_info.value)

    def test_classification_classifier_missing_fields(self, pipeline_config):
        """Test 24: Classifier missing 'fields' array fails."""
        with pytest.raises(ValidationError) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type=TaskTypes.CLASSIFICATION,
                json_schema=[{"category": "document_type"}],
                **pipeline_config,
            )
        assert "missing 'fields' array" in str(exc_info.value)

    def test_classification_field_missing_required_keys(self, pipeline_config):
        """Test 26: Classifier field missing required keys fails."""
        invalid_field_schemas = [
            [
                {
                    "category": "document_type",
                    "fields": [
                        {
                            "title": "Invoice",
                            "description": "Invoice doc",
                        }
                    ],
                }
            ]
        ]

        for schema in invalid_field_schemas:
            with pytest.raises(ValidationError) as exc_info:
                ApiWorkFlowCreateRequest(
                    name="Test Workflow",
                    workflow_type=TaskTypes.CLASSIFICATION,
                    json_schema=schema,
                    **pipeline_config,
                )
            assert "missing required keys" in str(exc_info.value)

    def test_classification_field_not_object(self, pipeline_config):
        """Test edge case: Classifier field is not an object."""
        with pytest.raises((ValidationError, TypeError)) as exc_info:
            ApiWorkFlowCreateRequest(
                name="Test Workflow",
                workflow_type=TaskTypes.CLASSIFICATION,
                json_schema=[[{"category": "document_type", "fields": [{}]}]],
                **pipeline_config,
            )
        assert any("valid dictionary" in err["msg"] for err in exc_info.value.errors())

    def test_update_request_validation(self, extraction_schema, pipeline_config):
        """Test 38: Update request follows same validation rules."""
        # Valid update
        request = ApiWorkFlowUpdateRequest(
            name="Updated Workflow",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )
        assert request.name == "Updated Workflow"

        # Invalid update
        with pytest.raises(ValidationError):
            ApiWorkFlowUpdateRequest(
                name="Updated Workflow",
                workflow_type=TaskTypes.EXTRACTION,
                json_schema=[],  # Empty extractors
                **pipeline_config,
            )

    def test_workflow_name_max_length(self, extraction_schema, pipeline_config):
        """Test edge case: Workflow name max length validation."""
        long_name = "a" * 256  # Exceeds max_length=255
        with pytest.raises(ValidationError) as exc_info:
            ApiWorkFlowCreateRequest(
                name=long_name,
                workflow_type=TaskTypes.EXTRACTION,
                json_schema=extraction_schema,
                **pipeline_config,
            )
        assert "String should have at most 255 characters" in str(exc_info.value)

    def test_additional_instruction_optional(self, extraction_schema, pipeline_config):
        """Test edge case: Additional instruction is optional."""
        request = ApiWorkFlowCreateRequest(
            name="Test Workflow",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            additional_instruction="Custom instructions here",
            **pipeline_config,
        )
        assert request.additional_instruction == "Custom instructions here"

        # Without additional_instruction
        request2 = ApiWorkFlowCreateRequest(
            name="Test Workflow 2",
            workflow_type=TaskTypes.EXTRACTION,
            json_schema=extraction_schema,
            **pipeline_config,
        )
        assert request2.additional_instruction is None
