from typing import Any

from leapx.common.observability.logger import logger
from leapx.pipeline.core.pool_manager import PoolManager
from leapx.pipeline.stages.configs.llm_extraction_config import LLMExtractionConfig
from leapx.pipeline.stages.constants import (
    COMBINED_TEXT,
    CONTENT,
    EXTRACTION_RESPONSE,
    INPUT_TEXT_LENGTH,
    JSON_SCHEMA,
    LAYOUT_PARSING,
    OUTPUT,
    RESPONSE_MODEL,
    STATUS_COMPLETED,
    SYSTEM_PROMPT,
    USER_INSTRUCTIONS,
    USER_PROMPT,
)
from leapx.pipeline.stages.exceptions import MissingInputForExtractionError
from leapx.pipeline.stages.extraction.base import BaseExtractionStage
from leapx.pipeline.stages.schemas import StageName, StageOutput
from leapx.services.extractor.extractor_factory import ExtractorFactory
from leapx.services.extractor.schemas import ExtractionRequest
from leapx.services.schema_generator import create_model


class LLMExtractionStage(BaseExtractionStage):
    """Standard LLM-based extraction.

    Args:
        extractor_service (ExtractorInterface): Service that performs
            extraction via LLM.
        config (PipelineConfig): Pipeline configuration providing extraction
            parameters.

    Attributes:
        extractor_service (ExtractorInterface): The extractor client.
        config (PipelineConfig): Configuration used to build extraction
            requests.
    """

    def __init__(
        self,
        config: LLMExtractionConfig,
        pool_manager: PoolManager | None = None,
        stage_id: str | None = None,
        use_llm_limit: bool = True,
    ):
        super().__init__(config, stage_id)
        self.extractor_service = ExtractorFactory.create(
            provider=config.provider,
            cache_config=config.cache_config,
        )
        self.pool_manager = pool_manager
        self.use_llm_limit = use_llm_limit

    async def execute(self, text: str) -> dict[str, Any]:
        """Extract using LLM.

        Args:
            text (str): Input text content to extract fields from.

        Returns:
            dict[str, Any]: Structured extraction result from the LLM.
        """
        extraction_config = self.config.llm_extraction_config
        extraction_config["user_prompt"]["content"] = text
        request = ExtractionRequest(**extraction_config)
        return await self.extractor_service.extract(request)

    async def execute_dynamic(
        self,
        chunk: Any,
        previous_output: dict[str, dict],
        config: dict[str, Any],
    ) -> StageOutput:
        """Extract structured data from parsed text or direct text input.

        Args:
            chunk: ChunkResult (may contain text_content for TEXT input type).
            previous_outputs: Must contain layout parsing output with combined_text
                (for FILE input type). May also contain _previous_chunk_context.
            config: Additional extraction configuration overrides.

        Returns:
            StageOutput with extraction response.

        Raises:
            ValueError: If no text input is available.
        """
        combined_text = self._find_combined_text(chunk, previous_output)

        if combined_text is None:
            raise MissingInputForExtractionError

        context_info = self._extract_context_info(previous_output)

        extraction_config = self.config.get_extraction_config()

        user_instructions = extraction_config[USER_PROMPT][USER_INSTRUCTIONS]
        user_content = self._build_context_aware_prompt(
            combined_text, context_info, user_instructions
        )
        extraction_config[USER_PROMPT][CONTENT] = user_content

        if self.stage_config:
            if JSON_SCHEMA in self.stage_config:
                schema = self.stage_config[JSON_SCHEMA]
                if isinstance(schema, dict):
                    extraction_config[RESPONSE_MODEL] = create_model(schema=schema)
                else:
                    extraction_config[RESPONSE_MODEL] = schema
            if SYSTEM_PROMPT in self.stage_config:
                prompt = self.stage_config[SYSTEM_PROMPT]
                if isinstance(prompt, str):
                    extraction_config[SYSTEM_PROMPT] = {CONTENT: prompt}
                else:
                    extraction_config[SYSTEM_PROMPT] = prompt

        extraction_config.update(config)
        extraction_request = ExtractionRequest(**extraction_config)
        if self.use_llm_limit:
            extraction_response = await self.pool_manager.run_with_llm_limit(
                self.extractor_service.extract(extraction_request)
            )
        else:
            extraction_response = await self.extractor_service.extract(
                extraction_request
            )
        logger.stage_log(
            stage_name=StageName.extraction,
            status=STATUS_COMPLETED,
            stage_id=self.stage_id,
        )

        return StageOutput(
            data={
                EXTRACTION_RESPONSE: extraction_response,
                INPUT_TEXT_LENGTH: len(combined_text),
            },
            metadata={
                INPUT_TEXT_LENGTH: len(combined_text),
                "has_context": context_info["has_context"],
            },
            context=context_info,
        )

    def _find_combined_text(
        self, chunk: Any, previous_outputs: dict[str, Any]
    ) -> str | None:
        """Find combined text from chunk or previous stages.

        Args:
            chunk: ChunkResult that may contain text_content.
            previous_outputs: Outputs from previous stages.

        Returns:
            Combined text string or None if not found.
        """
        if hasattr(chunk, "text_content") and chunk.text_content is not None:
            return chunk.text_content

        # Direct lookup by common layout stage ID
        if LAYOUT_PARSING in previous_outputs:
            return previous_outputs[LAYOUT_PARSING].get(OUTPUT).get(COMBINED_TEXT)

        for output in previous_outputs.values():
            if isinstance(output, dict):
                if OUTPUT in output and COMBINED_TEXT in output.get(OUTPUT):
                    return output.get(OUTPUT)[COMBINED_TEXT]
                if COMBINED_TEXT in output:
                    return output.get(COMBINED_TEXT)

        return chunk.text_content

    def _extract_context_info(self, previous_outputs: dict[str, Any]) -> dict[str, Any]:
        """Extract context information from previous chunks.

        Args:
            previous_outputs: Outputs from previous stages and chunks.

        Returns:
            Dictionary containing context information.
        """
        context_info = {
            "has_context": False,
            "previous_parsed_texts": [],
            "previous_llm_outputs": [],
            "previous_chunk_index": None,
        }
        # Check if previous chunk context exists
        prev_context = previous_outputs.get("_previous_chunk_context")
        if not prev_context:
            return context_info

        context_info["has_context"] = True
        context_info["previous_chunk_index"] = prev_context.get("chunk_index")

        stages = prev_context.get("stages", {})

        parser_output = stages.get("parsing", {}).get("output", {})
        if COMBINED_TEXT in parser_output:
            context_info["previous_parsed_texts"].append(parser_output[COMBINED_TEXT])

        extraction_output = stages.get("extraction", {}).get("output", {})
        if EXTRACTION_RESPONSE in extraction_output:
            context_info["previous_llm_outputs"].append(
                extraction_output[EXTRACTION_RESPONSE]
            )

        return context_info

    def _build_context_aware_prompt(
        self,
        current_text: str,
        context_info: dict[str, Any],
        user_instructions: str = "",
    ) -> str:
        """Build a context-aware prompt including previous chunk information.

        Args:
            current_text: Current chunk's parsed text.
            context_info: Context information from previous chunks.
            user_instructions: Task instructions from the extraction config.

        Returns:
            Enhanced prompt with context.
        """
        prompt_parts = []

        if user_instructions:
            prompt_parts.append(f"Additional Instructions: {user_instructions}\n\n")

        # Add previous parsed texts if available
        if context_info["previous_parsed_texts"]:
            prompt_parts.append("=== PREVIOUS CHUNK TEXT ===")
            for _i, prev_text in enumerate(context_info["previous_parsed_texts"]):
                prompt_parts.append("Previous Chunk")
                prompt_parts.append("```")
                prompt_parts.append(prev_text)
                prompt_parts.append("```")
            prompt_parts.append("")

        # Add previous LLM outputs if available
        if context_info["previous_llm_outputs"]:
            prompt_parts.append("=== PREVIOUS EXTRACTION RESULTS ===")
            for i, prev_output in enumerate(context_info["previous_llm_outputs"]):
                prompt_parts.append(f"[Previous Result {i}]")
                prompt_parts.append("```")
                prompt_parts.append(str(prev_output))
                prompt_parts.append("```")
            prompt_parts.append("")

        # Add current chunk
        prompt_parts.append("=== CURRENT CHUNK TEXT ===")
        prompt_parts.append("```")
        prompt_parts.append(current_text)
        prompt_parts.append("```")

        return "\n".join(prompt_parts)

    async def close(self) -> None:
        """Cleanup extractor resources."""
        self.extractor_service.close()
