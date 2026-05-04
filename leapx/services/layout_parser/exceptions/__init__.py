"""Layout parser specific exceptions."""

from leapx.services.layout_parser.exceptions.layout_parser_exceptions import (
    CombinedWordError,
    DataFrameColumnMissingError,
    DataFrameEmptyError,
    DataFrameValidationError,
    InvalidBBoxError,
    InvalidDataFrameSchemaError,
    InvalidParserConfigError,
    LayoutParserError,
    LayoutParsingError,
    LayoutPreservationError,
    ParserConfigurationError,
    TextLineParsingError,
    TextLinesMergeError,
    UnsupportedParsingMethodError,
)

__all__ = [
    "CombinedWordError",
    "DataFrameColumnMissingError",
    # Specific validation errors
    "DataFrameEmptyError",
    # Category exceptions
    "DataFrameValidationError",
    "InvalidBBoxError",
    "InvalidDataFrameSchemaError",
    "InvalidParserConfigError",
    # Base exception
    "LayoutParserError",
    "LayoutParsingError",
    "LayoutPreservationError",
    "ParserConfigurationError",
    # Specific parsing errors
    "TextLineParsingError",
    "TextLinesMergeError",
    # Specific configuration errors
    "UnsupportedParsingMethodError",
]
