from __future__ import annotations

from typing import Any

import litellm
from pydantic import BaseModel, model_validator

from leapx.common.types.providers import LLM_MODEL_GROUPS, LLMModel, LLMProviderType
from leapx.pipeline.stages.configs.base import BlockConfig
from leapx.services.credentials.base import Credential
from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.credentials.openai_config import OpenAICredential
from leapx.services.generator.exceptions.generator_exceptions import (
    InvalidLLMModelError,
)
from leapx.services.generator.generator_factory import GeneratorProvider
from leapx.services.generator.schemas import ResponseModel


class LLMGenerationConfig(BlockConfig):
    """Configuration for the LLM generation stage.

    Args:
        model: Target LLM model enum.
        provider: Backend generation provider implementation.
        system_prompt: System prompt to steer generation.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens for generation.
        cache_config: Optional cache configuration for LLM responses.
    """

    model: LLMModel
    provider: GeneratorProvider | None = GeneratorProvider.LITE_LLM
    llm_provider: LLMProviderType | None = LLMProviderType.BEDROCK
    system_prompt: str
    user_instructions: str
    json_schema: type[BaseModel] = ResponseModel
    temperature: float | None = 0.2
    max_tokens: int | None = 30000

    @model_validator(mode="before")
    @classmethod
    def validate_model_input(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Normalize and validate the LLM model based on the provider.

        Args:
            values: Raw initialization values for the model.

        Returns:
            The possibly mutated values with a validated/normalized model enum.

        Raises:
            InvalidLLMModelError: If the provided model is invalid for the
                inferred provider.
        """
        if isinstance(values, dict):
            llm_model_input = values.get("model")
            llm_provider = values.get("llm_provider", LLMProviderType.BEDROCK)
            if isinstance(llm_provider, str):
                llm_provider = LLMProviderType(llm_provider)
            if llm_model_input:
                if llm_provider.value == LLMProviderType.BEDROCK:
                    values["credential"] = BedrockCredential()
                elif llm_provider.value == LLMProviderType.OPENAI:
                    values["credential"] = OpenAICredential()

                model_group = LLM_MODEL_GROUPS.get(llm_provider)
                if not model_group:
                    raise InvalidLLMModelError(
                        details={
                            "error": f"No model group found for provider {llm_provider.value}"
                        }
                    )

                if isinstance(llm_model_input, str):
                    for model_enum in model_group:
                        if model_enum.value == llm_model_input:
                            values["model"] = model_enum
                            break
                    else:
                        raise InvalidLLMModelError(
                            details={
                                "error": f"Model {llm_model_input} is not valid for provider {llm_provider.value}.",
                                "allowed_models": [m.value for m in model_group],
                            }
                        )
                elif values["model"] not in model_group:
                    raise InvalidLLMModelError(
                        details={
                            "error": f"Model {llm_model_input} is not valid for provider {llm_provider.value}.",
                            "allowed_models": [m.value for m in model_group],
                        }
                    )
        return values

    @classmethod
    def _infer_generation_credential(
        cls, provider: GeneratorProvider
    ) -> LLMProviderType:
        """Infer the LLM Credential from generation_provider.

        Args:
            provider: llm generation provider.

        Returns:
            The inferred LLM provider type.

        Raises:
            InvalidLLMModelError: If the credential type cannot be mapped to an
                LLM provider.
        """
        # Check if provider is already an GeneratorProvider enum
        if isinstance(provider, GeneratorProvider):
            # For now, default to OPENAI for LITE_LLM provider
            # This will be overridden by model-based inference below
            # if model is provided
            return LLMProviderType.OPENAI

        # If provider is a credential, infer from its type
        if isinstance(provider, Credential):
            if isinstance(provider, BedrockCredential):
                return LLMProviderType.BEDROCK
            if isinstance(provider, OpenAICredential):
                return LLMProviderType.OPENAI

        raise InvalidLLMModelError(
            details={
                "error": f"Could not infer LLM provider from {provider}",
                "allowed_model_providers": ["bedrock", "openai"],
            },
        )

    @classmethod
    def _infer_provider_from_model(cls, model_input: str | LLMModel) -> LLMProviderType:
        """Infer the LLM provider from the model identifier.

        Args:
            model_input: Model string or enum value.

        Returns:
            The inferred LLM provider type.

        Raises:
            InvalidLLMModelError: If the provider cannot be inferred from the model.
        """
        # Get the string representation of the model
        if isinstance(model_input, str):
            model_str = model_input
        elif hasattr(model_input, "value"):
            model_str = model_input.value
        else:
            model_str = str(model_input)

        # Infer provider based on model prefix or pattern
        if model_str.startswith("bedrock/"):
            return LLMProviderType.BEDROCK
        if model_str.startswith(("gpt-", "o1-", "o3-")):
            return LLMProviderType.OPENAI

        # If no clear pattern, try to match against known model groups
        for provider_type, model_group in LLM_MODEL_GROUPS.items():
            for model_enum in model_group:
                if model_enum.value == model_str:
                    return provider_type

        raise InvalidLLMModelError(
            details={
                "error": f"Could not infer provider from model: {model_str}",
                "hint": "Model should start with 'bedrock/' for Bedrock or 'gpt-' for OpenAI",
            }
        )

    def _validate_llm_invocation(self):
        """Perform a minimal LLM call to validate model/credential combination."""
        model_value = (
            self.model.value if hasattr(self.model, "value") else str(self.model)
        )
        litellm.completion(
            model=model_value, messages=[{"role": "user", "content": "."}]
        )

    @model_validator(mode="after")
    def validate_credentials_after_init(self) -> LLMGenerationConfig:
        """Post-init validation for credentials and parser config.

        Returns:
            The validated LLMGenerationConfig instance.
        """
        self.credential.validate_for_use()
        self._validate_llm_invocation()
        return self

    def get_generation_config(self) -> dict[str, Any]:
        """Assemble the generationtion request configuration for the GeneratorService.

        Returns:
            A dictionary suitable for constructing an GenerationRequest.
        """
        model_value = (
            self.model.value if hasattr(self.model, "value") else str(self.model)
        )
        return {
            "system_prompt": {"content": self.system_prompt},
            "user_prompt": {
                "user_instructions": self.user_instructions,
                "content": "",  # Populated at runtime with parsed text
            },
            "config": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "model": model_value,
            },
            "response_model": self.json_schema,
        }
