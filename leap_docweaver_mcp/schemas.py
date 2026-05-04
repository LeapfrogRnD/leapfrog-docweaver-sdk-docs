from typing import Any, NamedTuple

from pydantic import BaseModel

from leap_docweaver_mcp.config import (
    DEFAULT_CLASSIFICATION_ADDITIONAL_INSTRUCTIONS, 
    DEFAULT_EXTRACTION_ADDITIONAL_INSTRUCTIONS, 
    DEFAULT_CLASSIFICATION_FIELD_DEFINITIONS, 
    DEFAULT_EXTRACTION_FIELD_DEFINITIONS)


class BaseToolSchema(BaseModel):
    base64_data: str | None = None
    s3_url: str | None = None
    file_name: str = "upload.pdf"
    llm_model_provider: str | None = None
    llm_model: str | None = None
    ocr_provider: str | None = None
    vlm_model_provider: str | None = None
    vlm_model: str | None = None
    context: Any = None

class ExtractorToolSchema(BaseToolSchema):
    field_definitions: list[dict[str, Any]] = DEFAULT_EXTRACTION_FIELD_DEFINITIONS
    additional_instructions: str = DEFAULT_EXTRACTION_ADDITIONAL_INSTRUCTIONS


class ClassifierToolSchema(BaseToolSchema):
    field_definitions: list[dict[str, Any]] = DEFAULT_CLASSIFICATION_FIELD_DEFINITIONS
    additional_instructions: str = DEFAULT_CLASSIFICATION_ADDITIONAL_INSTRUCTIONS

class SummarizerToolSchema(BaseToolSchema):
    additional_instructions: str | None = None

class WorkflowConfig(NamedTuple):
    name: str
    llm_provider: str
    llm_model: str
    ocr: str
    vlm_provider: str | None
    vlm_model: str | None
