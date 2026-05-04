"""Stage-specific chunking configuration."""

from pydantic import BaseModel, Field


class StageChunkingConfig(BaseModel):
    """Configuration for stage-specific chunking behavior.

    Different stages can process different chunk sizes:
    - OCR: Static batch size (e.g., 10 pages)
    - Parser: Same as OCR
    - LLM: User-defined chunk size with context from previous chunks

    Attributes:
        ocr_batch_size: Number of pages to process at once for OCR (static).
        parser_batch_size: Number of pages to process at once for parser.
                          If None, uses same as OCR.
        llm_chunk_size: Number of pages to process at once for LLM extraction.
        enable_context: Whether to enable context passing between chunks.
        context_window_size: Number of previous chunks to include in context.
    """

    ocr_batch_size: int = Field(
        default=10, ge=1, description="Static batch size for OCR processing"
    )
    parser_batch_size: int | None = Field(
        default=None,
        ge=1,
        description="Batch size for parser. If None, uses ocr_batch_size",
    )
    llm_chunk_size: int = Field(
        default=5, ge=1, description="Chunk size for LLM processing"
    )
    enable_context: bool = Field(
        default=True, description="Enable context passing between chunks"
    )
    context_window_size: int = Field(
        default=1, ge=0, description="Number of previous chunks to include in context"
    )

    @property
    def effective_parser_batch_size(self) -> int:
        """Get the effective parser batch size."""
        return self.parser_batch_size or self.ocr_batch_size
