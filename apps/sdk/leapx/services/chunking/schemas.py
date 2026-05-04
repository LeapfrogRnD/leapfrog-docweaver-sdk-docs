from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChunkingMethod(str, Enum):
    """Enumeration of available chunking techniques."""

    BATCH_WISE = "batch_wise"
    PAGE_WISE = "page_wise"


class InputType(str, Enum):
    """Enumeration of supported input types for the pipeline."""

    FILE = "file"  # PDF file path or bytes
    TEXT = "text"  # Raw text input (skips OCR and parser stages)


class ChunkInput(BaseModel):
    """Input payload representing a unit to be chunked."""

    chunk_id: str
    chunk_content: str


class ChunkMetaData(BaseModel):
    """Metadata describing a single chunk of a document.

    Attributes:
        chunk_id: Unique identifier for the chunk.
        chunk_index: Zero-based index of this chunk in the sequence.
        total_chunks: Total number of chunks produced.
        start_page: Start page index (0-based) in the original document.
        end_page: End page index (1-based exclusive) in the original document.
        page_count: Total pages included in this chunk.
        core_start_page: Core start page used for processing.
        core_end_page: Core end page used for processing.
        extra: Extra provider-specific metadata.
    """

    chunk_id: str
    chunk_index: int
    total_chunks: int
    start_page: int
    end_page: int
    page_count: int
    core_start_page: int
    core_end_page: int
    extra: dict[str, Any] = Field(default_factory=dict)


class ChunkResult(BaseModel):
    """Represents a chunk's content and associated metadata.

    Supports both PDF bytes (for file input) and text content (for text input).
    """

    file_bytes: bytes | None = None
    text_content: str | None = None
    input_type: InputType = InputType.FILE
    metadata: ChunkMetaData

    class Config:
        arbitrary_types_allowed = True

    @property
    def has_pdf(self) -> bool:
        """Check if this chunk has PDF bytes."""
        return self.file_bytes is not None

    @property
    def has_text(self) -> bool:
        """Check if this chunk has text content."""
        return self.text_content is not None
