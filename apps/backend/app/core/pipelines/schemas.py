"""Pipeline schemas."""

from datetime import datetime

from pydantic import Field, field_validator

from app.core.api_workflows.base import TaskMetadata
from app.core.common.schema import OrmResponseModel, RequestModel
from app.shared.constants.app_constants import (
    LLM_MODEL_GROUPS,
    VLM_MODEL_GROUPS,
    LLMProviderType,
    OCRProviderType,
    ParsingMethod,
    VLMProviderType,
)


class BasePipelineRequest(RequestModel):
    """Base pipeline request schema with shared validations."""

    ocr_provider: OCRProviderType = Field(
        ..., description="OCR provider", max_length=100
    )
    parsing_method: ParsingMethod | None = Field(
        None, description="Parsing method", max_length=100
    )
    vlm_model_provider: VLMProviderType | None = Field(
        None, description="VLM model provider", max_length=100
    )
    vlm_model: str | None = Field(
        None,
        description="VLM model",
        max_length=100,
        example="bedrock/qwen.qwen3-vl-235b-a22b",
    )
    llm_model_provider: LLMProviderType = Field(
        ..., description="LLM model provider", max_length=100, min_length=1
    )
    llm_model: str = Field(
        ...,
        description="LLM model",
        max_length=100,
        min_length=1,
        example="bedrock/qwen.qwen3-32b-v1:0",
    )
    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )

    @field_validator("parsing_method")
    @classmethod
    def validate_parsing_method(cls, v: str | None) -> str:
        if not v:
            raise ValueError("Parsing method cannot be empty")
        if v and v not in [
            ParsingMethod.LAYOUT_CONSERVED,
        ]:
            raise ValueError(
                f"Invalid parsing method: {v}. Must be one of: "
                f"{ParsingMethod.LAYOUT_CONSERVED}"
            )
        return v

    @field_validator("vlm_model")
    @classmethod
    def validate_vlm_model(cls, v: str | None, info) -> str | None:
        ocr_provider = info.data.get("ocr_provider")
        if ocr_provider == OCRProviderType.VLM.value and not v:
            raise ValueError("vlm_model is required when ocr_provider is vlm")

        vlm_provider = info.data.get("vlm_model_provider")
        if v and vlm_provider:
            provider_enum = VLMProviderType(vlm_provider)
            model_group = VLM_MODEL_GROUPS.get(provider_enum)
            if model_group and v not in [model.value for model in model_group]:
                available_models = [model.value for model in model_group]
                raise ValueError(
                    f"Invalid VLM model: {v} for provider {vlm_provider}. "
                    f"Must be one of: {', '.join(available_models)}"
                )
        return v

    @field_validator("vlm_model_provider")
    @classmethod
    def validate_vlm_model_provider(cls, v: str | None, info) -> str | None:
        ocr_provider = info.data.get("ocr_provider")
        if ocr_provider == OCRProviderType.VLM.value and not v:
            raise ValueError("vlm_model_provider is required when ocr_provider is vlm")
        return v

    @field_validator("llm_model")
    @classmethod
    def validate_llm_model(cls, v: str | None, info) -> str | None:
        llm_provider = info.data.get("llm_model_provider")
        if v and llm_provider:
            provider_enum = LLMProviderType(llm_provider)
            model_group = LLM_MODEL_GROUPS.get(provider_enum)
            if model_group and v not in [model.value for model in model_group]:
                available_models = [model.value for model in model_group]
                raise ValueError(
                    f"Invalid LLM model: {v} for provider {llm_provider}. "
                    f"Must be one of: {', '.join(available_models)}"
                )
        return v

    @field_validator("task_metadata")
    @classmethod
    def validate_batch_size(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if not isinstance(v.batch_size, int) or v.batch_size <= 0:
            raise ValueError("batch_size must be a positive integer")
        return v


class PipelineCreateRequest(BasePipelineRequest):
    name: str = Field(..., description="Pipeline name", max_length=255)
    description: str | None = Field(None, description="Pipeline description")
    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if not v:
            raise ValueError("Pipeline name cannot be empty or whitespace-only")
        return v


class PipelineUpdateRequest(BasePipelineRequest):
    name: str = Field(..., description="Pipeline name", max_length=255)
    description: str | None = Field(None, description="Pipeline description")
    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if not v:
            raise ValueError("Pipeline name cannot be empty or whitespace-only")
        return v


class StatsResponse(OrmResponseModel):
    """Pipeline statistics response schema."""

    total: int = Field(..., description="Total number of pipeline")
    last_updated: str = Field(..., description="Last updated date")

    class Config:
        arbitrary_types_allowed = True


class PipelineResponse(OrmResponseModel):
    """Pipeline response schema."""

    id: int = Field(..., description="Pipeline ID")
    name: str = Field(..., description="Pipeline name")
    description: str | None = Field(None, description="Pipeline description")
    is_active: bool = Field(..., description="Whether the pipeline is active")
    is_default: bool = Field(..., description="Whether the pipeline is default")
    ocr_provider: str | None = Field(None, description="OCR provider")
    parsing_method: str | None = Field(None, description="Parsing method")
    vlm_model_provider: str | None = Field(None, description="VLM model provider")
    vlm_model: str | None = Field(None, description="VLM model")
    llm_model_provider: str | None = Field(None, description="LLM model provider")
    llm_model: str | None = Field(None, description="LLM model")
    task_metadata: TaskMetadata | None = Field(
        None,
        description="Task specific metadata such as batch size and context enabling",
        example={"enable_context": False, "batch_size": 1},
    )
    created_by: int | None = Field(None, description="User ID who created the pipeline")
    created_at: datetime = Field(..., description="Pipeline creation timestamp")
    updated_at: datetime | None = Field(
        None, description="Pipeline last update timestamp"
    )


# ---------------------------------------------------------------------------
# Pipeline configuration response (available providers / models)
# ---------------------------------------------------------------------------

class ModelOption(OrmResponseModel):
    """A selectable model option."""

    value: str = Field(..., description="Model identifier")
    label: str = Field(..., description="Human-readable label")


class ProviderOption(OrmResponseModel):
    """A selectable provider option (no nested models)."""

    value: str = Field(..., description="Provider identifier")
    label: str = Field(..., description="Human-readable label")


class LLMProviderOption(OrmResponseModel):
    """LLM provider with its available models."""

    value: str = Field(..., description="Provider identifier")
    label: str = Field(..., description="Human-readable label")
    models: list[ModelOption] = Field(..., description="Available models for this provider")


class VLMProviderOption(OrmResponseModel):
    """VLM provider with its available models."""

    value: str = Field(..., description="Provider identifier")
    label: str = Field(..., description="Human-readable label")
    models: list[ModelOption] = Field(..., description="Available models for this provider")


class PipelineConfigsResponse(OrmResponseModel):
    """
    Available pipeline configuration options.

    Azure OCR and OpenAI LLM providers are only included when
    their respective credentials are present in the secret store.
    """

    ocr_providers: list[ProviderOption] = Field(..., description="Available OCR providers")
    llm_providers: list[LLMProviderOption] = Field(..., description="Available LLM providers")
    vlm_providers: list[VLMProviderOption] = Field(..., description="Available VLM providers")
    parsing_methods: list[ProviderOption] = Field(..., description="Available parsing methods")
