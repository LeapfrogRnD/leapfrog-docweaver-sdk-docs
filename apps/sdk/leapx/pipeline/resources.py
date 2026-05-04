"""Model and service registry."""

from leapx.common.types.providers import (
    LLM_MODEL_GROUPS,
    LLMProviderType,
    OCRProviderType,
    ParsingMethod,
)


def list_available_models(
    provider: LLMProviderType | None = None,
) -> dict[str, list[dict[str, str]]]:
    """
    List all available LLM models by provider.

    Args:
        provider: Optional specific provider to filter by.

    Returns:
        Dictionary mapping provider names to lists of model information.
    """
    result = {}

    if provider:
        if provider in LLM_MODEL_GROUPS:
            model_enum = LLM_MODEL_GROUPS[provider]
            result[provider.value] = [
                {"name": model.name, "value": model.value} for model in model_enum
            ]
    else:
        for llm_provider, model_enum in LLM_MODEL_GROUPS.items():
            result[llm_provider.value] = [
                {"name": model.name, "value": model.value} for model in model_enum
            ]

    return result


def list_available_services() -> dict[str, list[dict[str, str]]]:
    """List all available services."""
    return {
        "ocr": [{"name": m.name, "value": m.value} for m in OCRProviderType],
        "parser": [{"name": m.name, "value": m.value} for m in ParsingMethod],
    }
