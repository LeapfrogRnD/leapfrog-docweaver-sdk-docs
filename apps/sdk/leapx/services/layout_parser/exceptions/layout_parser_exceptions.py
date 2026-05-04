"""Layout parser specific exceptions.

All exceptions inherit from LeapXError (defined in leapx.common.exceptions).
Exception names are specific to layout parser domain to avoid conflicts.
"""

from leapx.common.exceptions import LeapXError


# Level 1: Base exception for layout parser
class LayoutParserError(LeapXError):
    """
    Base exception for all layout parser errors.

    All layout parser exceptions inherit from this class.
    This allows catching all layout parser specific errors with a single except clause.
    """

    pass


# Level 2: Category exceptions (domain-specific names)
class DataFrameValidationError(LayoutParserError):
    """
    Raised when input DataFrame validation fails.

    This category includes errors related to DataFrame schema validation,
    missing columns, empty data, and invalid bounding boxes.
    """

    pass


class LayoutParsingError(LayoutParserError):
    """
    Raised when layout parsing process encounters an error.

    This category includes errors during text line parsing, layout preservation,
    and text line merging operations.
    """

    pass


class ParserConfigurationError(LayoutParserError):
    """
    Raised when parser configuration is invalid.

    This category includes errors related to unsupported parsing methods
    and invalid configuration parameters.
    """

    pass


# Level 3: Specific exceptions (descriptive names)


# DataFrame Validation Errors
class DataFrameEmptyError(DataFrameValidationError):
    """
    Raised when input DataFrame is None or empty.

    Example:
        >>> parser.parse(pd.DataFrame())
        DataFrameEmptyError: Input DataFrame is empty
    """

    pass


class DataFrameColumnMissingError(DataFrameValidationError):
    """
    Raised when required columns are missing from DataFrame.

    Required columns: x0, y0, x2, y2, value

    Attributes:
        column_name: Name of the missing column (optional)

    Example:
        >>> df = pd.DataFrame({"x0": [1], "y0": [2]})  # Missing x2, y2, value
        >>> parser.parse(df)
        DataFrameColumnMissingError: Missing required columns: {'x2', 'y2', 'value'}
    """

    def __init__(self, message: str, column_name: str | None = None):
        """
        Initialize exception with optional column name.

        Args:
            message: Error message
            column_name: Name of missing column(s)
        """
        super().__init__(message)
        self.column_name = column_name


class InvalidDataFrameSchemaError(DataFrameValidationError):
    """
    Raised when DataFrame schema doesn't match expected structure.

    This includes wrong data types, invalid value ranges, or malformed data.
    """

    pass


class InvalidBBoxError(DataFrameValidationError):
    """
    Raised when bounding box coordinates are invalid.

    Invalid cases include:
    - x2 <= x0 (invalid width)
    - y2 <= y0 (invalid height)
    - Negative coordinates
    - None values

    Example:
        >>> bbox = BBox(x0=10, y0=20, x2=5, y2=30)  # x2 < x0
        >>> bbox.is_invalid()
        True
    """

    pass


# Layout Parsing Errors
class LineDetectionError(LayoutParsingError):
    """Raised when line detection algorithm fails."""

    pass


class LineMergingError(LayoutParsingError):
    """Raised when merging adjacent lines fails."""

    pass


class TextLineCreationError(LayoutParsingError):
    """Raised when creating TextLine objects fails."""

    pass


class CombiningError(LayoutParsingError):
    """Raised when combining words or text elements fails."""

    pass


class TextLineParsingError(LayoutParsingError):
    """
    Raised when text line parsing fails.

    This can occur during text line extraction, grouping, or conversion.
    """

    pass


class LayoutPreservationError(LayoutParsingError):
    """
    Raised when layout preservation algorithm fails.

    This can occur when spatial relationships cannot be preserved,
    or when character positioning calculations fail.
    """

    pass


class TextLinesMergeError(LineMergingError):
    """Legacy alias for LineMergingError - deprecated."""

    pass


class CombinedWordError(CombiningError):
    """Legacy alias for CombiningError - deprecated."""

    pass


# Parser Configuration Errors
class ParserNotRegisteredError(ParserConfigurationError):
    """Raised when attempting to use an unregistered parser."""

    pass


class ParserRegistrationError(ParserConfigurationError):
    """Raised when parser registration fails."""

    pass


class ParserExecutionError(ParserConfigurationError):
    """Raised when parser execution fails."""

    pass


class UnsupportedParsingMethodError(ParserConfigurationError):
    """
    Raised when an unsupported parsing method is requested.

    Example:
        >>> parse_layout(df, method="invalid_method")
        UnsupportedParsingMethodError: Unsupported parsing method: invalid_method
    """

    pass


class InvalidParserConfigError(ParserConfigurationError):
    """
    Raised when parser configuration is invalid.

    This includes invalid parameter values, incompatible settings,
    or missing required configuration.

    Example:
        >>> parser = LayoutConservedParser(pixel_to_char=-1.0)  # Negative value
        InvalidParserConfigError: pixel_to_char must be positive
    """

    pass
