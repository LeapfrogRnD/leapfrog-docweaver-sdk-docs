from leapx.pipeline.core.config import PipelineConfig
from leapx.pipeline.core.pool_manager import PoolManager
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.constants import LAYOUT_PARSING, VLM_PARSING
from leapx.pipeline.stages.extraction.llm_stage import LLMExtractionStage
from leapx.pipeline.stages.generation_stage import LLMGenerationStage
from leapx.pipeline.stages.ocr_stage import OCRStage
from leapx.pipeline.stages.parser_stage import ParserStage
from leapx.pipeline.stages.vlm_stage import VLMStage


class StageFactory:
    """Factory to create pipeline stages with injected dependencies."""

    def __init__(self, pipeline_config: PipelineConfig, pool_manager: PoolManager):
        self.pipeline_config = pipeline_config
        self.pool_manager = pool_manager

        self._registry: dict[type[BaseStage], callable] = {
            OCRStage: self._create_ocr_stage,
            ParserStage: self._create_parser_stage,
            LLMExtractionStage: self._create_llm_stage,
            VLMStage: self._create_vlm_stage,
            LLMGenerationStage: self._create_generation_stage,
        }

    def _create_ocr_stage(self) -> OCRStage:
        return OCRStage(config=self.pipeline_config.ocr_config, stage_id="ocr")

    def _create_vlm_stage(self) -> VLMStage:
        return VLMStage(config=self.pipeline_config.vlm_config, stage_id=VLM_PARSING)

    def _create_parser_stage(self) -> ParserStage:
        return ParserStage(
            config=self.pipeline_config.parser_config,
            pool_manager=self.pool_manager,
            stage_id=LAYOUT_PARSING,
        )

    def _create_llm_stage(self) -> LLMExtractionStage:
        return LLMExtractionStage(
            config=self.pipeline_config.llm_extraction_config,
            pool_manager=self.pool_manager,
            stage_id="extraction",
        )

    def _create_generation_stage(self) -> LLMGenerationStage:
        return LLMGenerationStage(
            config=self.pipeline_config.llm_generation_config,
            pool_manager=self.pool_manager,
            stage_id="generation",
        )

    def create(self, stage_cls: type[BaseStage]) -> BaseStage:
        """Generic create method for a stage class."""
        for registered_cls, factory in self._registry.items():
            if issubclass(stage_cls, registered_cls):
                return factory()
        raise ValueError(f"No factory registered for {stage_cls}")  # noqa: TRY003
