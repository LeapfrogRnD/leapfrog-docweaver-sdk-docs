"""
Document Classification Demo - Category-Based Document Classification

This demo shows how to classify a document into predefined categories
using OCR + Parser + LLM extraction pipeline.

Flow:
    PDF -> OCR -> Parser -> Category Classification
"""

import asyncio
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from leapx import InputType, linear_pipeline
from leapx.pipeline.stages.layers import Stage

# =============================================================================
# Category Definitions
# =============================================================================

CATEGORY_DEFINITIONS = {
    "Documents/Orders": """
        Incoming correspondence containing patient care orders, prescriptions,
        requisitions, and administrative requests. Includes medical orders
        (lab, pharmacy, supplies), treatment prescriptions, medication refills,
        patient intake forms, questionnaires, demographic information, facesheets,
        phone notes, and various healthcare service requests or referrals
        requiring action or documentation.
    """,
    "Insurance/Auths": """
        Incoming correspondence from insurance companies, payers, or authorization
        entities regarding coverage decisions, including approvals or denials for
        procedures/surgeries/treatments, eligibility verification, cost estimates,
        prior authorization communications, patient assistance program notifications,
        and confirmation of authorization request submissions.
    """,
    "Legal/Compliance": """
        Documents requiring legal authorization, regulatory compliance, or formal
        consent. Includes procedural/surgical consent forms, patient authorization
        paperwork, disability/FMLA documentation, medical record requests, subpoenas,
        fitness certifications, and compliance-related forms. Characterized by legal
        language, signature requirements, authorization statements, regulatory
        references, or formal request structures that establish legal permissions,
        patient rights, or compliance with healthcare regulations.
    """,
    "Reports": """
        Incoming clinical reports containing structured diagnostic test results,
        patient assessment data, or systematic evaluations. Characterized by
        quantitative measurements, clinical findings, graphical data representations,
        standardized scoring systems, or patient-recorded symptom tracking. Focuses
        on presenting medical data rather than requesting services, authorizing
        treatment, or providing general correspondence.
    """,
    "Speciality-Specific": """
        Clinical documentation received from healthcare providers across medical
        specialties containing patient care information. Characterized by
        provider-generated medical assessments, treatment notes, procedural
        documentation, medical clearances, care summaries, or specialty consultations.
        Includes inbound correspondence detailing clinical evaluations, surgical
        documentation, care transitions, emergency/urgent care records, and
        specialty-specific medical forms requiring clinical expertise.
    """,
}


class CategoryType(str, Enum):
    DOCUMENT_ORDERS = "Documents/Orders"
    INSURANCE_AUTHS = "Insurance/Auths"
    LEGAL_COMPLIANCE = "Legal/Compliance"
    REPORTS = "Reports"
    SPECIALITY_SPECIFIC = "Speciality-Specific"


def build_category_description() -> str:
    """Build the category description string from definitions."""
    lines = []
    for category, definition in CATEGORY_DEFINITIONS.items():
        # Clean up whitespace in definition
        clean_def = " ".join(definition.split())
        lines.append(f"- {category}: {clean_def}")
    return "\n".join(lines)


class CategoryClassification(BaseModel):
    """Document classification schema."""

    category: CategoryType = Field(
        ...,
        description=f"""High-level document category. Choose from:
{build_category_description()}
        """,
    )
    document_date: str | None = Field(
        None, description="The date of the document if available"
    )
    confidence: float = Field(
        ..., description="Confidence score for the classification (0.0 to 1.0)"
    )
    reasoning: str = Field(
        ..., description="Brief explanation of why this category was chosen"
    )


async def classify_document(
    input_path: str,
    input_type: InputType = InputType.FILE,
) -> dict:
    """
    Classify a document into one of the predefined categories.

    Args:
        input_path: Path to PDF file or text content
        input_type: InputType.FILE or InputType.TEXT

    Returns:
        Classification result with category and confidence
    """

    system_prompt = """
    You are a document classification expert for healthcare documents.
    Analyze the document content and classify it into the most appropriate category.
    Provide the document date if visible, your confidence score, and brief reasoning.
    """

    # Determine stages based on input type
    if input_type == InputType.FILE:
        stages = [Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION]
    else:
        stages = [Stage.LLM_EXTRACTION]

    pipeline = linear_pipeline(
        json_schema=CategoryClassification.model_json_schema(),
        additional_instructions=system_prompt,
        stages=stages,
    )

    result = await pipeline.async_run(input_path, input_type=input_type)

    # Extract classification from result

    return {
        "raw_result": result,
    }


async def demo_file_classification():
    """Demo: Classify a PDF file."""

    return await classify_document(
        input_path="test_documents/173323017376.pdf",
        input_type=InputType.FILE,
    )


async def main():
    """Run classification demos."""
    try:
        result = await demo_file_classification()
        import json

        with Path.open("classification_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
