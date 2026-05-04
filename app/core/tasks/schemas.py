"""Task schemas for multi-step form."""

import re
from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.core.common.schema import OrmResponseModel, RequestModel
from app.shared.constants.app_constants import TaskStatus, TaskTypes

MAX_FILENAME_LENGTH = 255


class TaskStatsResponse(OrmResponseModel):
    """Task statistics response schema."""

    total: int = Field(..., description="Total number of tasks")
    draft: int = Field(..., description="Number of tasks in draft status")
    ready: int = Field(..., description="Number of tasks in ready status")
    processing: int = Field(..., description="Number of tasks in processing status")
    queued: int = Field(..., description="Number of tasks in queued status")
    completed: int = Field(..., description="Number of tasks in completed status")
    failed: int = Field(..., description="Number of tasks in failed status")


class TaskNameRequest(RequestModel):
    """Step 1: Task name creation/update request schema."""

    task_id: int | None = Field(
        None,
        description="Task ID for update (optional, if not provided will create new task)",
    )
    name: str = Field(..., min_length=1, max_length=255, description="Task name")


class FileMetaData(RequestModel):
    """File metadata schema."""

    file_size: int = Field(..., description="Size of the uploaded file in bytes")
    content_type: str = Field(..., description="MIME type of the uploaded file")


class PresignedUrlRequest(RequestModel):
    """Request schema for generating presigned upload URL."""

    filename: str = Field(
        ...,
        max_length=MAX_FILENAME_LENGTH,
        description="Name of the file to be uploaded",
    )
    file_metadata: FileMetaData | None = Field(
        None, description="Additional metadata for the file"
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename format and characters."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")

        invalid_chars = r'[<>:"|?*\x00-\x1f]'
        if re.search(invalid_chars, v):
            raise ValueError("Filename contains invalid characters")

        if "." not in v or v.startswith(".") or v.endswith("."):
            raise ValueError("Filename must have a valid extension")

        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".tiff"}
        file_extension = v.rsplit(".", 1)[-1].lower()
        if f".{file_extension}" not in allowed_extensions:
            raise ValueError(
                f"Invalid file extension. Only PDF and image files are allowed: "
                f"{', '.join(sorted(allowed_extensions))}"
            )

        return v


class ConfirmDocUploadRequest(RequestModel):
    """Request schema for confirming document upload."""

    file_key: str = Field(..., description="S3 key/path where file was uploaded")


class PresignedUrlResponse(OrmResponseModel):
    """Response schema for presigned upload URL."""

    url: str = Field(..., description="Presigned URL for uploading")
    file_key: str | None = Field(
        None, description="S3 key/path where file will be stored"
    )


class TaskConfigurationRequest(RequestModel):
    """Step 3: Task configuration request schema."""

    additional_instruction: str | None = Field(
        None, description="Additional prompt for the task"
    )
    task_type: str = Field(
        ..., description="Type of task (extraction, classification, both)"
    )
    json_schema: list[dict[str, Any]] | dict[str, Any] = Field(
        ..., description="JSON schema for task output"
    )
    pipeline_id: int = Field(..., description="Pipeline ID to use for this task")
    enable_context: bool = Field(description="Context management control", default=True)
    batch_size: int = Field(
        description="size of batch to process", default=1
    )  # TODO update frontend and other accoirdngly

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        valid_types = [
            TaskTypes.EXTRACTION,
            TaskTypes.CLASSIFICATION,
            TaskTypes.SUMMARIZATION,
        ]
        if v not in valid_types:
            raise ValueError(
                f"Invalid task type. Must be one of: {', '.join(valid_types)}"
            )
        return v

    @field_validator("json_schema")
    @classmethod
    def validate_json_schema(cls, v: dict[str, Any], info) -> dict[str, Any]:
        """Validate json_schema structure based on task_type."""
        task_type = info.data.get("task_type")
        if task_type == TaskTypes.EXTRACTION:
            cls._validate_extraction_schema(v)
        elif task_type == TaskTypes.CLASSIFICATION:
            cls._validate_classification_schema(v)

        return v

    @classmethod
    def _validate_extraction_schema(cls, schema: dict[str, Any]) -> None:
        """Validate extraction schema structure."""
        # Accept either a dict with an 'extractors' key or a plain list of extractors
        extractors = (
            schema if isinstance(schema, list) else schema.get("extractors", [])
        )

        if not isinstance(extractors, list):
            raise TypeError("'extractors' must be an array or a list schema")

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
        # Accept either a dict with a 'classifiers' key or a plain list of classifiers

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


class TaskResponse(OrmResponseModel):
    """Task response schema."""

    id: int = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: TaskStatus | None = Field(
        None, description="Current task status"
    )  # remove if not required #TODO pramesh
    additional_instruction: str | None = Field(None, description="Additional prompt")
    task_type: str | None = Field(None, description="Task type")
    file_key: str | None = Field(None, description="File path")
    json_schema: dict[str, Any] | list[dict[str, Any]] | None = Field(
        None, description="JSON schema"
    )
    pipeline_id: int | None = Field(None, description="Associated pipeline ID")
    created_by: int | None = Field(None, description="Creator user ID")
    created_at: datetime = Field(..., description="Creation timestamp")


class TaskListResponse(OrmResponseModel):
    """Task list item response schema."""

    id: int = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: TaskStatus | None = Field(None, description="Current task status")
    task_type: str | None = Field(None, description="Task type")
    task_rank: int | None = Field(
        None, description="Task rank for ordering in pipeline"
    )
    created_by: int | None = Field(None, description="Creator user ID")
    created_by_fullname: str | None = Field(None, description="Creator name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(None, description="Last update timestamp")


class TaskListFilterParams(RequestModel):
    """Filter parameters for task list."""

    status: TaskStatus | None = Field(None, description="Filter by task status")
    search: str | None = Field(None, description="Filter by task name")


class TaskDetailResponse(OrmResponseModel):
    """Task detail response schema with presigned URL for document preview."""

    id: int = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: TaskStatus | None = Field(None, description="Current task status")
    additional_instruction: str | None = Field(None, description="System prompt")
    task_type: str | None = Field(None, description="Task type")
    task_rank: int | None = Field(
        None, description="Task rank for ordering in pipeline"
    )
    file_key: str | None = Field(None, description="File path")
    file_metadata: dict | None = Field(None, description="File metadata")
    json_schema: list | dict[str, Any] | dict[str, Any] | None = Field(
        None, description="JSON schema"
    )
    pipeline_id: int | None = Field(None, description="Associated pipeline ID")
    pipeline_name: str | None = Field(None, description="Pipeline name")
    document_preview_url: str | None = Field(
        None, description="Presigned URL to preview document"
    )
    failed_remarks: str | None = Field(
        None, description="Remarks in case of task failure"
    )
    created_by: int | None = Field(None, description="Creator user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    enable_context: bool = Field(True, description="enable context")
    file_status: str | None = Field(None, description="file upload status")


class TaskResultResponse(OrmResponseModel):
    """Task result response schema with presigned URL for document preview."""

    id: int = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    task_type: str | None = Field(None, description="Task type")
    status: TaskStatus | None = Field(None, description="Current task status")
    file_metadata: dict | None = Field(None, description="File metadata")
    document_preview_url: str | None = Field(
        None, description="Presigned URL to preview document"
    )
    result: list[dict[str, Any]] | None = Field(None, description="Task result data")
    updated_at: datetime | None = Field(None, description="last updated")


class TaskExecuteResponse(OrmResponseModel):
    """Task execution response schema."""

    processing: int = Field(
        ..., description="Number of tasks currently being processed"
    )
    queued: int | None = Field(None, description="Number of tasks currently queued")
