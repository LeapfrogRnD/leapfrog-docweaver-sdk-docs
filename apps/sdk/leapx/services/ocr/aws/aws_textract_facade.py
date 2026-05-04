import asyncio
from io import BytesIO

import boto3
import fitz  # PyMuPDF
from PIL import Image

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.aws.standardizer import (
    AwsTextractStandardizer,
)
from leapx.services.ocr.base.ocr_facade import OCRFacadeInterface


class AwsTextractFacade(OCRFacadeInterface):
    """
    AWS Textract Facade
    Processes PDFs page-by-page using image conversion.
    """

    def __init__(self, client: boto3.client = None):
        self.client = client

    def set_client(self, client: boto3.client):
        self.client = client

    @observe(
        name="aws_textract_facade.process_document",
        capture_input=False,
        capture_output=False,
    )
    async def process_document(self, file_bytes: bytes) -> list[OCRData]:
        """Process document - PDFs are converted to images page-by-page"""

        # Check if it's a PDF
        if file_bytes[:4] == b"%PDF":
            return await self._process_pdf_pages(file_bytes)
        # Single image
        result = await asyncio.to_thread(self._call_textract_api, file_bytes)
        return AwsTextractStandardizer.standardize_ocr_output(result)

    async def _process_pdf_pages(self, pdf_bytes: bytes) -> list[OCRData]:
        """Async convert PDF pages to images and process each page concurrently"""

        ocr_results = []

        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(pdf_document)

        logger.info(f"Processing PDF with {total_pages} pages (async)")

        try:
            # Create tasks for all pages
            tasks = []
            for page_num in range(total_pages):
                page = pdf_document[page_num]

                # Convert page to JPEG at 150 DPI (lower DPI and JPEG compression to stay under 10MB limit)
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                img_bytes = buffer.getvalue()

                # Validate image size (Textract limit is 10MB)
                img_size_mb = len(img_bytes) / (1024 * 1024)
                if img_size_mb > 9.5:  # Leave some margin
                    logger.warning(
                        f"Page {page_num + 1} image size ({img_size_mb:.2f}MB) is close to Textract limit"
                    )

                # Create async task for processing
                task = self._process_page(img_bytes, page_num, total_pages)
                tasks.append(task)

            # Process all pages concurrently
            ocr_results = await asyncio.gather(*tasks)
        finally:
            pdf_document.close()

        logger.info(f"Completed processing {len(ocr_results)} pages (async)")
        return ocr_results

    async def _process_page(
        self, img_bytes: bytes, page_num: int, total_pages: int
    ) -> OCRData:
        """Process a single page asynchronously"""
        logger.debug(f"Processing page {page_num + 1}/{total_pages}")

        # Run Textract API call in executor
        result = await asyncio.to_thread(self._call_textract_api, img_bytes)
        ocr_data_list = AwsTextractStandardizer.standardize_ocr_output(result)

        if ocr_data_list:
            ocr_data = ocr_data_list[0]
            # Update page metadata
            if not hasattr(ocr_data, "metadata") or ocr_data.metadata is None:
                ocr_data.metadata = {}
            ocr_data.metadata["page_number"] = page_num + 1
            ocr_data.metadata["total_pages"] = total_pages
            return ocr_data
        return None

    def _call_textract_api(self, file_bytes: bytes) -> dict:
        """Call Textract detect_document_text for images"""
        return self.client.detect_document_text(Document={"Bytes": file_bytes})


def get_aws_textract_facade() -> AwsTextractFacade:
    return AwsTextractFacade()
