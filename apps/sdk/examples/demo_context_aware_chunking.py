"""
Demo: Context-Aware Multi-Stage Chunking

"""

import asyncio
import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from leapx.pipeline.runner import linear_pipeline
from leapx.services.chunking.config import ChunkingConfig
from leapx.services.chunking.schemas import ChunkingMethod


class DocumentClassifier(BaseModel):
    title: str | None = Field(
        None,
        description="Title of the chunk if explicitly present, otherwise null",
    )


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
    """
    Extraction schema.

    IMPORTANT:
    All fields are optional to prevent hallucination.
    If a value is not explicitly present, it MUST be null.
    """

    patient_first_name: str | None = Field(
        None, description="First name of the patient if explicitly stated"
    )
    patient_last_name: str | None = Field(
        None, description="Last name of the patient if explicitly stated"
    )
    patient_dob: str | None = Field(
        None, description="Date of birth (YYYY-MM-DD) if explicitly stated"
    )
    patient_zip_code: str | None = Field(
        None, description="ZIP code if explicitly stated"
    )
    patient_street1: str | None = Field(
        None, description="Street address if explicitly stated"
    )
    patient_city: str | None = Field(None, description="City if explicitly stated")
    patient_state: str | None = Field(None, description="State if explicitly stated")
    classified_document_type: ClassifierEnum | None = Field(
        None, description="Document type if explicitly stated"
    )


additional_instructions = """
You are an information extraction system.

Extract patient information strictly from the provided document text
and any explicitly stated values in prior chunk context.

CRITICAL RULES (DO NOT VIOLATE):
- Do NOT guess, infer, assume, or fabricate values.
- Do NOT use common sense or medical knowledge.
- Do NOT auto-complete missing information.
- If a field is NOT explicitly present, return null (None).
- Never invent names, dates, addresses, or document types.

Context usage:
- You MAY reuse values from previous chunks ONLY if they were explicitly stated.
- If values conflict, use the most recently stated explicit value.
- If a value becomes unclear or absent, return null.

Output rules:
- Return ALL schema fields.
- Fields not found MUST be null.
- Do NOT add extra fields.
- Do NOT add explanations, comments, or confidence scores.

If no patient information is found, return all fields as null.
"""


async def demo_basic_context_aware():
    """Basic example with context-aware processing."""

    pipeline = linear_pipeline(
        json_schema=ReferralPatient,
        additional_instructions=additional_instructions,
        enable_context=True,
        chunking_config=ChunkingConfig(
            method=ChunkingMethod.BATCH_WISE,
            batch_size=1,
        ),
    )

    result = await pipeline.async_run("samples/addy_referral.pdf")

    Path("extraction_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main():
    asyncio.run(demo_basic_context_aware())


if __name__ == "__main__":
    main()
