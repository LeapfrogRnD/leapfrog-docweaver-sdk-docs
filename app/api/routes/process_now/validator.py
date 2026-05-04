"""
Multipart-form validator for the process-now endpoint.

Responsibilities
----------------
- Parse every form field (task_type, json_schema, pipeline_id / pipeline_config,
  additional_instruction) and the binary file upload.
- Validate file: MIME type, size, PDF page-count.
- Validate business fields via ProcessNowRequest (Pydantic raises HTTPException-
  compatible ValidationError automatically).
- Return a fully-populated (ProcessNowRequest, raw_bytes, filename, content_type)
  tuple so the router stays thin.
"""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import Depends, File, Form, UploadFile
from pypdf import PdfReader

from app.core.process_now.schemas import ProcessNowPipelineConfig, ProcessNowRequest
from app.shared.constants.app_constants import FileConstants
from app.shared.exceptions.common import BadRequestException
from app.shared.exceptions.validation_exceptions import (
    EmptyFileError,
    FileReadError,
    FileSizeExceededError,
    InvalidFileTypeError,
    PageLimitExceededError,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_MIME_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/tiff",
    }
)

_ALLOWED_DISPLAY = "PDF, JPEG, PNG, TIFF"


# ---------------------------------------------------------------------------
# Dependency function
# ---------------------------------------------------------------------------


async def get_validated_process_now_request(
    # --- required form fields ---
    task_type: str = Form(
        ..., description="Task type: extraction | classification | summarization"
    ),
    json_schema: str = Form(
        ...,
        description="JSON string representing the output schema (structure depends on task_type).",
    ),
    file: UploadFile = File(..., description="Binary document to process (PDF or image)."),
    # --- pipeline source: exactly one of the two must be supplied ---
    pipeline_id: int | None = Form(
        None,
        gt=0,
        description="ID of a saved pipeline. Mutually exclusive with pipeline_config.",
    ),
    pipeline_config: str | None = Form(
        None,
        description=(
            "JSON string of an inline pipeline config (BasePipelineRequest fields). "
            "Mutually exclusive with pipeline_id."
        ),
    ),
    # --- optional ---
    additional_instructions: str | None = Form(
        None,
        description="Optional extra system-prompt instruction.",
    ),
) -> tuple[ProcessNowRequest, bytes, str, str]:
    """
    FastAPI dependency that:
    1. Validates the uploaded file (type → size → page count).
    2. Parses and validates all form fields via ProcessNowRequest.
    3. Returns ``(request, file_bytes, filename, content_type)``.
    """

    # ------------------------------------------------------------------
    # 1. File validation
    # ------------------------------------------------------------------
    _validate_file_type(file)
    file_bytes = await _read_and_validate_file_size(file)
    _validate_pdf_page_count(file, file_bytes)

    # ------------------------------------------------------------------
    # 2. Decode pipeline_config JSON string (if provided)
    # ------------------------------------------------------------------
    parsed_pipeline_config: ProcessNowPipelineConfig | None = None
    if pipeline_config is not None:
        parsed_pipeline_config = _parse_pipeline_config(pipeline_config)

    # ------------------------------------------------------------------
    # 3. Decode json_schema JSON string
    # ------------------------------------------------------------------
    parsed_json_schema: dict | list = _parse_json_schema(json_schema)

    # ------------------------------------------------------------------
    # 4. Build and validate the Pydantic request model
    #    (model_validators for cross-field rules fire here)
    # ------------------------------------------------------------------
    try:
        request = ProcessNowRequest(
            task_type=task_type,
            json_schema=parsed_json_schema,
            additional_instructions=additional_instructions or None,
            pipeline_id=pipeline_id,
            pipeline_config=parsed_pipeline_config,
        )
    except Exception as exc:
        # Re-raise Pydantic ValidationError as a Bad Request
        raise BadRequestException(str(exc)) from exc

    filename: str = file.filename or "document.pdf"
    content_type: str = file.content_type or FileConstants.DEFAULT_CONTENT_TYPE

    return request, file_bytes, filename, content_type


# ---------------------------------------------------------------------------
# File validation helpers
# ---------------------------------------------------------------------------


def _validate_file_type(file: UploadFile) -> None:
    """Raise InvalidFileTypeError when the MIME type is not in the allowed set."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise InvalidFileTypeError(
            f"Unsupported file type '{file.content_type}'. Allowed types: {_ALLOWED_DISPLAY}."
        )


async def _read_and_validate_file_size(file: UploadFile) -> bytes:
    """
    Read the entire file into memory and reject it if it exceeds MAX_FILE_SIZE_BYTES.

    Reading first (rather than using seek/tell) works correctly for both
    real spooled uploads and in-memory test fixtures.
    """
    file_bytes = await file.read()

    if not file_bytes:
        raise EmptyFileError()

    if len(file_bytes) > FileConstants.MAX_FILE_SIZE_BYTES:
        raise FileSizeExceededError(FileConstants.MAX_FILE_SIZE_MB)

    # Rewind so downstream code (e.g. PdfReader) can read again
    await file.seek(0)
    return file_bytes


def _validate_pdf_page_count(file: UploadFile, file_bytes: bytes) -> None:
    """Reject PDF files that exceed MAX_PAGES."""
    if file.content_type != "application/pdf":
        return  # images are single-page by definition

    try:
        import io

        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        page_count = len(pdf_reader.pages)
    except Exception as exc:
        raise FileReadError(f"Could not read PDF: {exc}") from exc

    if page_count > FileConstants.MAX_PAGES:
        raise PageLimitExceededError(FileConstants.MAX_PAGES)


# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------


def _parse_json_schema(raw: str) -> dict | list:
    """Parse the json_schema form field; raise BadRequestException on bad JSON."""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BadRequestException(f"'json_schema' is not valid JSON: {exc}") from exc
    if not isinstance(parsed, (dict, list)):
        raise BadRequestException("'json_schema' must be a JSON object or array, not a scalar.")
    return parsed


def _parse_pipeline_config(raw: str) -> ProcessNowPipelineConfig:
    """Parse the pipeline_config form field into a ProcessNowPipelineConfig."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BadRequestException(f"'pipeline_config' is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise BadRequestException("'pipeline_config' must be a JSON object.")
    try:
        return ProcessNowPipelineConfig(**data)
    except Exception as exc:
        raise BadRequestException(f"Invalid pipeline_config: {exc}") from exc


# ---------------------------------------------------------------------------
# Annotated type alias used in the router
# ---------------------------------------------------------------------------

ValidatedProcessNowDep = Annotated[
    tuple[ProcessNowRequest, bytes, str, str],
    Depends(get_validated_process_now_request),
]
