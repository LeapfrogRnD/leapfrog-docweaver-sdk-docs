"""Layout-conserved parser - Basic rule-based layout preservation.

This parser preserves document layout by converting pixel positions to character
positions with dynamic sizing based on word occupation ratios. The dynamic sizing
helps maintain proper spacing and often avoids overlap issues that can occur with
fixed ratios.

Algorithm:
    1. Calculate pixel-to-char ratio based on word occupation across all lines
    2. Optionally reset line numbers based on y-coordinate proximity
    3. Group words into TextLines
    4. For each line, create character array with dynamic width
    5. Place words at positions calculated from x-coordinates
    6. Handle overlaps by shifting words right
    7. Convert character arrays to strings

Known Limitations:
    - While the dynamic sizing in this parser often avoids spacing issues, overlap
      detection in closely positioned words can still theoretically cause character
      overwrites in edge cases. The advance parser is more susceptible to this.

    - Block-based tracking (from ground truth) is not implemented, which could
      improve line continuation handling for multi-column documents.
"""

from __future__ import annotations

import pandas as pd

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.config import LayoutConservedConfig
from leapx.services.layout_parser.parsers.base_parser import BaseLayoutParser
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.layout_parser.utils.text_processing import reset_lines

THRESHOLD_VALUE = 0.1


class LayoutConservedParser(BaseLayoutParser):
    """
    Basic layout-conserved parser using rule-based spatial positioning.

    Preserves document layout by converting pixel positions to character positions,
    maintaining horizontal spacing between words and vertical spacing between lines.

    Algorithm:
        1. Optionally reset line numbers based on y-coordinate proximity
        2. Group words into TextLines
        3. For each line, create character array of fixed width
        4. Place words at positions calculated from x-coordinates
        5. Convert character arrays to strings

    Configuration:
        - reset_lines: Whether to recalculate line numbers (default: True)
        - pixel_to_char: Conversion ratio from pixels to characters (default: 0.2)
        - merge_threshold: Threshold for merging adjacent lines (default: 0.53)
        - max_line_width: Maximum line width in characters (default: 1000)

    Example:
        >>> config = LayoutConservedConfig(
        ...     reset_lines=True,
        ...     pixel_to_char=0.2,
        ...     merge_threshold=0.53
        ... )
        >>> parser = LayoutConservedParser(config)
        >>> ocr_data = OCRData(df=ocr_dataframe)
        >>> text = parser.parse(ocr_data)
    """

    def __init__(self, config: LayoutConservedConfig | None = None):
        """
        Initialize parser with configuration.

        Args:
            config: Configuration object (uses defaults if None)
        """
        super().__init__(config)
        self.config = config or LayoutConservedConfig()

    @observe(name="layout_conserved.parse", capture_input=False, capture_output=True)
    def parse(self, ocr_data: OCRData, **kwargs) -> str:  # noqa: PLR0915,PLR0912
        """
        Parse OCRData to layout-conserved text.

        Args:
            ocr_data: OCRData object containing word-level data
                     Required columns: x0, y0, x2, y2, value
                     Optional: page, block, line, space_type, confidence
            **kwargs: Override config parameters:
                - reset_lines: bool
                - pixel_to_char: float
                - merge_threshold: float
                - max_spaces: int

        Returns:
            Text string with layout preserved

        Raises:
            DataFrameEmptyError: If OCRData is empty
            DataFrameColumnMissingError: If required columns missing
        """
        # Get config values (kwargs override config)
        reset_lines_flag = kwargs.get("reset_lines", self.config.reset_lines)
        pixel_to_char = kwargs.get("pixel_to_char", self.config.pixel_to_char)
        merge_threshold = kwargs.get("merge_threshold", self.config.merge_threshold)
        max_spaces = kwargs.get("max_spaces", self.config.max_spaces)
        if not ocr_data or ocr_data.is_empty:
            logger.warning("Empty OCRData provided for parsing")
            return ""

        # Reset line numbers if requested
        if reset_lines_flag:
            df_reset_list = reset_lines(ocr_data.df)
            df_reset = pd.DataFrame(df_reset_list)
            ocr_data_reset = OCRData(df=df_reset)
            logger.debug(
                f"Reset lines: {ocr_data.word_count} rows -> "
                f"{ocr_data_reset.word_count} rows"
            )
        else:
            ocr_data_reset = ocr_data

        # Convert to TextLines structure
        try:
            text_lines = ocr_data_reset.to_text_lines()
        except Exception as e:
            logger.error(f"Failed to convert OCRData to TextLines: {e}")
            # Fallback: create simple line-by-line output
            return self._fallback_parse(ocr_data_reset)

        # Merge adjacent lines if threshold set
        # Note: Very small threshold (< 0.1) effectively disables merging
        if merge_threshold >= THRESHOLD_VALUE:
            text_lines = text_lines.merge_adjacent_lines(
                max_gap=5.0, max_height_diff=merge_threshold
            )
            logger.debug(f"Merged lines: {text_lines.line_count} lines")

        # Calculate dynamic max_spaces based on word occupation ratio
        # This matches the ground truth advance parser approach
        max_pixel_length = 0
        max_word_length = 0
        total_text_chars = 0  # Track actual text length needed

        for line in text_lines:
            line_pixel_length = 0
            previous_word_end = None
            word_occupied_length = 0
            line_text_chars = 0

            for word in line._words:
                if previous_word_end is not None:
                    space_length = word.x0 - previous_word_end
                    line_pixel_length += space_length

                line_pixel_length += word.x2 - word.x0
                word_occupied_length += word.x2 - word.x0
                line_text_chars += len(word.text.strip())
                previous_word_end = word.x2

            max_word_length = max(max_word_length, word_occupied_length)
            max_pixel_length = max(max_pixel_length, line_pixel_length)
            total_text_chars = max(total_text_chars, line_text_chars)

        # Calculate occupation ratio for pixel-to-char conversion
        # Adjust to prevent excessive spacing
        if max_pixel_length > 0 and max_word_length > 0:
            occupation_ratio = max_word_length / max_pixel_length
            # Use a more conservative ratio that considers actual text length
            # This prevents creating character arrays that are too large
            if total_text_chars > 0:
                pixel_to_char = total_text_chars / max_pixel_length
            else:
                pixel_to_char = occupation_ratio

            max_spaces = int(max_pixel_length * pixel_to_char) + 100  # Add buffer
            logger.debug(
                f"Dynamic sizing: max_pixel={max_pixel_length:.1f}, "
                f"occupation_ratio={occupation_ratio:.4f}, "
                f"pixel_to_char={pixel_to_char:.6f}, "
                f"max_spaces={max_spaces}, "
                f"total_text_chars={total_text_chars}"
            )
        else:
            # Fallback to config defaults
            logger.debug("Using config defaults for max_spaces")

        # Convert lines to text with layout preservation
        texts = []
        for line in text_lines:
            # Create character array for line
            final_string = [" "] * max_spaces

            # Place each word at its horizontal position
            for word in line._words:
                start_index = round(word.x0 * pixel_to_char)

                # Ensure index is within bounds
                start_index = max(start_index, 0)
                if start_index >= max_spaces:
                    continue

                # Trim whitespace from word text (ground truth does this)
                word_text = word.text.strip()
                len_word = len(word_text)
                word_end_index = start_index + len_word

                # Extend array if word would exceed current length
                if word_end_index > len(final_string):
                    final_string += [" "] * (word_end_index - len(final_string))

                # Detect overlap: shift right until no overlap
                # Ground truth doesn't check bounds, but we should for safety
                while start_index < len(final_string) and any(
                    final_string[start_index + i] != " "
                    for i in range(len_word)
                    if start_index + i < len(final_string)
                ):
                    start_index += 1
                    word_end_index = start_index + len_word
                    # Extend if needed after shift
                    if word_end_index > len(final_string):
                        final_string += [" "] * (word_end_index - len(final_string))

                # Check if we need a space before the word
                needs_space = len(final_string) < start_index + 1 or (
                    start_index >= 1 and final_string[start_index - 1] != " "
                )
                word_space = [" "] if needs_space else []

                # Place word with spacing - use ground truth slicing
                final_string = (
                    final_string[:start_index]
                    + word_space
                    + list(word_text)
                    + final_string[start_index + len_word + len(word_space) :]
                )

            # Convert to string and strip trailing spaces
            text = "".join(final_string).rstrip()
            texts.append(text)

        result = "\n".join(texts)
        logger.info(f"Parsed {ocr_data.word_count} words into {len(texts)} lines")

        return result

    def _fallback_parse(self, ocr_data: OCRData) -> str:
        """
        Fallback parsing when TextLines conversion fails.

        Simple line-by-line concatenation without layout preservation.

        Args:
            ocr_data: OCRData to parse

        Returns:
            Simple text output
        """
        logger.warning("Using fallback parser (no layout preservation)")

        df = ocr_data.df
        if "line" not in df.columns:
            # No line info, just concatenate
            return " ".join(df["value"].astype(str))

        # Group by line and concatenate
        lines = []
        for _, group in df.groupby("line", sort=True):
            line_text = " ".join(group["value"].astype(str))
            lines.append(line_text)

        return "\n".join(lines)
