"""Shared API dependencies."""

from typing import Annotated

from fastapi import Depends, File, UploadFile

from app.shared.exceptions.validation_exceptions import FileReadError
from app.shared.validators.pdf_validator import PDFValidator


class ValidatedPDF:
    """Container for validated PDF file data."""

    def __init__(self, content: bytes, filename: str, page_count: int | None = None):
        self.content = content
        self.filename = filename
        self.page_count = page_count


async def get_validated_pdf(
    file: UploadFile = File(...),
) -> ValidatedPDF:
    """Read and validate PDF file (basic validation without page count)."""
    try:
        content = await file.read()
    except Exception as e:
        raise FileReadError(detail=str(e)) from e

    PDFValidator.validate(file.filename, content)
    return ValidatedPDF(content=content, filename=file.filename)


async def get_validated_pdf_with_pages(
    file: UploadFile = File(...),
) -> ValidatedPDF:
    """Read and validate PDF file with page count validation."""
    try:
        content = await file.read()
    except Exception as e:
        raise FileReadError(detail=str(e)) from e

    page_count = PDFValidator.validate_with_pages(file.filename, content)
    return ValidatedPDF(content=content, filename=file.filename, page_count=page_count)


ValidatedPDFDep = Annotated[ValidatedPDF, Depends(get_validated_pdf)]
ValidatedPDFWithPagesDep = Annotated[ValidatedPDF, Depends(get_validated_pdf_with_pages)]
