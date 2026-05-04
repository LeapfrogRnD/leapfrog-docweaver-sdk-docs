"""Parser stage implementation.

This module provides ParserStage which converts OCR data into structured text
using a layout parser.
"""

from typing import Any

from leapx.common.observability.logger import logger
from leapx.pipeline.core.pool_manager import PoolManager
from leapx.pipeline.core.text_processor import TextProcessor
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.configs import ParserConfig
from leapx.pipeline.stages.constants import (
    COMBINED_TEXT,
    END_PAGE,
    METADATA,
    OCR,
    OCR_DATA_LIST,
    OUTPUT,
    PAGE_NUMBER,
    PARSED_PAGES,
    START_PAGE,
    STATUS_COMPLETED,
    TEXT,
    TOTAL_CHARS,
    TOTAL_PAGES,
)
from leapx.pipeline.stages.exceptions import MissingOCRResultError
from leapx.pipeline.stages.schemas import StageName, StageOutput, StageType
from leapx.services.layout_parser.parser_factory import ParserFactory
from leapx.services.layout_parser.structures.ocr_data import OCRData


class ParserStage(BaseStage[list[OCRData], str]):
    """Layout parsing stage.

    Args:
        config (ParserConfig): Parser stage configuration.
        pool_manager (PoolManager, optional): Optional CPU pool manager.
        stage_id (str, optional): Stage identifier.
    """

    def __init__(
        self,
        config: ParserConfig,
        pool_manager: PoolManager | None = None,
        stage_id: str | None = None,
    ):
        super().__init__(config, stage_id)

        self.parser_subconfig = config.instance
        self.method = config.method

        self.layout_parser = ParserFactory.create(
            method=self.method,
            config=self.parser_subconfig,
        )

        self.pool_manager = pool_manager or PoolManager()
        self.text_processor = TextProcessor()

    @property
    def name(self) -> str:
        """Get stage identifier.

        Returns:
            str: The identifier for this stage.
        """
        return StageName.parser

    @property
    def stage_type(self) -> StageType:
        """Get execution type.

        Returns:
            StageType: IO-bound stage type.
        """
        return StageType.IO

    async def execute(self, ocr_data: OCRData) -> str:
        """Parse OCR data to structured text.

        Args:
            ocr_data (OCRData): OCR structures to be parsed.

        Returns:
            str: Parsed structured text.
        """
        return self.layout_parser.parse(ocr_data)

    async def execute_dynamic(
        self,
        previous_output: dict[str, dict],
        **kwargs,  # noqa: ARG002
    ) -> StageOutput:
        """Parse OCR output into structured text.

        Args:
            chunk: ChunkResult (not directly used, OCR
            output comes from previous_outputs).
            previous_output: Must contain OCR stage output with ocr_data_list.
            config: Layout parsing configuration.

        Returns:
            StageOutput with parsed_pages and combined_text.

        Raises:
            ValueError: If OCR output is not available.
        """
        ocr_result = self._find_ocr_output(previous_output)
        ocr_output = ocr_result.get(OUTPUT)

        if ocr_output is None:
            raise MissingOCRResultError
        ocr_data_list = ocr_output.get(OCR_DATA_LIST, [])
        total_pages = ocr_output.get(TOTAL_PAGES, len(ocr_data_list))

        # Parse pages concurrently
        parsed_pages = await self._parse_pages(ocr_data_list)
        combined_text = self.text_processor.combine_parsed_pages(
            parsed_pages, total_pages
        )

        logger.stage_log(
            stage_name=self.name,
            status=STATUS_COMPLETED,
            stage_id=self.stage_id,
            total_pages=total_pages,
            total_chars=len(combined_text),
        )
        return StageOutput(
            data={
                PARSED_PAGES: parsed_pages,
                COMBINED_TEXT: combined_text,
                TOTAL_PAGES: total_pages,
            },
            metadata={
                TOTAL_PAGES: total_pages,
                START_PAGE: ocr_result.get(METADATA).get(START_PAGE),
                END_PAGE: ocr_result.get(METADATA).get(END_PAGE),
                TOTAL_CHARS: len(combined_text),
            },
        )

    def _find_ocr_output(self, previous_outputs: dict[str, Any]) -> dict | None:
        """Find OCR output from previous stages."""
        if OCR in previous_outputs:
            return previous_outputs[OCR]

        for output in previous_outputs.values():
            if isinstance(output, dict) and OCR_DATA_LIST in output:
                return output

        return None

    async def _parse_pages(self, ocr_data_list: list[OCRData]) -> list[dict]:
        """Parse all OCR pages concurrently."""
        tasks = [
            self.pool_manager.run_cpu(self.layout_parser.parse, ocr_data)
            for ocr_data in ocr_data_list
        ]
        parsed_texts = await self.pool_manager.run_concurrently(tasks)

        return [
            {
                PAGE_NUMBER: getattr(d, METADATA, {}).get(PAGE_NUMBER, i + 1),
                TEXT: t,
            }
            for i, (d, t) in enumerate(zip(ocr_data_list, parsed_texts, strict=True))
        ]
