"""
Async Demo - LeapX Pipeline with Async Support
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from leapx import Stage, linear_pipeline


class DocumentClassifier(BaseModel):
    title: str = Field(..., description="title of the chunk")


class ClassifierEnum(Enum):
    REFERRAL = "referral"
    PRESCRIPTION = "prescription"
    MEDICAL_RECORD = "medical_record"
    LAB_RESULT = "lab_result"
    INSURANCE_CARD = "insurance_card"
    ID_DOCUMENT = "id_document"
    INSURANCE_AUTHORIZATION = "insurance_authorization"
    MEDICAL_FORM = "medical_form"
    DISCHARGE_SUMMARY = "discharge_summary"
    OTHER = "other"


class ReferralPatient(BaseModel):
    patient_first_name: str = Field(..., description="First name of the patient")
    patient_last_name: str = Field(..., description="Last name of the patient")
    patient_dob: datetime = Field(
        ..., description="Date of birth of the patient (YYYY-MM-DD)"
    )
    patient_zip_code: str = Field(..., description="ZIP code of the patient's address")
    patient_street1: str = Field(..., description="Street address of the patient")
    patient_city: str = Field(..., description="City of the patient's residence")
    patient_state: str = Field(..., description="State of the patient's residence")
    classified_document_type: ClassifierEnum = Field(..., description="Document type")


async def demo_generation_pipeline():
    stages = [Stage.OCR, Stage.PARSER, Stage.LLM_GENERATION]
    additional_instructions = "Provide a summary of history of substance use"
    # Create linear pipeline - dependencies are automatic: ocr -> parser -> llm
    extraction_pipeline = linear_pipeline(
        json_schema=ReferralPatient.model_json_schema(),
        enable_context=True,
        additional_instructions=additional_instructions,
        stages=stages,
        llm_provider="bedrock",
        llm_model="bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        max_tokens="30000",
    )

    result = await extraction_pipeline.async_run("/samples/Ashley_Brenderson.pdf")

    serialized_result = result.model_dump() if hasattr(result, "model_dump") else result

    Path("generation_result.json").write_text(
        json.dumps(serialized_result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    return result


async def demo_generation_pipeline_vlm():
    stages = [Stage.VLM_PARSER, Stage.LLM_GENERATION]
    additional_instructions = "Provide a summary of document"
    # Create linear pipeline - dependencies are automatic: ocr -> parser -> llm
    extraction_pipeline = linear_pipeline(
        json_schema=ReferralPatient.model_json_schema(),
        enable_context=True,
        additional_instructions=additional_instructions,
        stages=stages,
        llm_provider="bedrock",
        llm_model="bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        max_tokens="30000",
    )

    result = await extraction_pipeline.async_run("samples/document.png")

    serialized_result = result.model_dump() if hasattr(result, "model_dump") else result

    Path("generation_result.json").write_text(
        json.dumps(serialized_result, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    return result


async def main():
    try:
        # Run with file input (default)
        await demo_generation_pipeline_vlm()

        # Run with text input (extraction only)
    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
