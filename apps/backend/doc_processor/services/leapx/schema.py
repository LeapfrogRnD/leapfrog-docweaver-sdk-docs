from typing import Any

from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    """Model for a single page classification result."""

    pg_no: int = Field(..., description="Page number")
    predicted_class: str = Field(..., description="Predicted class name")
    reasoning: str = Field(..., description="Reasoning for the classification")


class ClassificationMetadata(BaseModel):
    """Model for classification metadata in response."""

    ocr_provider: str = Field(..., description="OCR provider used")
    llm_model: str = Field(..., description="LLM model used")
    parsing_method: str | None = Field(None, description="Parsing method used")


class ClassificationResponse(BaseModel):
    """Response model for classification endpoint."""

    task_type: str = Field("classification", description="Type of task performed (classification)")
    meta_data: ClassificationMetadata = Field(
        ..., description="Metadata about the classification process"
    )
    results: list[ClassificationResult] = Field(..., description="Classification results per page")


class PipelineExecuteResponse(BaseModel):
    """Response model for pipeline execute endpoint."""

    data: dict[str, Any] = Field(..., description="Processed document data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    ocr_text: str = Field(default="", description="Raw OCR text")
    layout: str = Field(default="", description="Document layout information")
    pipeline_stages: list[str] = Field(
        default_factory=lambda: ["ocr", "layout", "extraction"],
        description="Pipeline stages executed",
    )
