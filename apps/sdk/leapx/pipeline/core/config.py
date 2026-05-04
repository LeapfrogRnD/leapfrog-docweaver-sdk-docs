"""Pipeline configuration using Pydantic."""

from functools import cached_property

from pydantic import BaseModel

from leapx.pipeline.stages.configs import (
    LLMExtractionConfig,
    LLMGenerationConfig,
    OCRConfig,
    ParserConfig,
    VLMConfig,
)
from leapx.services.chunking.config import ChunkingConfig
from leapx.services.chunking.exceptions import (
    InvalidChunkingClassError,
)
from leapx.services.chunking.factory import ChunkingStrategyFactory
from leapx.services.chunking.schemas import ChunkingMethod
from leapx.services.chunking.strategy.base import ChunkingStrategy


class PipelineConfig(BaseModel):
    """Central configuration for the LeapX pipeline.

    This model normalizes inputs, validates credentials, and builds fully
    resolved configuration objects for downstream services.

    Args:
        ocr_config: ocr_config
        parser_config: Parser-specific configuration.
        llm_extraction_config:LLM specific config
        chunking_config: Optional chunking configuration.
        custom_chunking_class: Optional custom chunking strategy class.
    """

    ocr_config: OCRConfig | None = None
    parser_config: ParserConfig | None = None
    llm_extraction_config: LLMExtractionConfig | None = None
    llm_generation_config: LLMGenerationConfig | None = None
    vlm_config: VLMConfig | None = None
    chunking_config: ChunkingConfig | None = None
    custom_chunking_class: type[ChunkingStrategy] | None = None
    enable_context: bool = False  # Enable context passing between chunks

    @cached_property
    def chunking_class(self) -> ChunkingStrategy:
        """Resolve and instantiate the chunking strategy.

        Returns:
            An instance of the configured chunking strategy.

        Raises:
            InvalidChunkingClassError: If a custom class is provided but does not
                inherit from ChunkingStrategy.
        """
        if self.custom_chunking_class:
            if not issubclass(self.custom_chunking_class, ChunkingStrategy):
                raise InvalidChunkingClassError
            return self.custom_chunking_class()
        if not self.chunking_config:
            self.chunking_config = ChunkingConfig(
                method=ChunkingMethod.BATCH_WISE,
                batch_size=1,
            )
        return ChunkingStrategyFactory.create(self.chunking_config)
