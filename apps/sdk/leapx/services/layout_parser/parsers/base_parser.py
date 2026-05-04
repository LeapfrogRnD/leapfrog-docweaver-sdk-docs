"""Base parser abstract class for all layout parsers."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from leapx.common.observability.logger import logger

if TYPE_CHECKING:
    from leapx.services.layout_parser.config import (
        LayoutConservedAdvanceConfig,
        LayoutConservedConfig,
    )
    from leapx.services.layout_parser.structures.ocr_data import OCRData


class BaseLayoutParser(ABC):
    """
    Abstract base class for all layout parsers.

    Defines the common interface for parsers that convert OCRData
    to formatted text while preserving layout.

    Subclasses must implement the `parse()` method with their specific
    parsing algorithm (rule-based, LLM-based, etc.).

    Attributes:
        config: Configuration object for the parser

    Example:
        >>> class MyParser(BaseLayoutParser):
        ...     def parse(self, ocr_data: OCRData, **kwargs) -> str:
        ...         # Implementation here
        ...         return ocr_data.get_text()
        >>> parser = MyParser(config=some_config)
        >>> ocr_data = OCRData(df=ocr_dataframe)
        >>> text = parser.parse(ocr_data)
    """

    def __init__(
        self,
        config: LayoutConservedConfig | LayoutConservedAdvanceConfig | None = None,
    ):
        """
        Initialize base parser.

        Args:
            config: Optional configuration object
        """
        self.config = config
        logger.debug(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def parse(self, ocr_data: OCRData, **kwargs) -> str:
        """
        Parse OCRData to formatted text.

        This is the main entry point for parsing. Subclasses must implement
        their specific parsing logic here.

        Args:
            ocr_data: OCRData object containing word-level data
                     OCRData validates required columns: x0, y0, x2, y2, value
                     Optional columns: page, block, line, space_type, confidence
            **kwargs: Additional parser-specific parameters

        Returns:
            Formatted text string with layout preserved

        Raises:
            DataFrameEmptyError: If OCRData is empty
                (raised by OCRData validation)
            DataFrameColumnMissingError: If required columns missing
                (raised by OCRData validation)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement parse()")

    async def parse_async(self, ocr_data: OCRData, **kwargs) -> str:
        """
        Async parse OCRData to formatted text.

         NOTE: This is NOT truly async I/O. The sync parse() method is
        executed in a thread pool to avoid blocking the event loop.
        This is appropriate for CPU-bound parsing operations.

        For I/O-bound operations, consider implementing native async I/O.

        Args:
            ocr_data: OCRData object containing word-level data
            **kwargs: Additional parser-specific parameters

        Returns:
            Formatted text string with layout preserved
        """
        return await asyncio.to_thread(self.parse, ocr_data, **kwargs)

    def __repr__(self) -> str:
        """Return string representation."""
        config_str = f", config={self.config}" if self.config else ""
        return f"{self.__class__.__name__}({config_str})"
