from typing import Any

from leapx.common.observability.logger import logger
from leapx.pipeline.core.pool_manager import PoolManager
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.configs.llm_generation_config import LLMGenerationConfig
from leapx.pipeline.stages.constants import (
    COMBINED_TEXT,
    CONTENT,
    INPUT_TEXT_LENGTH,
    LAYOUT_PARSING,
    OUTPUT,
    RESPONSE_MODEL,
    STATUS_COMPLETED,
    SYSTEM_PROMPT,
    USER_INSTRUCTIONS,
    USER_PROMPT,
)
from leapx.pipeline.stages.schemas import StageName, StageOutput, StageType
from leapx.services.generator.exceptions.generator_exceptions import (
    MissingInputForGenerationError,
)
from leapx.services.generator.generator_factory import GeneratorFactory
from leapx.services.generator.schemas import GenerationRequest


class LLMGenerationStage(BaseStage):
    """
    Initializes the LLM generation stage.

    Args:
        config (LLMGenerationConfig): Configuration for the LLM generation
            process, including provider and cache settings.
        pool_manager (PoolManager | None, optional): Optional pool manager
            for managing resource pools. Defaults to None.
        stage_id (str | None, optional): Optional identifier for the stage.
            Defaults to None.
        use_llm_limit (bool, optional): Flag to enforce LLM usage limits.
            Defaults to True.

    Attributes:
        generator_service (GeneratorInterface): Service for LLM-based
            generation.
        pool_manager (PoolManager | None): Manages resource pools if provided.
        use_llm_limit (bool): Indicates whether LLM usage limits are enforced.
    """

    def __init__(
        self,
        config: LLMGenerationConfig,
        pool_manager: PoolManager | None = None,
        stage_id: str | None = None,
        use_llm_limit: bool = True,
    ):
        super().__init__(config, stage_id)
        self.generator_service = GeneratorFactory.create(
            provider=config.provider,
        )
        self.pool_manager = pool_manager
        self.use_llm_limit = use_llm_limit

    @property
    def name(self) -> str:
        """Get stage identifier."""
        return StageName.generation

    @property
    def stage_type(self) -> StageType:
        """Get execution type.

        Returns:
            StageType: IO-bound stage type.
        """
        return StageType.IO

    async def execute(self, text) -> dict[str, Any]:
        """Summarize using LLM.

        Args:
            text (str): Input text content to summarize

        Returns:
            dict[str, Any]: Structured generation result from the LLM.
        """
        generation_config = self.config.get_generation_config()
        generation_config["user_prompt"]["content"] = text
        request = GenerationRequest(**generation_config)
        return await self.generator_service.generate(request)

    async def execute_dynamic(
        self,
        chunk: Any,
        previous_output: dict[str, dict],
        config: dict[str, Any],
    ) -> StageOutput:
        """Generate the summary from parsed text or direct text input.

        Args:
            chunk: ChunkResult (may contain text_content for TEXT input type).
            previous_output: Must contain layout parsing output with combined_text
                (for FILE input type). May also contain _previous_chunk_context.
            config: Additional generation configuration overrides.

        Returns:
            StageOutput with generation response.

        Raises:
            MissingInputForGenerationError: If no text input is available.
        """
        combined_text = self._find_combined_text(chunk, previous_output)

        if combined_text is None:
            raise MissingInputForGenerationError

        context_info = self._extract_context_info(previous_output)

        generation_config = self.config.get_generation_config()

        user_instructions = generation_config[USER_PROMPT][USER_INSTRUCTIONS]
        user_content = self._build_context_aware_prompt(
            combined_text, context_info, user_instructions
        )
        generation_config[USER_PROMPT][CONTENT] = user_content

        # Override with stage-specific config for system prompt only
        if self.stage_config and SYSTEM_PROMPT in self.stage_config:
            prompt = self.stage_config[SYSTEM_PROMPT]
            if isinstance(prompt, str):
                generation_config[SYSTEM_PROMPT] = {CONTENT: prompt}
            else:
                generation_config[SYSTEM_PROMPT] = prompt

        # Apply runtime config overrides (excluding response_model)
        config_without_model = {k: v for k, v in config.items() if k != RESPONSE_MODEL}
        generation_config.update(config_without_model)

        generation_request = GenerationRequest(**generation_config)

        if self.use_llm_limit and self.pool_manager:
            generation_response = await self.pool_manager.run_with_llm_limit(
                self.generator_service.generate(generation_request)
            )
        else:
            generation_response = await self.generator_service.generate(
                generation_request
            )

        logger.stage_log(
            stage_name=StageName.generation,
            status=STATUS_COMPLETED,
            stage_id=self.stage_id,
        )

        return StageOutput(
            data={
                "generation_response": generation_response.data,
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
            layout_output = previous_outputs[LAYOUT_PARSING].get(OUTPUT)
            if layout_output and COMBINED_TEXT in layout_output:
                return layout_output.get(COMBINED_TEXT)

        # Fallback: search all outputs
        for output in previous_outputs.values():
            if isinstance(output, dict):
                if COMBINED_TEXT in output:
                    return output[COMBINED_TEXT]
                if (
                    OUTPUT in output
                    and isinstance(output[OUTPUT], dict)
                    and COMBINED_TEXT in output[OUTPUT]
                ):
                    return output[OUTPUT][COMBINED_TEXT]

        return None

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
            "previous_generation_outputs": [],
            "previous_chunk_index": None,
        }

        # Check if previous chunk context exists
        prev_context = previous_outputs.get("_previous_chunk_context")
        if not prev_context:
            return context_info

        context_info["has_context"] = True
        context_info["previous_chunk_index"] = prev_context.get("chunk_index")

        stages = prev_context.get("stages", {})

        # Extract previous parsing output
        parser_output = stages.get("parsing", {}).get("output", {})
        if COMBINED_TEXT in parser_output:
            context_info["previous_parsed_texts"].append(parser_output[COMBINED_TEXT])

        # Extract previous generation output
        generation_output = stages.get("generation", {}).get("output", {})
        if "generation_response" in generation_output:
            context_info["previous_generation_outputs"].append(
                generation_output["generation_response"]
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
            user_instructions: Task instructions from the generation config.

        Returns:
            Enhanced prompt with context.
        """
        prompt_parts = []

        if user_instructions:
            prompt_parts.append(f"User Task: {user_instructions}\n\n")

        # Add previous generation outputs if available
        if context_info["previous_generation_outputs"]:
            prev_output = "\n".join(
                str(o) for o in context_info["previous_generation_outputs"]
            )
            prompt_parts.append("Previous output")
            prompt_parts.append("```")
            prompt_parts.append(prev_output)
            prompt_parts.append("```")

        # Add current chunk
        prompt_parts.append("\n\nCurrent chunk")
        prompt_parts.append("```")
        prompt_parts.append(current_text)
        prompt_parts.append("```")

        return "\n".join(prompt_parts)

    async def close(self) -> None:
        """Cleanup generator resources."""
        if hasattr(self.generator_service, "close"):
            self.generator_service.close()
