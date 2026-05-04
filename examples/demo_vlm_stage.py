"""
Async Demo - LeapX Pipeline with Async Support using VLMStage
"""

import asyncio
import json
from pathlib import Path

from pydantic import BaseModel, Field

from leapx import Stage, linear_pipeline
from leapx.pipeline.core.config import PipelineConfig
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.vlm_stage import VLMStage


# class DocumentClassifier(BaseModel):
class DocumentClassifier(BaseModel):
    title: str = Field(..., description="title of the chunk")


class SimpleLinearPipeline:
    """
    Minimal linear pipeline runner for async stages.
    """

    def __init__(self, stages: list[BaseStage]):
        self.stages = stages

    async def async_run(self, content: bytes | str):
        data = content
        for stage in self.stages:
            if isinstance(data, bytes):
                data = await stage.execute(data)
            else:
                # For text input
                data = await stage.execute(data.encode("utf-8"))
        return data


async def demo_linear_pipeline():
    additional_instruction = (
        "Please read the text carefully and extract the required fields."
    )
    stages = [Stage.VLM_PARSER, Stage.LLM_EXTRACTION]
    # Create linear pipeline (can add OCRStage, ParserStage later)

    # Sample document file

    extraction_pipeline = linear_pipeline(
        json_schema=DocumentClassifier.model_json_schema(),
        additional_instructions=additional_instruction,
        stages=stages,
        max_tokens=15000,
    )
    result = await extraction_pipeline.async_run("samples/add.pdf")

    Path("extraction_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return result


async def demo_linear_pipeline_with_text():
    config = PipelineConfig()
    vlm_stage = VLMStage(config)

    stages = [vlm_stage]
    pipeline = SimpleLinearPipeline(stages=stages)

    sample_text = """
    Document Title: Employee Handbook 2024

    This handbook contains policies and procedures for all employees.
    Please review carefully and acknowledge receipt.
    """

    result = await pipeline.async_run(sample_text)

    Path("extraction_result_text.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return result


async def main():
    try:
        await demo_linear_pipeline()

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
