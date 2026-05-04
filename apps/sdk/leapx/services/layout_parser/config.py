# TODO (Amit): Evaluate if we can break this file into smaller files.

"""Configuration and enums for layout parser.

This module defines parsing methods, configuration dataclasses,
and constants used throughout the layout parser.
"""

from dataclasses import dataclass


@dataclass
class LayoutConservedConfig:
    """
    Configuration for basic LayoutConservedParser.

    This parser uses a fixed pixel-to-char conversion ratio to preserve
    layout by positioning characters at calculated horizontal positions.

    Attributes:
        pixel_to_char: Conversion ratio from pixels to characters.
            Higher values = wider spacing. Default: 0.2
        reset_lines: Whether to reassign words to lines based on y-coordinates.
            Helps correct OCR line detection errors. Default: True
        merge_threshold: Threshold for grouping words into same line.
            Multiplied by median text height. Default: 0.53
        max_spaces: Maximum number of spaces in a line.
            Prevents excessive line length. Default: 1000
    """

    pixel_to_char: float = 0.2
    reset_lines: bool = True
    merge_threshold: float = 0.53
    max_spaces: int = 1000

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.pixel_to_char <= 0:
            raise ValueError("pixel_to_char must be positive")
        if self.merge_threshold <= 0:
            raise ValueError("merge_threshold must be positive")
        if self.max_spaces <= 0:
            raise ValueError("max_spaces must be positive")


@dataclass
class LayoutConservedAdvanceConfig:
    """
    Configuration for advanced LayoutConservedAdvanceParser.

    This parser dynamically calculates pixel-to-char ratio based on content,
    detects overlaps, and adjusts spacing adaptively for better layout preservation.

    Attributes:
        pixel_to_char: Initial conversion ratio (may be adjusted dynamically).
            If None, ratio is calculated from content. Default: 0.2
        reset_lines: Whether to reassign words to lines based on y-coordinates.
            Default: True
        merge_threshold: Threshold for grouping words into same line.
            Default: 0.53
    """

    pixel_to_char: float = 0.2
    reset_lines: bool = True
    merge_threshold: float = 0.53

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.pixel_to_char <= 0:
            raise ValueError("pixel_to_char must be positive")
        if self.merge_threshold <= 0:
            raise ValueError("merge_threshold must be positive")


# Common constants
REQUIRED_DATAFRAME_COLUMNS = {"x0", "y0", "x2", "y2", "Text"}
"""Required columns that must be present in input DataFrame."""

OPTIONAL_DATAFRAME_COLUMNS = {
    "page",
    "block",
    "line",
    "confidence",
    "space_type",
    "index_sort",
}
"""Optional columns that may be present in input DataFrame."""
