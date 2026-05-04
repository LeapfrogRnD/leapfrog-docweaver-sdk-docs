"""LeapX Pipeline - Document processing orchestration."""

import asyncio
from typing import Any

from leapx.common.document.utils import read_file_to_bytes
from leapx.common.observability.logger import logger
from leapx.pipeline.core.config import (
    PipelineConfig,
)
from leapx.pipeline.core.executor import PipelineExecutor
from leapx.pipeline.core.pool_manager import PoolManager
from leapx.pipeline.core.response_builder import PipelineResponseBuilder
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.configs import LLMExtractionConfig, OCRConfig, ParserConfig
from leapx.pipeline.stages.configs.llm_generation_config import LLMGenerationConfig
from leapx.pipeline.stages.configs.vlm_config import VLMConfig
from leapx.pipeline.stages.extraction.llm_stage import LLMExtractionStage
from leapx.pipeline.stages.ocr_stage import OCRStage
from leapx.pipeline.stages.parser_stage import ParserStage
from leapx.pipeline.stages.stage_factory import StageFactory
from leapx.services.chunking.config import ChunkingConfig
from leapx.services.chunking.schemas import ChunkResult, InputType
from leapx.services.chunking.strategy.base import ChunkingStrategy


class LeapXPipeline:
    """Document processing pipeline orchestrator.

    Coordinates OCR, layout parsing, and LLM extraction stages.

    Args:
        ocr: OCR stage configuration.
        llm: LLM stage configuration.
        parser: Layout parser configuration.
        json_schema: Pydantic model class or JSON schema dict describing
            expected output.
        chunking_config: Optional chunking configuration for splitting input.
        chunking_class: Optional custom chunking strategy instance.
        stages: Optional custom stages list (overrides default stages).
    """

    def __init__(  # noqa: PLR0913
        self,
        ocr: OCRConfig | None = None,
        llm: LLMExtractionConfig | None = None,
        llm_gen: LLMGenerationConfig | None = None,
        parser: ParserConfig | None = None,
        vlm: VLMConfig | None = None,
        chunking_config: ChunkingConfig | None = None,
        chunking_class: ChunkingStrategy | None = None,
        stages: list[type[BaseStage]] | None = None,
        enable_context: bool = False,
    ) -> None:
        """Initialize LeapX Pipeline and all dependent services."""
        self.config = PipelineConfig(
            ocr_config=ocr,
            llm_extraction_config=llm,
            llm_generation_config=llm_gen,
            parser_config=parser,
            vlm_config=vlm,
            chunking_config=chunking_config,
            chunking_class=chunking_class,
            enable_context=enable_context,
        )

        logger.info(
            "Initializing LeapX pipeline",
            ocr_provider=self.config.ocr_config.provider
            if self.config.ocr_config
            else None,
            parser=self.config.parser_config.method
            if self.config.parser_config
            else None,
            vlm_provider=self.config.vlm_config.vlm_provider
            if self.config.vlm_config
            else None,
            model=llm.model if llm else llm,
        )

        self.chunking_classs = self.config.chunking_class
        self.pool_manager = PoolManager(cpu_workers=0)
        self.stage_factory = StageFactory(self.config, self.pool_manager)

        if stages:
            self.stages = [self.stage_factory.create(s) for s in stages]
        else:
            self.stages = [
                self.stage_factory.create(OCRStage),
                self.stage_factory.create(ParserStage),
                self.stage_factory.create(LLMExtractionStage),
            ]

        response_builder = PipelineResponseBuilder(self.config)
        self.executor = PipelineExecutor(
            stages=self.stages,
            config=self.config,
            response_builder=response_builder,
            pool_manager=self.pool_manager,
        )
        logger.info(
            "LeapX pipeline initialized successfully",
            stages=[s.stage_id for s in self.stages],
        )

    def _create_chunks(
        self, input_data: str | bytes, input_type: InputType = InputType.FILE
    ) -> list[ChunkResult]:
        """Create chunks from the input.

        Args:
            input_data: Path to a file, raw bytes, or text string.
            input_type: Type of input (FILE or TEXT).

        Returns:
            A list of chunking results used downstream by the executor.
        """
        bytes_data = read_file_to_bytes(input_data)
        return self.chunking_classs.chunk(bytes_data, input_type)

    def run(
        self, input_data: str | bytes, input_type: InputType = InputType.FILE
    ) -> dict[str, Any]:
        """Execute the pipeline synchronously on a document or text.

        Uses asyncio.run under the hood if not already in an event loop.

        Args:
            input_data: Path, bytes of the document, or text string to process.
            input_type: Type of input (FILE or TEXT).

        Returns:
            The aggregated pipeline result for all chunks.

        Raises:
            RuntimeError: If called inside a running event loop.
        """
        try:
            asyncio.get_running_loop()
            raise RuntimeError(  # noqa: TRY003, TRY301
                "Cannot call run() inside a running event loop. Use async_run() instead."
            )
        except RuntimeError:

            async def _wrapper():
                chunks = self._create_chunks(input_data, input_type)
                return await self.executor.execute(
                    chunks, enable_context=self.config.enable_context
                )

            return asyncio.run(_wrapper())

    async def async_run(
        self, input_data: str | bytes, input_type: InputType = InputType.FILE
    ) -> dict[str, Any]:
        """Execute the pipeline on a document or text asynchronously.

        Args:
            input_data: Path, bytes of the document, or text string to process.
            input_type: Type of input (FILE or TEXT).

        Returns:
            The aggregated pipeline result for all chunks.
        """
        chunks = self._create_chunks(input_data, input_type)
        return await self.executor.execute(
            chunks, enable_context=self.config.enable_context
        )
