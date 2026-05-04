from leapx.common.document.utils import (
    create_chunk_pdf,
    generate_id,
    is_image,
    load_pdf,
)
from leapx.common.observability.logger import logger
from leapx.services.chunking.schemas import ChunkMetaData, ChunkResult, InputType
from leapx.services.chunking.strategy.base import ChunkingStrategy


class BatchWiseChunking(ChunkingStrategy):
    """Fixed batch-size chunking strategy.

    Splits a PDF into sequential chunks of pages based on the configured
    batch_size. Also supports text input for extraction-only pipelines.
    """

    def chunk(
        self, input_data: str | bytes, input_type: InputType = InputType.FILE
    ) -> list[ChunkResult]:
        """Split input into fixed-size batches.

        Args:
            input_data: Path to file, raw bytes (PDF/image), or text string.
            input_type: Type of input (FILE or TEXT).

        Returns:
            List of ChunkResult objects with chunk metadata and content.
        """
        if input_type == InputType.TEXT:
            return self._chunk_text(input_data)

        # Handle images as single chunk
        is_img, file_bytes = is_image(input_data)
        if is_img:
            return self._chunk_image(file_bytes)

        # Handle PDFs with batch processing
        return self._chunk_pdf(input_data)

    def _chunk_text(self, text: str) -> list[ChunkResult]:
        """Create a single chunk from text input.

        Args:
            text: The text content to chunk.

        Returns:
            List containing a single ChunkResult with text content.
        """
        logger.info("Creating text chunk for extraction-only pipeline")

        metadata = ChunkMetaData(
            chunk_id=generate_id(),
            chunk_index=0,
            total_chunks=1,
            start_page=0,
            end_page=1,
            page_count=1,
            core_start_page=0,
            core_end_page=1,
        )

        chunk = ChunkResult(
            text_content=text,
            input_type=InputType.TEXT,
            metadata=metadata,
        )

        logger.info("Text chunk created successfully")
        return [chunk]

    def _chunk_image(self, image_bytes: bytes) -> list[ChunkResult]:
        """Create a single chunk from an image file.

        Args:
            image_bytes: Raw image bytes (PNG or JPG).

        Returns:
            List containing a single ChunkResult with image bytes.
        """
        logger.info("Creating single chunk for image file")

        metadata = ChunkMetaData(
            chunk_id=generate_id(),
            chunk_index=0,
            total_chunks=1,
            start_page=0,
            end_page=1,
            page_count=1,
            core_start_page=0,
            core_end_page=1,
            extra={"is_image": True, "page_number": 1},
        )

        chunk = ChunkResult(
            file_bytes=image_bytes,
            input_type=InputType.FILE,
            metadata=metadata,
        )

        logger.info("Image chunk created successfully")
        return [chunk]

    def _chunk_pdf(self, file_path: str | bytes) -> list[ChunkResult]:
        """Split PDF into fixed-size page batches.

        Args:
            file_path: Path to PDF file or raw PDF bytes.

        Returns:
            List of ChunkResult objects with chunk metadata and bytes.
        """
        reader = load_pdf(file_path)
        total_pages = len(reader.pages)
        batch_size = self.config.batch_size
        chunks: list[ChunkResult] = []

        logger.info(
            "Starting Batch wise chunking",
            total_pages=total_pages,
            batch_size=batch_size,
        )
        total_chunks = (total_pages + batch_size - 1) // batch_size

        for start_idx in range(0, total_pages, batch_size):
            end_idx = min(start_idx + batch_size, total_pages)
            file_bytes = create_chunk_pdf(reader, start_idx, end_idx)

            metadata = ChunkMetaData(
                chunk_id=generate_id(),
                chunk_index=len(chunks),
                total_chunks=total_chunks,
                start_page=start_idx,
                end_page=end_idx,
                page_count=end_idx - start_idx,
                core_start_page=start_idx,
                core_end_page=end_idx,
            )

            chunks.append(
                ChunkResult(
                    file_bytes=file_bytes,
                    input_type=InputType.FILE,
                    metadata=metadata,
                )
            )
            logger.debug(
                "Created batch chunk",
                chunk=len(chunks),
                pages=f"{start_idx + 1}-{end_idx}",
            )

        logger.info("Batch-wise chunking complete", chunks=len(chunks))
        return chunks
