import pandas as pd

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.base.standardize import BaseOCRStandardizer


class AwsTextractStandardizer(BaseOCRStandardizer):
    """
    Standardizes OCR output from AWS Textract to OCRData format.

    This class converts raw OCR results (dictionaries) from AWS Textract
    into the standardized OCRData structure used throughout the system.
    """

    STANDARD_PAGE_WIDTH_INCHES = 8.5
    STANDARD_PAGE_HEIGHT_INCHES = 11.0
    DPI_FACTOR = 9.0

    @staticmethod
    @observe(
        name="aws_textract_standardizer.standardize_output",
        capture_input=True,
        capture_output=False,
    )
    def standardize_ocr_output(result: dict[str, any]) -> list[OCRData]:
        """
        Convert AWS Textract output to list of OCRData objects (one per page).

        Args:
            result: Raw output from AWS Textract
                   containing 'Blocks' with LINE and WORD types

        Returns:
            List of OCRData objects, one for each page

        Example:
            >>> raw = {"Blocks": [{"BlockType": "LINE", ...}], ...}
            >>> ocr_data_list = AwsTextractStandardizer.standardize_ocr_output(raw)
            >>> isinstance(ocr_data_list, list)
            True
        """
        logger.debug("Standardizing AWS Textract OCR output")

        blocks = result.get("Blocks", [])

        pages_data = {}

        for block in blocks:
            if block.get("BlockType") == "LINE":
                page_num = block.get("Page", 1)
                if page_num not in pages_data:
                    pages_data[page_num] = []
                pages_data[page_num].append(block)

        total_pages = len(pages_data) if pages_data else 1
        logger.info(f"Processing all {total_pages} pages")

        ocr_data_list = []

        # Convert: normalized -> inches -> scaled by DPI factor (matching Azure)
        page_width = (
            AwsTextractStandardizer.STANDARD_PAGE_WIDTH_INCHES
            * AwsTextractStandardizer.DPI_FACTOR
        )
        page_height = (
            AwsTextractStandardizer.STANDARD_PAGE_HEIGHT_INCHES
            * AwsTextractStandardizer.DPI_FACTOR
        )

        logger.debug(
            f"Using coordinate scale: {page_width:.1f}x{page_height:.1f} "
            f"(inches * DPI factor {AwsTextractStandardizer.DPI_FACTOR})"
        )

        for page_number in sorted(pages_data.keys()):
            lines = pages_data[page_number]
            words_data = []
            word_index = 0

            for line_idx, line in enumerate(lines):
                line_content = line.get("Text", "")
                geometry = line.get("Geometry", {})
                bbox = geometry.get("BoundingBox", {})

                # AWS Textract returns normalized coordinates (0-1)
                # Convert to match Azure's coordinate system (inches * DPI factor)
                left = bbox.get("Left", 0) * page_width
                top = bbox.get("Top", 0) * page_height
                width = bbox.get("Width", 0) * page_width
                height = bbox.get("Height", 0) * page_height

                x0 = left
                y0 = top
                x2 = left + width
                y2 = top + height

                if line_content.strip():
                    word_data = {
                        "x0": x0,
                        "y0": y0,
                        "x2": x2,
                        "y2": y2,
                        "value": line_content.strip(),
                        "index": word_index,
                        "page": page_number,
                        "line": line_idx,
                        "confidence": line.get("Confidence"),
                        "block": 0,
                        "space_type": 1 if line_idx < len(lines) - 1 else 2,
                    }
                    words_data.append(word_data)
                    word_index += 1

            if words_data:
                df = pd.DataFrame(words_data)
            else:
                df = pd.DataFrame(
                    columns=[
                        "x0",
                        "y0",
                        "x2",
                        "y2",
                        "value",
                        "index",
                        "page",
                        "line",
                        "confidence",
                        "block",
                        "space_type",
                    ]
                )

            # Extract full text content for this page
            page_content = "\n".join([line.get("Text", "") for line in lines])

            metadata = {
                "provider": "aws_textract",
                "page_number": page_number,
                "total_pages": total_pages,
                "content": page_content,
                "extraction_method": "textract",
                "document_metadata": result.get("DocumentMetadata", {}),
            }

            ocr_data_list.append(OCRData(df=df, metadata=metadata))
            logger.debug(f"Processed page {page_number}: {len(words_data)} words")

        logger.info(f"Standardized AWS Textract output: {total_pages} pages")

        return ocr_data_list
