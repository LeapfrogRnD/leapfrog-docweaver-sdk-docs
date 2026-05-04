"""Base stage interface.

This module defines the abstract BaseStage class used to implement pipeline stages.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from leapx.common.observability import logger
from leapx.pipeline.core.config import PipelineConfig
from leapx.pipeline.stages.schemas import StageName, StageOutput, StageResult, StageType


class BaseStage[InputT, OutputT](ABC):
    """Abstract base for all pipeline stages.

    Type Parameters:
        InputT: The input data type accepted by the stage.
        OutputT: The output data type produced by the stage.

    """

    _dependencies: ClassVar[list[type["BaseStage"]]] = []
    _custom_stage_id: ClassVar[str | None] = None
    _stage_config: ClassVar[dict[str, Any]] = {}

    def __init__(self, config: PipelineConfig, stage_id: str | None = None):
        """Initialize stage with optional custom ID.

        Args:
            stage_id: Unique identifier for this stage instance.
            config: passes pipelineconfig instance
                     Defaults to the stage's default name.
        """
        self.config = config
        if isinstance(stage_id, StageName):
            stage_id = stage_id.value

        self._stage_id = stage_id or self._custom_stage_id or self.name
        self._instance_stage_config = dict(self._stage_config)

    def __init_subclass__(cls, **kwargs):
        """Initialize each subclass with its own dependencies list."""
        super().__init_subclass__(**kwargs)
        if (
            not hasattr(cls, "_dependencies")
            or cls._dependencies is BaseStage._dependencies
        ):
            cls._dependencies = []
        if not hasattr(cls, "_custom_stage_id"):
            cls._custom_stage_id = None
        if not hasattr(cls, "_stage_config"):
            cls._stage_config = {}

    @property
    def stage_id(self) -> str:
        """Unique identifier for this stage instance."""
        return self._stage_id

    @property
    def dependencies(self) -> list["BaseStage"]:
        """Get the list of stages this stage depends on."""
        return self._dependencies

    @classmethod
    def after(cls, *stages: type["BaseStage"]) -> type["BaseStage"]:
        """Define dependencies for this stage.

        Args:
            *stages: One or more stage classes that must complete before this stage.

        Returns:
            A new subclass with the dependencies set.

        Example:
            ParserStage.after(OCRStage)
            MergeStage.after(OCRStage, ParserStage)
        """
        return type(
            cls.__name__,
            (cls,),
            {
                "_dependencies": list(stages),
                "_custom_stage_id": getattr(cls, "_custom_stage_id", None),
            },
        )

    @classmethod
    def with_id(cls, stage_id: str) -> type["BaseStage"]:
        """Set a custom stage ID for this stage.

        This is useful when you need multiple instances of the same stage type
        with different configurations (e.g., two LLM extraction stages).

        Args:
            stage_id: Unique identifier for this stage instance.

        Returns:
            A new subclass with the custom stage_id set.

        Example:
            LLMExtractionStage.after(OCRStage).with_id("classification")
        """
        return type(
            cls.__name__,
            (cls,),
            {
                "_dependencies": getattr(cls, "_dependencies", []),
                "_custom_stage_id": stage_id,
                "_stage_config": getattr(cls, "_stage_config", {}),
            },
        )

    @classmethod
    def with_config(cls, **config: Any) -> type["BaseStage"]:
        """Set custom configuration for this stage.

        This allows passing stage-specific configuration like different
        schemas or prompts for LLM extraction stages.

        Args:
            **config: Key-value configuration options for the stage.

        Returns:
            A new subclass with the configuration set.

        Example:
            LLMExtractionStage.after(ParserStage).with_id("metadata").with_config(
                json_schema=MetadataSchema.model_json_schema(),
                system_prompt="Extract metadata from the document."
            )
        """
        existing_config = dict(getattr(cls, "_stage_config", {}))
        existing_config.update(config)

        return type(
            cls.__name__,
            (cls,),
            {
                "_dependencies": getattr(cls, "_dependencies", []),
                "_custom_stage_id": getattr(cls, "_custom_stage_id", None),
                "_stage_config": existing_config,
            },
        )

    @property
    def stage_config(self) -> dict[str, Any]:
        """Get the stage-specific configuration."""
        return self._instance_stage_config

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the stage identifier.

        Returns:
            str: Human-readable unique identifier of the stage.
        """
        pass

    @property
    @abstractmethod
    def stage_type(self) -> StageType:
        """Get the execution type of the stage.

        Returns:
            StageType: The execution classification (e.g., CPU, IO, ASYNC).
        """
        pass

    @abstractmethod
    async def execute(self, input_data: InputT) -> OutputT:
        """Execute the stage logic.

        Args:
            input_data (InputT): The input payload for the stage.

        Returns:
            OutputT: The result produced by the stage.
        """
        pass

    async def execute_dynamic(
        self,
        chunk: Any,
        previous_output: dict[str, dict],  # noqa: ARG002
        config: dict[str, Any],  # noqa: ARG002
    ) -> StageOutput:
        """Execute the stage in dynamic pipeline mode.

        Override this method to support dynamic pipeline execution.

        Args:
            chunk: The chunk being processed (ChunkResult).
            previous_outputs: Dict mapping stage_id -> output_data from prior stages.
            config: Stage-specific configuration.

        Returns:
            StageOutput containing the result data and metadata.
        """
        # Default implementation calls the standard execute method
        output = await self.execute(chunk)
        return StageOutput(data={"result": output}, metadata={})

    async def run(self, input_data: InputT) -> StageResult:
        """Run the stage and wrap the result in a StageResult.

        Args:
            input_data (InputT): The input payload for the stage.

        Returns:
            StageResult: A wrapper containing the stage name, output data and status.
        """
        try:
            output = await self.execute(input_data)
            return StageResult(stage_name=self.name, data=output)
        except Exception as e:
            logger.logger.error("Stage %s failed", self.name)
            return StageResult(
                stage_name=self.name,
                data=None,
                success=False,
                error=str(e),
            )

    def get_dependency_output(
        self,
        previous_outputs: dict[str, dict],
        dependency_class: type["BaseStage"] | None = None,
        output_key: str | None = None,
    ) -> dict | Any | None:
        """Get output from a dependency stage.

        This method searches for outputs from dependencies in order:
        1. By the dependency class's default name (e.g., "ocr", "parsing")
        2. By searching all outputs for a specific key
        3. By returning any output from a matching dependency class

        Args:
            previous_outputs: Dict mapping stage_id -> output_data from prior stages.
            dependency_class: Optional specific dependency class to find output for.
            output_key: Optional specific key to look for in outputs.

        Returns:
            The dependency output dict, or the specific value if output_key provided.
        """
        if output_key:
            for output in previous_outputs.values():
                if isinstance(output, dict) and output_key in output:
                    return output[output_key]
            return None

        if dependency_class:
            try:
                default_name = (
                    dependency_class(None).name
                    if hasattr(dependency_class, "name")
                    else None
                )
            except Exception:
                default_name = None

            if default_name and default_name in previous_outputs:
                return previous_outputs[default_name]

        for output in previous_outputs.values():
            if isinstance(output, dict):
                return output

        return None
