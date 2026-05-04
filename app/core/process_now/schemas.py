"""Process-now request and response schemas."""

import json
from typing import Any

from fastapi import UploadFile
from pydantic import Field, field_validator, model_validator

from app.core.common.schema import OrmResponseModel, RequestModel
from app.core.pipelines.schemas import BasePipelineRequest
from app.shared.constants.app_constants import TaskTypes

SUPPORTED_TASK_TYPES: list[str] = [
    TaskTypes.EXTRACTION,
    TaskTypes.CLASSIFICATION,
    TaskTypes.SUMMARIZATION,
]


def _validate_extraction_schema(schema: dict[str, Any]) -> None:
    """Validate extraction schema structure."""
    for idx, field in enumerate(schema):
        if not isinstance(field, dict):
            raise ValueError(
                f"Extractor at index {idx} must be an object."
            )  # noqa: TRY004
        missing = [k for k in ("name", "type") if k not in field]
        if missing:
            raise ValueError(
                f"Extractor at index {idx} is missing required keys: {', '.join(missing)}."
            )


def _validate_single_classifier(idx: int, clf: Any) -> None:
    """Validate a single classifier entry."""
    if not isinstance(clf, dict):
        raise ValueError(f"Classifier at index {idx} must be an object.")
    for required_key in ("category", "fields"):
        if required_key not in clf:
            raise ValueError(
                f"Classifier at index {idx} is missing required key '{required_key}'."
            )
    if not isinstance(clf["fields"], list):
        raise ValueError(f"Classifier at index {idx} 'fields' must be an array.")
    if not clf["fields"]:
        raise ValueError(f"Classifier at index {idx} 'fields' array cannot be empty.")
    for f_idx, f in enumerate(clf["fields"]):
        if not isinstance(f, dict) or "name" not in f:
            raise ValueError(
                f"Classifier {idx}, field {f_idx} must be an object with a 'name' key."
            )


def _validate_classification_schema(schema: dict[str, Any] | list) -> None:
    """Validate classification schema structure.

    Accepts either:
    - A top-level list: [{"category": "...", "fields": [...]}, ...]
    - A dict with a 'classifiers' key: {"classifiers": [...]}
    """
    # Normalise: unwrap dict wrapper if present
    if isinstance(schema, dict):
        if "classifiers" not in schema:
            raise ValueError(
                "Classification schema must contain a 'classifiers' array."
            )
        classifiers = schema["classifiers"]
    else:
        classifiers = schema

    if not isinstance(classifiers, list):
        raise ValueError("'classifiers' must be an array.")  # noqa: TRY004
    if not classifiers:
        raise ValueError("'classifiers' array cannot be empty.")
    for idx, clf in enumerate(classifiers):
        _validate_single_classifier(idx, clf)


def _validate_summarization_schema(schema: dict[str, Any]) -> None:
    """
    Summarization accepts either an empty dict (free-form summary) or a dict
    with an optional 'fields' key listing the aspects to summarise.
    """
    if not isinstance(schema, dict):
        raise ValueError("Summarization schema must be a JSON object.")  # noqa: TRY004
    if "fields" in schema:
        if not isinstance(schema["fields"], list):
            raise ValueError("Summarization 'fields' must be an array.")
        for idx, item in enumerate(schema["fields"]):
            if not isinstance(item, str) or not item.strip():
                raise ValueError(
                    f"Summarization field at index {idx} must be a non-empty string."
                )


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ProcessNowPipelineConfig(BasePipelineRequest):
    """Inline pipeline config sent directly in the request body."""


class ProcessNowRequest(RequestModel):
    """
    Multipart form request for synchronous document processing.

    Exactly **one** of `pipeline_id` (reference an existing saved pipeline) or
    `pipeline_config` (an inline ad-hoc pipeline definition) must be supplied.
    """

    task_type: str = Field(
        ...,
        description=f"Type of processing task. One of: {', '.join(SUPPORTED_TASK_TYPES)}.",
    )
    json_schema: dict[str, Any] | list[dict[str, Any]] | None = Field(
        ...,
        description=(
            "Output schema driving the LLM. "
            "Must match the structure required by task_type "
            "(extraction → 'extractors', classification → 'classifiers', "
            "summarization → {} or {'fields': [...]})."
        ),
    )
    additional_instructions: str | None = Field(
        None,
        max_length=4096,
        description="Optional extra instruction appended to the system prompt.",
    )

    pipeline_id: int | None = Field(
        1,
        description="ID of a saved pipeline to use. Mutually exclusive with pipeline_config.",
        gt=0,
    )
    pipeline_config: ProcessNowPipelineConfig | None = Field(
        None,
        description="Inline pipeline config. Mutually exclusive with pipeline_id.",
    )

    file: UploadFile | None = Field(None, exclude=True)

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        if v not in SUPPORTED_TASK_TYPES:
            raise ValueError(
                f"Invalid task_type '{v}'. Must be one of: {', '.join(SUPPORTED_TASK_TYPES)}."
            )
        return v

    @field_validator("json_schema", mode="before")
    @classmethod
    def coerce_json_schema(cls, v: Any) -> dict[str, Any]:
        """Accept either a dict or a raw JSON string (handy for multipart forms)."""
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError as exc:
                raise ValueError(f"json_schema is not valid JSON: {exc}") from exc
        if not isinstance(v, dict) and not isinstance(v, list):
            raise ValueError("json_schema must be a JSON object.")  # noqa: TRY004
        return v

    @model_validator(mode="after")
    def validate_schema_matches_task_type(self) -> "ProcessNowRequest":
        """Cross-field: validate schema structure against task_type."""
        if self.task_type == TaskTypes.EXTRACTION:
            _validate_extraction_schema(self.json_schema)
        elif self.task_type == TaskTypes.CLASSIFICATION:
            _validate_classification_schema(self.json_schema)
        elif self.task_type == TaskTypes.SUMMARIZATION:
            _validate_summarization_schema(self.json_schema)
        return self

    @model_validator(mode="after")
    def validate_pipeline_source(self) -> "ProcessNowRequest":
        """Exactly one of pipeline_id / pipeline_config must be set."""
        has_id = self.pipeline_id is not None
        has_cfg = self.pipeline_config is not None
        if has_id and has_cfg:
            raise ValueError(
                "Provide either 'pipeline_id' or 'pipeline_config', not both."
            )
        if not has_id and not has_cfg:
            raise ValueError("One of 'pipeline_id' or 'pipeline_config' is required.")
        return self

    @field_validator("additional_instructions")
    @classmethod
    def validate_additional_instruction(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("additional_instruction cannot be blank whitespace.")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ProcessNowPageResult(OrmResponseModel):
    """Result for a single page / chunk."""

    pg_no: int = Field(..., description="1-based page number.")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted or classified data for this page.",
    )


class ProcessNowSummaryResult(OrmResponseModel):
    """Result for a summarisation task."""

    summary: Any = Field(..., description="Generated summary content.")


class ProcessNowResponse(OrmResponseModel):
    """Top-level response for a synchronous process-now call."""

    task_type: str = Field(..., description="Task type that was executed.")
    pipeline_id: int | None = Field(
        None, description="Pipeline ID used (if resolved from DB)."
    )
    results: list[dict[str, Any]] = Field(
        ...,
        description=(
            "Per-page results for extraction/classification; single-element list for summarization."
        ),
    )
    page_count: int = Field(..., description="Total number of pages processed.")
    processing_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime metadata: model used, OCR provider, etc.",
    )
