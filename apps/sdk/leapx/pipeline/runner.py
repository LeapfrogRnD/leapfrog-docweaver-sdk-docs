# leapx/pipeline/factory.py
"""Factory functions to create and run LeapX pipelines."""

from enum import Enum
from typing import Any

from pydantic import BaseModel

from leapx.common.cache.cache_config import CacheConfig
from leapx.common.types.providers import OCRProviderType, ParsingMethod
from leapx.pipeline.core.error_handler import PipelineErrorHandler
from leapx.pipeline.core.pipeline import LeapXPipeline
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.configs import (
    LLMExtractionConfig,
    OCRConfig,
    ParserConfig,
    VLMConfig,
)
from leapx.pipeline.stages.configs.llm_generation_config import LLMGenerationConfig
from leapx.pipeline.stages.constants import (
    CHUNKING_CONFIG,
    DEFAULT_CLASSIFICATION_SYSTEM_PROMPT,
    DEFAULT_EXTRACTION_SYSTEM_PROMPT,
    DEFAULT_GENERATION_SYSTEM_PROMPT,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROCESS_TYPE,
    DEFAULT_TEMPERATURE,
    DEFAULT_VLM_EXTRACTION_METHOD,
    DEFAULT_VLM_MODEL,
    EXTRACTOR_PROVIDER,
    LLM_CACHE_CONFIG,
    LLM_MODEL,
    LLM_PROVIDER,
    LLM_PROVIDER_CREDENTIAL,
    MAX_TOKENS,
    OCR_CACHE_CONFIG,
    OCR_CREDENTIAL,
    OCR_PROVIDER,
    PARSER,
    TEMPERATURE,
    TYPE,
    VLM_EXTRACTION_METHOD,
    VLM_EXTRACTION_PROMPTS,
    VLM_MODEL,
)
from leapx.pipeline.stages.exceptions import InvalidStageError, MissingStageError
from leapx.pipeline.stages.layers import Stage
from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential
from leapx.services.extractor.extractor_factory import ExtractorProvider


def _validate_stages(stages: list[BaseStage | Enum]) -> dict[str, bool]:
    """Validate stage combinations and return configuration flags.

    Args:
        stages: List of stage enums or instances to validate

    Returns:
        Dictionary with has_ocr, has_vlm, has_parser flags

    Raises:
        InvalidStageConfigurationError: If stage combination is invalid
    """
    # Validate stage combinations
    has_ocr = Stage.OCR in stages
    has_vlm = Stage.VLM_PARSER in stages
    has_parser = Stage.PARSER in stages
    has_llm = Stage.LLM_EXTRACTION in stages
    has_generation = Stage.LLM_GENERATION in stages

    # At least one extraction method required (OCR or VLM)
    if not has_ocr and not has_vlm:
        raise InvalidStageError("At least one of OCR or VLM must be included in stages")  # noqa: TRY003

    # OCR and VLM are mutually exclusive
    if has_ocr and has_vlm:
        raise InvalidStageError("OCR and VLM cannot be used at the same time")  # noqa: TRY003

    # OCR requires Parser
    if has_ocr and not has_parser:
        raise InvalidStageError("Parser must be used when OCR is enabled")  # noqa: TRY003

    # VLM cannot use Parser
    if has_vlm and has_parser:
        raise InvalidStageError("VLM and Parser cannot be used at the same time")  # noqa: TRY003

    return {
        "has_ocr": has_ocr,
        "has_vlm": has_vlm,
        "has_parser": has_parser,
        "has_llm": has_llm,
        "has_generation": has_generation,
    }


def linear_pipeline(
    json_schema: type[BaseModel] | dict[str, Any],
    additional_instructions: str | None = None,
    stages: list[BaseStage | Enum] | None = None,
    enable_context: bool = False,
    **kwargs,
) -> LeapXPipeline:
    """
    Create a LeapXPipeline instance with linear stage dependencies.

    Args:
        json_schema: Pydantic model or dict describing expected output.
        additional_instructions: Optional string with extra instructions for LLM stages.
        stages: Optional list of Stage enums or BaseStage instances.
                If None, uses default [OCR, PARSER, LLM_EXTRACTION] stages.
        enable_context: boolean field to check the context status
        **kwargs: Additional configuration options.

    Returns:
        LeapXPipeline: Configured pipeline instance.

    Raises:
        InvalidStageConfigurationError: If stage combination is invalid.

    Example:
        # Simplest usage - uses default stages
        pipeline = linear_pipeline(
            json_schema=MySchema,
            additional_instructions="Extract the data",
        )

        # With Stage enums
        pipeline = linear_pipeline(
            json_schema=MySchema,
            additional_instructions="Extract the data",
            stages=[Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION],
        )
    """
    # If stages are Stage enums, we'll let LeapXPipeline build default stages
    # since Stage enums hold classes that need complex initialization
    use_default_stages = stages is None or not all(isinstance(s, Enum) for s in stages)

    # additional instructions is compulsory for generation stage
    if (
        stages
        and Stage.LLM_GENERATION in stages
        and (additional_instructions is None or additional_instructions.strip() == "")
    ):
        raise ValueError(  # noqa: TRY003
            "Additional instructions must be provided for generation stage"
        )

    # Validate stage combinations
    stage_flags = _validate_stages(stages)
    has_vlm = stage_flags["has_vlm"]
    has_llm = stage_flags["has_llm"]
    has_generation = stage_flags["has_generation"]

    try:
        llm_cred = kwargs.pop(LLM_PROVIDER_CREDENTIAL, None)
        llm_cfg = None
        llm_gen_cfg = None

        if has_llm:
            process_type = kwargs.pop(TYPE, DEFAULT_PROCESS_TYPE)
            if process_type == DEFAULT_PROCESS_TYPE:
                base_prompt = DEFAULT_EXTRACTION_SYSTEM_PROMPT
            else:
                base_prompt = DEFAULT_CLASSIFICATION_SYSTEM_PROMPT

            llm_cfg = LLMExtractionConfig(
                model=kwargs.pop(LLM_MODEL, DEFAULT_LLM_MODEL),
                credential=llm_cred,
                system_prompt=base_prompt,
                user_instructions=additional_instructions or "",
                temperature=kwargs.pop(TEMPERATURE, DEFAULT_TEMPERATURE),
                max_tokens=kwargs.pop(MAX_TOKENS, DEFAULT_MAX_TOKENS),
                llm_provider=kwargs.pop(LLM_PROVIDER, DEFAULT_LLM_PROVIDER),
                cache_config=kwargs.pop(LLM_CACHE_CONFIG, None) or CacheConfig(),
                provider=kwargs.pop(EXTRACTOR_PROVIDER, ExtractorProvider.LITE_LLM),
                json_schema=json_schema,
            )

        if has_generation:
            base_prompt = DEFAULT_GENERATION_SYSTEM_PROMPT
            llm_gen_cfg = LLMGenerationConfig(
                model=kwargs.pop(LLM_MODEL, DEFAULT_LLM_MODEL),
                credential=llm_cred,
                system_prompt=base_prompt,
                user_instructions=additional_instructions or "",
                temperature=kwargs.pop(TEMPERATURE, DEFAULT_TEMPERATURE),
                max_tokens=kwargs.pop(MAX_TOKENS, DEFAULT_MAX_TOKENS),
                llm_provider=kwargs.pop(LLM_PROVIDER, DEFAULT_LLM_PROVIDER),
            )

        # Create VLM config if VLM stage is present
        vlm_cfg = ocr_cfg = parser_cfg = None

        if has_vlm:
            vlm_cfg = VLMConfig(
                model=kwargs.pop(VLM_MODEL, DEFAULT_VLM_MODEL),
                extraction_type=kwargs.pop(
                    VLM_EXTRACTION_METHOD, DEFAULT_VLM_EXTRACTION_METHOD
                ),
                extraction_prompt=VLM_EXTRACTION_PROMPTS,
            )
        else:
            # Create OCR and Parser configs
            ocr_cfg = OCRConfig(
                provider=kwargs.pop(OCR_PROVIDER, OCRProviderType.AWS_TEXTRACT),
                credential=kwargs.pop(OCR_CREDENTIAL, None),
                cache_config=kwargs.pop(OCR_CACHE_CONFIG, None) or CacheConfig(),
            )
            parser_cfg = ParserConfig(
                method=kwargs.pop(PARSER, ParsingMethod.LAYOUT_CONSERVED)
            )

        chunking_cfg = kwargs.pop(CHUNKING_CONFIG, None)

        if use_default_stages:
            return LeapXPipeline(
                ocr=ocr_cfg,
                llm=llm_cfg,
                llm_gen=llm_gen_cfg,
                parser=parser_cfg,
                vlm=vlm_cfg,
                chunking_config=chunking_cfg,
                enable_context=enable_context,
            )
        stages = [stage.value for stage in stages]
        for i in range(1, len(stages)):
            stages[i].after(stages[i - 1])
        return LeapXPipeline(
            ocr=ocr_cfg,
            llm=llm_cfg,
            llm_gen=llm_gen_cfg,
            vlm=vlm_cfg,
            parser=parser_cfg,
            stages=stages,
            chunking_config=chunking_cfg,
            enable_context=enable_context,
        )
    except InvalidStageError:
        raise
    except Exception as exc:
        PipelineErrorHandler.handle_initialization_error(exc)
        raise


def dag_pipeline(
    json_schema: type[BaseModel] | dict[str, Any],
    system_prompt: str,
    stages: list[BaseStage],
    **kwargs,
) -> LeapXPipeline:
    """
    Create a LeapXPipeline instance with custom DAG stage dependencies.

    Stages should define their own dependencies using the .after() method before
    passing them to this function. This allows for complex dependency graphs with
    multiple dependencies per stage.

    Args:
        json_schema: Pydantic model or dict describing expected output.
        system_prompt: System prompt for LLM extraction.
        stages: List of stage instances with pre-configured dependencies.
        **kwargs: Additional configuration options.

    Returns:
        LeapXPipeline: Configured pipeline instance.

    Example:
        ocr_stage = OCRStage(config=ocr_cfg)
        parser_stage = ParserStage(config=parser_cfg).after(ocr_stage)
        llm_stage = LLMStage(config=llm_cfg).after(parser_stage)
        merge_stage = MergeStage(config=merge_cfg).after(ocr_stage, parser_stage)

        pipeline = dag_pipeline(
            json_schema=schema,
            system_prompt=prompt,
            stages=[ocr_stage, parser_stage, llm_stage, merge_stage]
        )
    """
    if not stages:
        raise MissingStageError

    try:
        # Extract configurations from stages for pipeline initialization
        ocr_cfg = None
        parser_cfg = None
        llm_cfg = None
        vlm_cfg = None
        for stage in stages:
            if hasattr(stage, "config"):
                config = stage.config
                if hasattr(config, "provider"):  # OCRConfig
                    ocr_cfg = config
                elif hasattr(config, "parser"):  # ParserConfig
                    parser_cfg = config
                elif hasattr(config, "model"):  # LLMConfig
                    llm_cfg = config
                elif hasattr(config, "vlm_provider"):  # VLMConfig
                    vlm_cfg = config
        # Build default configs if not found in stages
        if not llm_cfg:
            llm_cred = kwargs.pop(LLM_PROVIDER_CREDENTIAL, None) or BedrockCredential()
            llm_cfg = LLMExtractionConfig(
                model=kwargs.pop(LLM_MODEL, DEFAULT_LLM_MODEL),
                provider=kwargs.pop(EXTRACTOR_PROVIDER, ExtractorProvider.LITE_LLM),
                credential=llm_cred,
                system_prompt=system_prompt,
                temperature=kwargs.pop(TEMPERATURE, DEFAULT_TEMPERATURE),
                max_tokens=kwargs.pop(MAX_TOKENS, DEFAULT_MAX_TOKENS),
                cache_config=kwargs.pop(LLM_CACHE_CONFIG, None) or CacheConfig(),
                json_schema=json_schema,
            )
        if not vlm_cfg:
            vlm_cfg = VLMConfig(
                model=kwargs.pop(VLM_MODEL, DEFAULT_VLM_MODEL),
                extraction_type=kwargs.pop(
                    VLM_EXTRACTION_METHOD, DEFAULT_VLM_EXTRACTION_METHOD
                ),
                extraction_prompt=VLM_EXTRACTION_PROMPTS,
            )

        return LeapXPipeline(
            ocr=ocr_cfg
            or OCRConfig(
                provider=OCRProviderType.AWS_TEXTRACT,
                credential=AwsOcrCredential(),
                cache_config=CacheConfig(),
            ),
            llm=llm_cfg,
            vlm=vlm_cfg,
            parser=parser_cfg or ParserConfig(method=ParsingMethod.LAYOUT_CONSERVED),
            stages=stages,
        )

    except Exception as exc:
        PipelineErrorHandler.handle_initialization_error(exc)
        raise
