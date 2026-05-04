"""PDF validation module."""

from io import BytesIO
from typing import Any

from pypdf import PdfReader

from app.shared.constants.app_constants import FileConstants
from app.shared.exceptions.validation_exceptions import (
    EmptyFileError,
    FileReadError,
    FileSizeExceededError,
    InvalidFileTypeError,
    PageLimitExceededError,
)


class PDFValidator:
    """Validates PDF files against application constraints."""

    @classmethod
    def validate(cls, filename: str, content: bytes) -> None:
        """
        Validate PDF file without checking page count.

        Args:
            filename: Name of the file
            content: File content as bytes

        Raises:
            InvalidFileTypeError: If file extension is not PDF
            EmptyFileError: If file content is empty
            FileSizeExceededError: If file exceeds size limit
        """
        cls._validate_extension(filename)
        cls._validate_not_empty(content)
        cls._validate_size(content)

    @classmethod
    def validate_with_pages(cls, filename: str, content: bytes) -> int:
        """
        Validate PDF and return page count.

        Args:
            filename: Name of the file
            content: File content as bytes

        Returns:
            Number of pages in the PDF

        Raises:
            InvalidFileTypeError: If file extension is not PDF
            EmptyFileError: If file content is empty
            FileSizeExceededError: If file exceeds size limit
            PageLimitExceededError: If PDF has too many pages
            FileReadError: If PDF cannot be read
        """
        cls.validate(filename, content)
        page_count = cls._get_page_count(content)
        cls._validate_page_count(page_count)
        return page_count

    @classmethod
    def _validate_extension(cls, filename: str) -> None:
        """Validate file has PDF extension."""
        if not filename:
            raise InvalidFileTypeError()

        has_valid_extension = Any(
            filename.lower().endswith(ext) for ext in FileConstants.ALLOWED_EXTENSIONS
        )
        if not has_valid_extension:
            raise InvalidFileTypeError()

    @classmethod
    def _validate_not_empty(cls, content: bytes) -> None:
        """Validate file is not empty."""
        if len(content) == 0:
            raise EmptyFileError()

    @classmethod
    def _validate_size(cls, content: bytes) -> None:
        """Validate file size is within limits."""
        if len(content) > FileConstants.MAX_FILE_SIZE_BYTES:
            raise FileSizeExceededError()

    @classmethod
    def _get_page_count(cls, content: bytes) -> int:
        """Get number of pages in PDF."""
        try:
            pdf_reader = PdfReader(BytesIO(content))
            return len(pdf_reader.pages)
        except Exception as e:
            raise FileReadError(detail=str(e)) from e

    @classmethod
    def _validate_page_count(cls, page_count: int) -> None:
        """Validate page count is within limits."""
        if page_count > FileConstants.MAX_PAGES:
            raise PageLimitExceededError()
