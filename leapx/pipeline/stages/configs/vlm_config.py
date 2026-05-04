# ruff: noqa: TRY003

from __future__ import annotations

from typing import Any

from pydantic import model_validator

from leapx.common.types.providers import (
    VLM_MODEL_GROUPS,
    VLMModel,
    VLMProviderType,
)
from leapx.pipeline.stages.configs.base import BlockConfig
from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.vlm.exceptions.vlm_exceptions import InvalidVLMModelError


class VLMConfig(BlockConfig):
    """
    Configuration for the VLM stage.

    Args:
        model: Vision-language model identifier.
        vlm_provider: Underlying platform (OpenAI, Bedrock, etc.).
        extraction_type: Output format for the VLM (html, or markdown).
        extraction_prompt: Dict mapping of extraction_type to VLM system prompt.
        credential: Bedrock credentials
    """

    model: VLMModel
    vlm_provider: VLMProviderType | None = None
    extraction_type: str | None = None
    extraction_prompt: dict[str, str] | None = None
    credential: BedrockCredential | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_model_input(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Normalize and validate the VLM model based on the provider.

        Args:
            values: Raw initialization values for the model.

        Returns:
            The possibly mutated values with a validated/normalized model enum.

        Raises:
            InvalidVLMModelError: If the provided model is invalid for the
                inferred provider.
        """
        if isinstance(values, dict):
            vlm_model_input = values.get("model")
            vlm_provider = values.get("vlm_provider", VLMProviderType.BEDROCK)
            if vlm_model_input:
                if vlm_provider == VLMProviderType.BEDROCK:
                    values["credential"] = BedrockCredential()

                model_group = VLM_MODEL_GROUPS.get(vlm_provider)
                if not model_group:
                    raise InvalidVLMModelError(
                        details={
                            "error": f"No model group found for provider {vlm_provider}"
                        }
                    )

                if isinstance(vlm_model_input, str):
                    for model_enum in model_group:
                        if model_enum.value == vlm_model_input:
                            values["model"] = model_enum
                            break
                    else:
                        raise InvalidVLMModelError(
                            details={
                                "error": f"Model {vlm_model_input} is not valid for provider {vlm_provider.value}.",
                                "allowed_models": [m.value for m in model_group],
                            }
                        )
                elif values["model"] not in model_group:
                    raise InvalidVLMModelError(
                        details={
                            "error": f"Model {vlm_model_input} is not valid for provider {vlm_provider.value}.",
                            "allowed_models": [m.value for m in model_group],
                        }
                    )
        return values
