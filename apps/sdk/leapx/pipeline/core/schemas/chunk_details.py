from typing import Any

from pydantic import BaseModel


class ChunkDetails(BaseModel):
    """Schema for chunk-level pipeline results.

    Attributes:
        page_numbers: Page range string in format "start:end".
        total_pages: Total number of pages in this chunk.
        ocr: Optional OCR stage output (can be list or dict).
        parsed_text: Optional combined parsed text.
        extraction: Optional extraction stage output.
    """

    page_numbers: str
    total_pages: int
    ocr: dict | list | None = None
    parsed_text: str | None = None
    extraction: Any | None = None

    model_config = {"extra": "allow"}  # Allow additional stage outputs
