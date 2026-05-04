"""
Async Demo - LeapX Pipeline with Async Support
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from leapx import InputType, Stage, linear_pipeline


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


async def demo_linear_pipeline():
    additional_instruction = (
        "Please read the text carefully and extract the required fields."
    )
    stages = [Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION]
    # Create linear pipeline - dependencies are automatic: ocr -> parser -> llm
    extraction_pipeline = linear_pipeline(
        json_schema=ReferralPatient.model_json_schema(),
        additional_instructions=additional_instruction,
        stages=stages,
        llm_provider="bedrock",
        llm_model="bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        max_tokens="50000",
    )

    result = await extraction_pipeline.async_run(
        "samples/5032165-BDH-Hearing-Results.pdf"
    )
    Path("extraction_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return result


async def demo_linear_pipeline_vlm():
    additional_instruction = "Please read the ocr_text carefully and help get the answers if available for the required fields."
    stages = [Stage.VLM_PARSER, Stage.LLM_EXTRACTION]

    # Create linear pipeline - dependencies are automatic: ocr -> parser -> llm
    extraction_pipeline = linear_pipeline(
        json_schema=ReferralPatient.model_json_schema(),
        additional_instructions=additional_instruction,
        stages=stages,
        llm_provider="bedrock",
        llm_model="bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        max_tokens=50000,
    )

    result = await extraction_pipeline.async_run("samples/addy_referral.pdf")
    Path("extraction_result_vlm.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return result


async def demo_linear_pipeline_with_text():
    """Demo: Process text directly through Extraction only (skips OCR and Parser)."""
    additional_instruction = (
        "Please read the text carefully and extract the required fields."
    )
    stages = [Stage.LLM_EXTRACTION]
    json_schema = DocumentClassifier.model_json_schema()
    extraction_pipeline = linear_pipeline(
        json_schema=json_schema,
        additional_instructions=additional_instruction,
        stages=stages,
        max_tokens="30000",
    )

    # Example text input - could be from any source
    sample_text = """
    Document Title: Employee Handbook 2024

    This handbook contains policies and procedures for all employees.
    Please review carefully and acknowledge receipt.
    """

    result = await extraction_pipeline.async_run(sample_text, input_type=InputType.TEXT)

    Path("extraction_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return result


async def main():
    try:
        # Run with file input (default)
        await demo_linear_pipeline()

        # Run with text input (extraction only)
    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
