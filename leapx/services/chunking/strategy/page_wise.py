from leapx.common.document.utils import create_chunk_pdf, is_image, load_pdf
from leapx.common.observability.logger import logger
from leapx.services.chunking.schemas import ChunkMetaData, ChunkResult, InputType
from leapx.services.chunking.strategy.base import ChunkingStrategy


class PageWiseChunking(ChunkingStrategy):
    """Page-wise chunking strategy.

    Splits a PDF into individual pages, one chunk per page.
    Uses page_number as the identifier instead of chunk_id.
    """

    def chunk(
        self, input_data: str | bytes, input_type: InputType = InputType.FILE
    ) -> list[ChunkResult]:
        """Split input into individual pages.

        Args:
            input_data: Path to file, raw bytes (PDF/image), or text string.
            input_type: Type of input (FILE or TEXT).

        Returns:
            List of ChunkResult objects with chunk metadata and content.
        """
        if input_type == InputType.TEXT:
            return self._chunk_text(input_data)

        # Handle images as single page
        is_img, file_bytes = is_image(input_data)
        if is_img:
            return self._chunk_image(file_bytes)

        # Handle PDFs with page-wise processing
        return self._chunk_pdf(input_data)

    def _chunk_text(self, text: str) -> list[ChunkResult]:
        """Create a single chunk from text input.

        Args:
            text: The text content to chunk.

        Returns:
            List containing a single ChunkResult with text content.
        """
        logger.info("Creating text chunk for extraction-only pipeline (page-wise)")

        metadata = ChunkMetaData(
            chunk_id="page_1",
            chunk_index=0,
            total_chunks=1,
            start_page=0,
            end_page=1,
            page_count=1,
            core_start_page=0,
            core_end_page=1,
            extra={"page_number": 1},
        )

        chunk = ChunkResult(
            text_content=text,
            input_type=InputType.TEXT,
            metadata=metadata,
        )

        logger.info("Text chunk created successfully (page-wise)")
        return [chunk]

    def _chunk_image(self, image_bytes: bytes) -> list[ChunkResult]:
        """Create a single chunk from an image file.

        Args:
            image_bytes: Raw image bytes (PNG or JPG).

        Returns:
            List containing a single ChunkResult representing the image as one page.
        """
        logger.info("Creating single page chunk for image file")

        metadata = ChunkMetaData(
            chunk_id="page_1",
            chunk_index=0,
            total_chunks=1,
            start_page=0,
            end_page=1,
            page_count=1,
            core_start_page=0,
            core_end_page=1,
            extra={"page_number": 1, "is_image": True},
        )

        chunk = ChunkResult(
            file_bytes=image_bytes,
            input_type=InputType.FILE,
            metadata=metadata,
        )

        logger.info("Image page chunk created successfully")
        return [chunk]

    def _chunk_pdf(self, file_path: str | bytes) -> list[ChunkResult]:
        """Split PDF into individual pages.

        Args:
            file_path: Path to PDF file or raw PDF bytes.

        Returns:
            List of ChunkResult objects, one per page.
        """
        reader = load_pdf(file_path)
        total_pages = len(reader.pages)
        chunks: list[ChunkResult] = []

        logger.info(
            "Starting Page-wise chunking",
            total_pages=total_pages,
        )

        for page_idx in range(total_pages):
            page_number = page_idx + 1  # 1-based page number
            pdf_bytes = create_chunk_pdf(reader, page_idx, page_idx + 1)

            metadata = ChunkMetaData(
                chunk_id=f"page_{page_number}",
                chunk_index=page_idx,
                total_chunks=total_pages,
                start_page=page_idx,
                end_page=page_idx + 1,
                page_count=1,
                core_start_page=page_idx,
                core_end_page=page_idx + 1,
                extra={"page_number": page_number},
            )

            chunks.append(
                ChunkResult(
                    file_bytes=pdf_bytes,
                    input_type=InputType.FILE,
                    metadata=metadata,
                )
            )
            logger.debug(
                "Created page chunk",
                page_number=page_number,
            )

        logger.info("Page-wise chunking complete", total_pages=len(chunks))
        return chunks
