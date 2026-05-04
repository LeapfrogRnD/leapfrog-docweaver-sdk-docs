from enum import Enum

from leapx.pipeline.stages.ocr_stage import OCRStage
from leapx.pipeline.stages.parser_stage import ParserStage
from leapx.pipeline.stages.extraction.llm_stage import LLMExtractionStage
from leapx.pipeline.stages.generation_stage import LLMGenerationStage
from leapx.pipeline.stages.vlm_stage import VLMStage


class Stage(Enum):
    """enum values for stage"""

    OCR = OCRStage
    PARSER = ParserStage
    LLM_EXTRACTION = LLMExtractionStage
    LLM_GENERATION = LLMGenerationStage
    VLM_PARSER = VLMStage
