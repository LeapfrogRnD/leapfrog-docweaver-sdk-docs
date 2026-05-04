from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """Model configuration for the extractor"""

    temperature: float | None = Field(default=0.1, description="Model temperature")
    max_tokens: int | None = Field(
        default=1000, description="Maximum tokens to generate"
    )
    model: str = Field(
        default="bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0",
        description="Model to use",
    )


class SystemPrompt(BaseModel):
    """System prompt configuration for the extractor"""

    content: str = Field(..., description="The system prompt content")


class UserPrompt(BaseModel):
    """User prompt with the content to extract from"""

    content: str = Field(..., description="The user prompt content")
    context: str | None = Field(
        default=None, description="Additional context for extraction"
    )


class ExtractionRequest(BaseModel):
    """Request model for extraction operations"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    system_prompt: SystemPrompt
    user_prompt: UserPrompt
    config: ModelConfig
    response_model: type[BaseModel] = Field(
        ..., description="Pydantic model for structured output"
    )


class ExtractionResponse(BaseModel):
    """Response model for extraction operations"""

    data: BaseModel | None = Field(
        default=None, description="Extracted pydantic model data"
    )
    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional metadata"
    )
