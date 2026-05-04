"""Pydantic schemas for processing results."""

from typing import Any

from pydantic import BaseModel


class LeapXResult(BaseModel):
    """LeapX SDK processing result."""

    raw_output: dict[str, Any]
    confidence_scores: dict[str, float] | None = None
    extracted_fields: dict[str, Any] | None = None
    document_type: str | None = None
