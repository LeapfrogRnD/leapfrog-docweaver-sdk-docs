"""Layout Parser - OCR text extraction with layout preservation.

This module provides parsers for converting OCR DataFrame output
into formatted text while preserving the original document layout.

Public API:
    - ParserFactory: Factory for creating parser instances
    - ParsingMethod: Enum of available parsing methods
    - LayoutConservedParser: Basic layout-preserving parser
    - LayoutConservedAdvanceParser: Advanced layout-preserving parser
    - LayoutConservedConfig: Configuration for basic parser
    - LayoutConservedAdvanceConfig: Configuration for advanced parser

Example:
    >>> from leapx.services.layout_parser import ParserFactory, ParsingMethod
    >>> from leapx.services.layout_parser.config import LayoutConservedConfig
    >>>
    >>> # Create parser
    >>> config = LayoutConservedConfig(reset_lines=True, pixel_to_char=0.2)
    >>> parser = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED, config)
    >>>
    >>> # Parse OCR data
    >>> text = parser.parse(ocr_dataframe)
"""

from leapx.common.types.providers import ParsingMethod
from leapx.services.layout_parser.config import (
    LayoutConservedAdvanceConfig,
    LayoutConservedConfig,
)
from leapx.services.layout_parser.parser_factory import ParserFactory
from leapx.services.layout_parser.parsers.base_parser import BaseLayoutParser
from leapx.services.layout_parser.parsers.layout_conserved import LayoutConservedParser
from leapx.services.layout_parser.parsers.layout_conserved_advance import (
    LayoutConservedAdvanceParser,
)

# Register parsers with factory
ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED, LayoutConservedParser)
ParserFactory.register(
    ParsingMethod.LAYOUT_CONSERVED_ADVANCE, LayoutConservedAdvanceParser
)

__all__ = [
    # Base class
    "BaseLayoutParser",
    "LayoutConservedAdvanceConfig",
    "LayoutConservedAdvanceParser",
    # Configurations
    "LayoutConservedConfig",
    # Parser implementations
    "LayoutConservedParser",
    # Factory and enums
    "ParserFactory",
    "ParsingMethod",
]

__version__ = "0.1.0"
