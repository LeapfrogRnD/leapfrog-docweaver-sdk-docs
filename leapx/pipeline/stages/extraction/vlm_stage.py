from typing import Any

from leapx.pipeline.core.config import PipelineConfig
from leapx.pipeline.stages.extraction.base import BaseExtractionStage


class VLMExtractionStage(BaseExtractionStage):
    """VLM direct extraction (future implementation).

    Args:
        vlm_client (Any): Client or SDK used to communicate with a VLM provider.
        config (PipelineConfig): Pipeline configuration providing extraction parameters.

    Attributes:
        vlm_client (Any): The VLM client instance.
        config (PipelineConfig): Configuration used to build extraction requests.
    """

    def __init__(self, vlm_client: Any, config: PipelineConfig):
        self.vlm_client = vlm_client
        self.config = config

    async def execute_dynamic(self, text: str) -> dict[str, Any]:
        """Extract using VLM directly.

        Args:
            text (str): Input text content to extract fields from.

        Returns:
            dict[str, Any]: Structured extraction result.

        Raises:
            NotImplementedError: VLM extraction is not yet implemented.
        """
        raise NotImplementedError("VLM extraction coming soon")
