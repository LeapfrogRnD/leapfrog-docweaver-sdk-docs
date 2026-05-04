"""OCR stage implementation.

This module provides the OCRStage responsible for running OCR on binary content
and normalizing the extracted text.
"""

from typing import Any

from leapx.common.document.utils import is_image
from leapx.common.observability.logger import logger
from leapx.common.utils.file_to_bytes import is_pdf_blank
from leapx.pipeline.core.text_processor import TextProcessor
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.configs.ocr_config import OCRConfig
from leapx.pipeline.stages.constants import (
    BLANK_PDF_DETECTED,
    END_PAGE,
    IS_BLANK,
    OCR_DATA_LIST,
    START_PAGE,
    STATUS_COMPLETED,
    TOTAL_PAGES,
)
from leapx.pipeline.stages.schemas import StageName, StageOutput, StageType
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.engine_factory import OCREngineFactory


class OCRStage(BaseStage[bytes, list[OCRData]]):
    """OCR extraction stage.

    Args:
        ocr_engine (OCREngine): Engine used to extract text from binary content.

    Attributes:
        ocr_engine (OCREngine): The OCR engine instance.
        text_processor (TextProcessor): Utility to normalize OCR output.
    """

    def __init__(self, config: OCRConfig, stage_id: str | None = None, **kwargs):  # noqa: ARG002
        super().__init__(config, stage_id)
        self.ocr_engine = OCREngineFactory.create_engine(
            provider=self.config.provider,
            credential=self.config.credential,
            cache_config=self.config.cache_config,
        )
        self.text_processor = TextProcessor()

    @property
    def name(self) -> str:
        """Get stage identifier.

        Returns:
            str: The identifier for this stage.
        """
        return StageName.ocr

    @property
    def stage_type(self) -> StageType:
        """Get execution type.

        Returns:
            StageType: IO-bound stage type.
        """
        return StageType.IO

    async def execute(self, content: bytes) -> OCRData:
        """Run OCR on content.

        Args:
            content (bytes): Binary document content.

        Returns:
            OCRData: Normalized OCR result for the first page or segment.
        """
        extracted = await self.ocr_engine.extract_text(content)
        return self.text_processor.normalize_ocr_data(extracted)[0]

    async def execute_dynamic(
        self,
        chunk: Any,
        **kwargs,  # noqa: ARG002
    ) -> StageOutput:
        """Execute OCR on the chunk's PDF bytes.

        Args:
            chunk: ChunkResult containing file_bytes.
            previous_outputs: Not used for OCR stage.
            config: OCR configuration options.

        Returns:
            StageOutput with ocr_data_list and metadata.
        """
        # Check for blank PDF (skip for images)
        is_img, _ = is_image(chunk.file_bytes)
        if not is_img and is_pdf_blank(chunk.file_bytes):
            logger.info(BLANK_PDF_DETECTED)
            return StageOutput(
                data={OCR_DATA_LIST: [], TOTAL_PAGES: 0, IS_BLANK: True},
                metadata={TOTAL_PAGES: 0, IS_BLANK: True},
                skip_remaining=True,
            )

        # Perform OCR
        ocr_data_list = await self.ocr_engine.extract_text(chunk.file_bytes)
        ocr_data_list = self.text_processor.normalize_ocr_data(ocr_data_list)
        total_pages = len(ocr_data_list)

        logger.stage_log(
            stage_name=StageName.ocr,
            status=STATUS_COMPLETED,
            stage_id=self.stage_id,
            total_pages=total_pages,
        )
        return StageOutput(
            data={
                OCR_DATA_LIST: ocr_data_list,
                TOTAL_PAGES: total_pages,
                IS_BLANK: False,
            },
            metadata={
                TOTAL_PAGES: total_pages,
                START_PAGE: chunk.metadata.start_page,
                END_PAGE: chunk.metadata.end_page,
            },
        )
