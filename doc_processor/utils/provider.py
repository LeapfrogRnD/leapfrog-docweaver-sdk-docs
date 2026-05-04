from leapx import Stage
from shared.constants.app_constants import LLMProviders


def get_llm_provider(llm_model: str) -> str:
    """
    Determine LLM provider based on model name.

    Args:
        llm_model: Name of the LLM model

    Returns:
        Provider name ('openai' or 'bedrock')
    """

    if llm_model and "gpt" in llm_model.lower():
        return LLMProviders.OPENAI
    return LLMProviders.BEDROCK


def build_pipeline_kwargs(
    config: dict | None = None, use_generation: bool = False
) -> dict:
    """
    Build pipeline arguments

    """

    config = config or {}

    def use_vlm(ocr_provider):
        stages = (
            [Stage.VLM_PARSER] if ocr_provider == "vlm" else [Stage.OCR, Stage.PARSER]
        )

        (
            stages.append(Stage.LLM_GENERATION)
            if use_generation
            else stages.append(Stage.LLM_EXTRACTION)
        )
        return stages

    llm_model = config.get("llm_model")
    ocr_provider = config.get("ocr_provider")
    json_schema = config.get("formatted_json_schema")
    additional_instruction = config.get("additional_instruction")
    if use_generation:
        base_instruction = "Task: Please provide summary of given context"
        if not additional_instruction or additional_instruction.strip() == "":
            additional_instruction = base_instruction
        else:
            additional_instruction = (
                base_instruction + "\nAdditional Instruction: " + additional_instruction
            )

    task_metadata = config.get("task_metadata") or {}
    enable_context = task_metadata.get("enable_context", True)
    batch_size = task_metadata.get("batch_size", 1)
    stages = use_vlm(ocr_provider)

    pipeline_kwargs = {
        "json_schema": json_schema,
        "additional_instructions": additional_instruction,
        "llm_model": llm_model,
        "llm_provider": get_llm_provider(llm_model) if llm_model else None,
        "stages": stages,
        "max_tokens": 30000,
        "chunking_config": {"batch_size": batch_size},
        "llm_cache_config": {"enabled": False},
        "ocr_cache_config": {"enabled": False},
        "enable_context": enable_context,
    }
    if ocr_provider and ocr_provider != "vlm":
        pipeline_kwargs["ocr_provider"] = ocr_provider
    return pipeline_kwargs
