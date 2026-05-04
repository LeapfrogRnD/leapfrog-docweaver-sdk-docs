"""API workflow schemas."""

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator
from pydantic import BaseModel

from app.core.api_workflows.base import TaskMetadata
from app.core.common.schema import OrmResponseModel
from app.core.pipelines.schemas import BasePipelineRequest
from app.shared.constants.app_constants import TaskTypes
from enum import StrEnum


class BaseApiFlowRequest(BasePipelineRequest):
    """Base request schema for API workflow operations."""

    name: str = Field(
        ...,
        description="Name of the API workflow",
        max_length=255,
        min_length=1,
        example="Invoice Extraction Flow",
    )
    workflow_type: str = Field(
        ...,
        description="Type of the API workflow",
        max_length=100,
        example=TaskTypes.EXTRACTION,
    )
    additional_instruction: str | None = Field(
        None,
        description="Additional instructions for the API workflow",
        example="Extract title, date and total amount from invoices",
    )
    json_schema: dict[str, Any] | list[dict[str, Any]] | None = Field(
        None,
        description="JSON schema defining the integration structure",
        example=[{"name": "title", "type": "text"}],
    )

    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )

    @field_validator("workflow_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        valid_types = [
            TaskTypes.EXTRACTION,
            TaskTypes.CLASSIFICATION,
            TaskTypes.SUMMARIZATION,
        ]
        if v not in valid_types:
            raise ValueError(
                f"Invalid workflow type. Must be one of: {', '.join(valid_types)}"
            )
        return v

    @field_validator("json_schema")
    @classmethod
    def validate_json_schema(cls, v: Any, info) -> Any:
        """Validate json_schema structure based on workflow_type.

        For extraction workflows we accept either:
        - a dict containing an "extractors" key with a list of extractor objects
        - a legacy list of extractor objects directly
        """
        if v is None:
            return v
        task_type = info.data.get("workflow_type")
        if task_type == TaskTypes.EXTRACTION:
            cls._validate_extraction_schema(v)
        elif task_type == TaskTypes.CLASSIFICATION:
            cls._validate_classification_schema(v)

        return v

    @classmethod
    def _validate_extraction_schema(cls, schema: Any) -> None:
        """Validate extraction schema structure.

        Accept either a dict with 'extractors' key or a list of extractor dicts.
        """
        # If a list is provided (legacy format), treat it as the extractors list
        if isinstance(schema, list):
            extractors = schema
        elif isinstance(schema, dict):
            extractors = schema["extractors"]
        else:
            raise TypeError(
                "Extraction json_schema must be an object containing 'extractors' or an array of extractor objects"
            )

        if not isinstance(extractors, list):
            raise TypeError("'extractors' must be an array")

        if not extractors:
            raise ValueError("'extractors' array cannot be empty")

        for idx, field in enumerate(extractors):
            if not isinstance(field, dict):
                raise TypeError(f"Field at index {idx} must be an object")

            required_keys = ["name", "type"]
            missing_keys = [key for key in required_keys if key not in field]
            if missing_keys:
                raise ValueError(
                    f"Field at index {idx} is missing required keys: {', '.join(missing_keys)}"
                )

    @classmethod
    def _validate_classification_schema(cls, schema: dict[str, Any]) -> None:
        """Validate classification schema structure."""
        if not schema:
            raise ValueError("array cannot be empty")

        for idx, classifier in enumerate(schema):
            if not isinstance(classifier, dict):
                raise TypeError(f"Classifier at index {idx} must be an object")

            if "category" not in classifier:
                raise ValueError(
                    f"Classifier at index {idx} is missing 'category' field"
                )

            if "fields" not in classifier:
                raise ValueError(f"Classifier at index {idx} is missing 'fields' array")

            if not isinstance(classifier["fields"], list):
                raise TypeError(f"Classifier at index {idx} 'fields' must be an array")

            if not classifier["fields"]:
                raise ValueError(
                    f"Classifier at index {idx} 'fields' array cannot be empty"
                )

            cls._validate_classifier_fields(classifier["fields"], idx)

    @classmethod
    def _validate_classifier_fields(cls, fields: list, classifier_idx: int) -> None:
        """Validate fields within a classifier."""
        for field_idx, field in enumerate(fields):
            if not isinstance(field, dict):
                raise TypeError(
                    f"Classifier at index {classifier_idx}, field at index {field_idx} must be an object"
                )

            required_keys = ["name"]
            missing_keys = [key for key in required_keys if key not in field]
            if missing_keys:
                raise ValueError(
                    f"Classifier at index {classifier_idx}, field at index {field_idx} "
                    f"is missing required keys: {', '.join(missing_keys)}"
                )


class ApiWorkFlowCreateRequest(BaseApiFlowRequest):
    """Request schema for creating an API workflow."""


class ApiWorkFlowUpdateRequest(BaseApiFlowRequest):
    """Request schema for updating an API workflow."""


class WorkflowType(StrEnum):
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"


class ApiWorkFlowResponse(OrmResponseModel):
    """API workflow response schema."""

    id: int = Field(..., description="API workflow ID", example=1)
    name: str = Field(
        ..., description="Name of the API workflow", example="Invoice Extraction Flow"
    )
    workflow_type: WorkflowType = Field(
        ..., description="Type of the API workflow", example=WorkflowType.EXTRACTION
    )
    pipeline_config: dict = Field(
        ...,
        description="Workflow configuration",
        example={"pipeline": [{"name": "ingest", "type": "extractor"}]},
    )
    additional_instruction: str | None = Field(
        None,
        description="Additional instructions for the API workflow",
        example="Extract title, date and total amount from invoices",
    )
    json_schema: list[dict[str, Any]] | dict[str, Any] | None = Field(
        None,
        description="JSON schema for the workflow",
        example=[{"name": "title", "type": "text"}],
    )
    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )
    created_at: datetime = Field(
        ..., description="Workflow creation timestamp", example="2026-03-19T12:34:56Z"
    )


class ApiWorkFlowListResponse(OrmResponseModel):
    """API workflow list response schema."""

    id: int = Field(..., description="API workflow ID", example=1)
    name: str = Field(
        ..., description="Name of the API workflow", example="Invoice Extraction Flow"
    )
    workflow_type: str = Field(
        ..., description="Type of the API workflow", example="extraction"
    )
    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )
    created_at: datetime = Field(
        ..., description="Workflow creation timestamp", example="2026-03-19T12:34:56Z"
    )
