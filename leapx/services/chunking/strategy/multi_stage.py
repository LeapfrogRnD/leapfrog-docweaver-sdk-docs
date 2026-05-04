"""Multi-stage chunking strategy with different batch sizes per stage."""

from typing import Any

from leapx.common.observability.logger import logger
from leapx.common.utils.file_to_bytes import get_pdf_page_count, split_pdf_by_pages
from leapx.services.chunking.schemas import ChunkMetaData, ChunkResult, InputType
from leapx.services.chunking.strategy.base import ChunkingStrategy


class MultiStageChunkingStrategy(ChunkingStrategy):
    """Chunking strategy that creates different chunk sizes for different stages.

    This strategy creates chunks optimized for each processing stage:
    - OCR chunks: Static batch size (e.g., 10 pages)
    - Parser chunks: Same as OCR chunks
    - LLM chunks: User-defined size with context from previous chunks

    The strategy creates OCR/Parser chunks first, then maps them to LLM chunks.

    Args:
        ocr_batch_size: Number of pages per OCR/Parser chunk.
        llm_chunk_size: Number of pages per LLM chunk.
    """

    def __init__(
        self,
        ocr_batch_size: int = 10,
        llm_chunk_size: int = 5,
    ):
        self.ocr_batch_size = ocr_batch_size
        self.llm_chunk_size = llm_chunk_size

    def chunk(
        self,
        content: bytes | str,
        input_type: InputType = InputType.FILE,
        **kwargs: Any,
    ) -> list[ChunkResult]:
        """Create chunks with OCR batch size.

        For the OCR and Parser stages, we use the OCR batch size.
        The LLM stage will re-chunk these results based on llm_chunk_size.

        Args:
            content: PDF bytes or text content.
            input_type: Type of input (FILE or TEXT).
            **kwargs: Additional arguments.

        Returns:
            List of chunk results for OCR/Parser processing.
        """
        if input_type == InputType.TEXT:
            return self._chunk_text(content, **kwargs)
        return self._chunk_pdf(content, **kwargs)

    def _chunk_pdf(self, pdf_bytes: bytes, **kwargs: Any) -> list[ChunkResult]:  # noqa: ARG002
        """Chunk PDF into OCR-sized batches.

        Args:
            pdf_bytes: PDF content as bytes.
            **kwargs: Additional arguments.

        Returns:
            List of chunk results.
        """
        total_pages = get_pdf_page_count(pdf_bytes)
        chunks = []

        # Create chunks based on OCR batch size
        for chunk_idx, start_page in enumerate(
            range(0, total_pages, self.ocr_batch_size)
        ):
            end_page = min(start_page + self.ocr_batch_size, total_pages)
            chunk_bytes = split_pdf_by_pages(pdf_bytes, start_page, end_page)

            metadata = ChunkMetaData(
                chunk_id=f"ocr_chunk_{chunk_idx}",
                chunk_index=chunk_idx,
                total_chunks=(total_pages + self.ocr_batch_size - 1)
                // self.ocr_batch_size,
                start_page=start_page,
                end_page=end_page,
                page_count=end_page - start_page,
                core_start_page=start_page,
                core_end_page=end_page,
                extra={
                    "ocr_batch_size": self.ocr_batch_size,
                    "llm_chunk_size": self.llm_chunk_size,
                },
            )

            chunks.append(
                ChunkResult(
                    file_bytes=chunk_bytes,
                    input_type=InputType.FILE,
                    metadata=metadata,
                )
            )

        logger.info(
            f"Created {len(chunks)} OCR chunks from {total_pages} pages "
            f"(batch_size={self.ocr_batch_size})"
        )
        return chunks

    def _chunk_text(self, text: str, **kwargs: Any) -> list[ChunkResult]:  # noqa: ARG002
        """Chunk text content.

        For text input, we create a single chunk since there are no pages.

        Args:
            text: Text content.
            **kwargs: Additional arguments.

        Returns:
            List with single chunk result.
        """
        metadata = ChunkMetaData(
            chunk_id="text_chunk_0",
            chunk_index=0,
            total_chunks=1,
            start_page=0,
            end_page=1,
            page_count=1,
            core_start_page=0,
            core_end_page=1,
        )

        return [
            ChunkResult(
                text_content=text,
                input_type=InputType.TEXT,
                metadata=metadata,
            )
        ]

    def get_llm_chunk_mapping(
        self, ocr_chunks: list[ChunkResult]
    ) -> dict[int, list[int]]:
        """Map LLM chunks to their corresponding OCR chunks.

        This creates a mapping showing which OCR chunks should be combined
        for each LLM processing chunk.

        Args:
            ocr_chunks: List of OCR chunk results.

        Returns:
            Dictionary mapping LLM chunk index to list of OCR chunk indices.
            Example: {0: [0, 1], 1: [2, 3]} means LLM chunk 0 uses OCR chunks 0-1.
        """
        if not ocr_chunks:
            return {}

        mapping = {}
        current_page = 0

        for ocr_idx, ocr_chunk in enumerate(ocr_chunks):
            chunk_pages = ocr_chunk.metadata.page_count

            # Determine which LLM chunk this OCR chunk belongs to
            llm_idx = current_page // self.llm_chunk_size

            if llm_idx not in mapping:
                mapping[llm_idx] = []

            mapping[llm_idx].append(ocr_idx)
            current_page += chunk_pages

        logger.info(
            f"Created LLM chunk mapping: {len(mapping)} LLM chunks "
            f"from {len(ocr_chunks)} OCR chunks"
        )
        return mapping
