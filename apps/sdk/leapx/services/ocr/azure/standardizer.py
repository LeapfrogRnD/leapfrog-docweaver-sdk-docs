import pandas as pd

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.base.standardize import BaseOCRStandardizer


class AzureStandardizer(BaseOCRStandardizer):
    """
    Standardizes OCR output from different providers to OCRData format.

    This class converts raw OCR results (dictionaries) from various providers
    into the standardized OCRData structure used throughout the system.
    """

    @staticmethod
    @observe(
        name="azure_standardizer.standardize_output",
        capture_input=True,
        capture_output=False,
    )
    def standardize_ocr_output(result: dict[str, any]) -> list[OCRData]:
        """
        Convert Azure Document Intelligence output to list of OCRData objects
        (one per page).

        Args:
            result: Raw output from Azure Document Intelligence
                   containing 'pages', 'content', 'tables', 'key_value_pairs'

        Returns:
            List of OCRData objects, one for each page

        Example:
            >>> raw = {"pages": [{"lines": [...]}], "content": "...", ...}
            >>> ocr_data_list = AzureStandardizer.standardize_ocr_output(raw)
            >>> isinstance(ocr_data_list, list)
            True
        """
        logger.debug("Standardizing Azure OCR output")

        raw_output = {
            "content": result.content,
            "pages": [
                {
                    "page_number": page.page_number,
                    "lines": [
                        {"content": line.content, "bounding_box": line.polygon}
                        for line in page.lines
                    ],
                }
                for page in result.pages
            ],
            "tables": (
                [
                    {
                        "rows": [
                            {
                                "cells": [
                                    {
                                        "content": cell.content,
                                        "row_index": cell.row_index,
                                        "column_index": cell.column_index,
                                    }
                                    for cell in table.cells
                                ]
                            }
                            for row in range(table.row_count)
                        ]
                    }
                    for table in result.tables
                ]
                if result.tables
                else []
            ),
            "key_value_pairs": (
                [
                    {
                        "key": kv.key.content if kv.key else "",
                        "value": kv.value.content if kv.value else "",
                        "confidence": kv.confidence,
                    }
                    for kv in getattr(result, "key_value_pairs", []) or []
                ]
            ),
        }

        pages = raw_output.get("pages", [])
        total_pages = len(pages)

        logger.info(f"Processing all {total_pages} pages")

        # Process each page separately and create OCRData for each
        ocr_data_list = []

        for page_idx, page in enumerate(pages):
            words_data = []
            word_index = 0
            lines = page.get("lines", [])
            page_number = page.get("page_number", page_idx + 1)

            for line_idx, line in enumerate(lines):
                line_content = line.get("content", "")
                bounding_box = line.get("bounding_box", [])

                x0, y0, x2, y2 = BaseOCRStandardizer._extract_bbox_from_polygon(
                    bounding_box
                )

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
                        "confidence": None,
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

            metadata = {
                "provider": "azure",
                "page_number": page_number,
                "total_pages": total_pages,
                "content": raw_output.get("content", ""),
                "tables": raw_output.get("tables", []),
                "key_value_pairs": raw_output.get("key_value_pairs", []),
                "extraction_method": "document_intelligence",
            }

            ocr_data_list.append(OCRData(df=df, metadata=metadata))
            logger.debug(f"Processed page {page_number}: {len(words_data)} words")

        logger.info(f"Standardized Azure output: {total_pages} pages")

        return ocr_data_list
