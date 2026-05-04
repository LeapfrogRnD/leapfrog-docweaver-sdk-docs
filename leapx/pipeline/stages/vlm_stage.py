from typing import Any

from leapx.common.document.utils import is_pdf
from leapx.common.observability.logger import logger
from leapx.common.utils.file_to_bytes import is_pdf_blank
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.configs import VLMConfig
from leapx.pipeline.stages.constants import (
    COMBINED_TEXT,
    IS_BLANK,
    PARSED_PAGES,
    STATUS_COMPLETED,
    TOTAL_CHARS,
    TOTAL_PAGES,
)
from leapx.pipeline.stages.schemas import StageName, StageOutput, StageType
from leapx.services.vlm.engine_factory import VLMEngineFactory


class VLMStage(BaseStage[bytes, str]):
    """
    Pipeline stage that uses a VLM extractor to convert documents
    into structured HTML.
    """

    def __init__(self, config: VLMConfig, stage_id: str | None = None):
        super().__init__(config, stage_id)
        try:
            self.vlm_extractor = VLMEngineFactory.create_engine(
                model_id=self.config.model.value,
                extraction_method=self.config.extraction_type,
                extraction_prompt=self.config.extraction_prompt,
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize VLM extractor: {e}",
                stage_name=StageName.vlm,
                stage_id=self.stage_id,
                error_type=type(e).__name__,
            )
            raise RuntimeError("VLMStage initialization failed") from e  # noqa: TRY003

    @property
    def name(self) -> str:
        return StageName.vlm

    @property
    def stage_type(self) -> StageType:
        return StageType.IO

    async def execute(self, input_data: bytes) -> StageOutput:
        """
        Placeholder for static execution method. Could be implemented if needed.
        """
        try:
            return await self.execute_dynamic(
                input_data, previous_output=None, config=self.config
            )
        except Exception as e:
            logger.error(
                f"Execution failed in VLMStage: {e}",
                stage_name=self.name,
                stage_id=self.stage_id,
                error_type=type(e).__name__,
            )
            raise

    async def execute_dynamic(
        self,
        chunk: Any,
        previous_output=None,  # noqa: ARG002
        config=None,  # noqa: ARG002
    ) -> StageOutput:
        """
        Execute the VLM stage on a document.
        Handles blank PDF detection and returns structured output.

        Args:
            chunk: Input chunk containing PDF bytes.
            previous_output: Unused, kept for parent class compatibility.
            config: Unused, kept for parent class compatibility.
        """
        try:
            # Check for blank PDF only when the chunk is actually PDF bytes.
            is_chunk_pdf, _ = is_pdf(chunk.file_bytes)
            if is_chunk_pdf and is_pdf_blank(chunk.file_bytes):
                logger.warning(
                    "Blank PDF detected", stage_name=self.name, stage_id=self.stage_id
                )
                return StageOutput(
                    data={
                        PARSED_PAGES: [],
                        COMBINED_TEXT: "",
                        TOTAL_PAGES: 0,
                        IS_BLANK: True,
                    },
                    metadata={
                        IS_BLANK: True,
                        TOTAL_PAGES: 0,
                        TOTAL_CHARS: 0,
                    },
                    skip_remaining=True,
                )

            # Extract text using VLM extractor
            output = await self.vlm_extractor.extract_multi_page(chunk.file_bytes)
            combined_text = "\n".join(output)

            logger.stage_log(
                stage_name=self.name,
                status=STATUS_COMPLETED,
                stage_id=self.stage_id,
                total_pages=len(output),
            )

            return StageOutput(
                data={
                    PARSED_PAGES: output,
                    COMBINED_TEXT: combined_text,
                    TOTAL_PAGES: len(output),
                },
                metadata={
                    TOTAL_PAGES: len(output),
                    TOTAL_CHARS: len(combined_text),
                },
            )

        except Exception as e:
            logger.error(
                f"VLM extraction failed: {e}",
                stage_name=self.name,
                stage_id=self.stage_id,
                error_type=type(e).__name__,
            )
            # You can choose to raise or return a structured error output
            raise RuntimeError("VLMStage execution failed") from e  # noqa: TRY003
