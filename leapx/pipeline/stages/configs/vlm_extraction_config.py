from __future__ import annotations

from leapx.common.types.providers import VLMModel, VLMProviderType
from leapx.pipeline.stages.configs.base import BlockConfig


class VLMExtractionConfig(BlockConfig):
    model: VLMModel
    provider: VLMProviderType | None = VLMProviderType.BEDROCK
    system_prompt: str
    temperature: float | None = 0.2
    max_tokens: int | None = 30000
