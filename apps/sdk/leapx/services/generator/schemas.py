from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResponseModel(BaseModel):
    """Example response model for generation output"""

    summary: str = Field(..., description="Generated summary text")


class ModelConfig(BaseModel):
    """Model configuration for the generator"""

    temperature: float | None = Field(default=0.1, description="Model temperature")
    max_tokens: int | None = Field(
        default=20000, description="Maximum tokens to generate"
    )
    model: str = Field(
        default="bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0",
        description="Model to use",
    )


class SystemPrompt(BaseModel):
    """System prompt configuration for the generator"""

    content: str = Field(..., description="The system prompt content")


class UserPrompt(BaseModel):
    """User prompt with the content to summarize"""

    content: str = Field(..., description="The user prompt content")
    context: str | None = Field(
        default=None, description="Additional context for generation"
    )


class GenerationRequest(BaseModel):
    """Request model for generation operations"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    system_prompt: SystemPrompt
    user_prompt: UserPrompt
    config: ModelConfig
    response_model: type[BaseModel]  # Changed to accept a class type, not an instance


class GenerationResponse(BaseModel):
    """Response model for generation operations"""

    data: str = Field(..., description="The generated text response")
    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional metadata"
    )
