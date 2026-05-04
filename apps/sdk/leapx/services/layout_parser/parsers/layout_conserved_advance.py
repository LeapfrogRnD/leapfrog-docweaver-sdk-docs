"""Layout-conserved advance parser - Advanced layout preservation with dynamic ratio.

This parser improves upon the basic parser by calculating pixel-to-char conversion
ratios dynamically based on word occupation, resulting in more accurate spacing.

Known Limitations:
    - When two words have very close x0 coordinates (within 1-2 pixels), the overlap
      detection algorithm may shift the earlier word to overwrite the first character
      of the later word. This is an inherent limitation of the spatial positioning
      algorithm inherited from the ground truth implementation.

      Example: "1" at x0=259.60 and "contents" at x0=265.00 may result in "1ontents"

      This occurs because:
      1. "1" calculates to position 26, "contents" already at position 28
      2. Overlap detection shifts "1" right to position 27 (space character)
      3. needs_space=True because position 26 has 's' from "contents"
      4. Slicing logic places "1 " starting at 27, overwriting 'c' at position 28

      The basic parser with dynamic sizing often avoids this due to different
      pixel-to-char ratios, but the issue can still occur with certain documents.
"""

from __future__ import annotations

import pandas as pd

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.config import LayoutConservedAdvanceConfig
from leapx.services.layout_parser.parsers.base_parser import BaseLayoutParser
from leapx.services.layout_parser.parsers.constants import constants
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.layout_parser.utils.text_processing import reset_lines


class LayoutConservedAdvanceParser(BaseLayoutParser):
    """
    Advanced layout-conserved parser with dynamic line width calculation.

    Improves upon basic LayoutConservedParser by:
    - Calculating optimal pixel-to-char ratio per document
    - Dynamic line width based on content
    - Better handling of multi-column layouts
    - More accurate spacing preservation

    Algorithm:
        1. Optionally reset line numbers based on y-coordinate proximity
        2. Group words into TextLines
        3. Calculate max pixel length and word length across all lines
        4. Compute optimal pixel_to_char ratio dynamically
        5. For each line, create character array with calculated width
        6. Place words using optimized positioning

    Configuration:
        - reset_lines: Whether to recalculate line numbers (default: True)
        - pixel_to_char: Base conversion ratio (default: 0.2)
        - merge_threshold: Threshold for merging adjacent lines (default: 0.53)
        - max_line_width: Maximum line width in characters (default: 1000)
        - auto_adjust_ratio: Auto-calculate pixel_to_char (default: True)

    Example:
        >>> config = LayoutConservedAdvanceConfig(
        ...     reset_lines=True,
        ...     pixel_to_char=0.2,
        ...     auto_adjust_ratio=True
        ... )
        >>> parser = LayoutConservedAdvanceParser(config)
        >>> ocr_data = OCRData(df=ocr_dataframe)
        >>> text = parser.parse(ocr_data)
    """

    def __init__(self, config: LayoutConservedAdvanceConfig | None = None):
        """
        Initialize parser with configuration.

        Args:
            config: Configuration object (uses defaults if None)
        """
        super().__init__(config)
        self.config = config or LayoutConservedAdvanceConfig()

    @observe(
        name="layout_conserved_advance.parse", capture_input=False, capture_output=True
    )
    def parse(self, ocr_data: OCRData, **kwargs) -> str:  # noqa: PLR0912, PLR0915
        """
        Parse OCRData to layout-conserved text with advanced features.

        Args:
            ocr_data: OCRData object containing word-level data
                     Required columns: x0, y0, x2, y2, value
                     Optional: page, block, line, space_type, confidence
            **kwargs: Override config parameters:
                - reset_lines: bool
                - pixel_to_char: float
                - merge_threshold: float
                - max_spaces: int (default: 1000)
                - auto_adjust_ratio: bool (default: True)

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
        max_spaces = kwargs.get("max_spaces", 1000)  # Default max line width
        auto_adjust = kwargs.get("auto_adjust_ratio", True)  # Enable by default

        if ocr_data.is_empty:
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
            return self._fallback_parse(ocr_data_reset)

        # Merge adjacent lines if threshold set
        # Note: Very small threshold (< 0.1) effectively disables merging
        if merge_threshold >= constants.MERGE_THRESHOLD:
            text_lines = text_lines.merge_adjacent_lines(
                max_gap=5.0, max_height_diff=merge_threshold
            )
            logger.debug(f"Merged lines: {text_lines.line_count} lines")

        # Calculate optimal pixel_to_char ratio if auto_adjust enabled
        if auto_adjust:
            calculated_ratio = self._calculate_optimal_ratio(text_lines, max_spaces)
            # Only use calculated ratio if it seems reasonable
            if (
                constants.CALCULATED_RATIO_MINIMUM
                <= calculated_ratio
                <= constants.CALCULATED_RATIO_MAXIMUM
            ):
                pixel_to_char = calculated_ratio
                logger.debug(f"Auto-adjusted pixel_to_char ratio: {pixel_to_char:.4f}")
            else:
                logger.warning(
                    f"Calculated ratio {calculated_ratio:.4f} out of bounds, "
                    f"using config value: {pixel_to_char:.4f}"
                )

        # Convert lines to text with advanced layout preservation
        texts = []

        # Calculate max line width across all lines for consistent formatting
        max_char_length = max_spaces
        for line in text_lines:
            line_pixel_length = 0
            previous_word_end = None

            for word in line._words:
                if previous_word_end is not None:
                    space_length = word.x0 - previous_word_end
                    line_pixel_length += space_length

                line_pixel_length += word.x2 - word.x0
                previous_word_end = word.x2

            # Update max if this line is wider
            line_char_length = round(line_pixel_length * pixel_to_char)
            max_char_length = max(max_char_length, line_char_length)

        logger.debug(f"Calculated max_char_length: {max_char_length}")

        for line in text_lines:
            # Start with calculated max width
            final_string = [" "] * max_char_length

            # Place each word at its horizontal position
            for word in line._words:
                start_index = round(word.x0 * pixel_to_char)

                # Ensure index is within bounds
                start_index = max(start_index, 0)

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
        logger.info(
            f"Parsed {ocr_data.word_count} words into {len(texts)} lines "
            f"(pixel_to_char={pixel_to_char:.4f})"
        )

        return result

    def _calculate_optimal_ratio(self, text_lines, max_spaces: int) -> float:
        """
        Calculate optimal pixel-to-character ratio based on content.

        Analyzes all lines to find a ratio that best fits the content
        within the maximum line width constraint.

        The ratio should be such that:
        - Text occupies a reasonable portion of the line width
        - Multi-column layouts are preserved
        - Spacing looks natural

        Args:
            text_lines: TextLines object
            max_spaces: Maximum allowed line width

        Returns:
            Optimal pixel_to_char ratio
        """
        max_pixel_length = 0
        total_word_length = 0
        total_pixel_length = 0
        line_count = 0

        for line in text_lines:
            # Calculate pixel length of line
            line_pixel_length = 0
            previous_word_end = None
            word_occupied_length = 0

            for word in line._words:
                if previous_word_end is not None:
                    space_length = word.x0 - previous_word_end
                    line_pixel_length += space_length

                word_width = word.x2 - word.x0
                line_pixel_length += word_width
                word_occupied_length += len(word.text)
                previous_word_end = word.x2

            # Track maximum and averages
            if line_pixel_length > 0:
                max_pixel_length = max(max_pixel_length, line_pixel_length)
                total_pixel_length += line_pixel_length
                total_word_length += word_occupied_length
                line_count += 1

        # Calculate ratio based on actual text density
        if line_count > 0 and total_pixel_length > 0:
            # Average occupation ratio across all lines
            avg_occupation = total_word_length / total_pixel_length

            # Calculate ratio to fit longest line in max_spaces with some margin
            space_based_ratio = (max_spaces * 0.8) / max_pixel_length

            # Use the more conservative of the two approaches
            optimal_ratio = min(avg_occupation, space_based_ratio)

            # Clamp ratio to reasonable bounds
            optimal_ratio = max(0.1, min(0.3, optimal_ratio))

            logger.debug(
                f"Ratio calculation: avg_occupation={avg_occupation:.4f}, "
                f"space_based={space_based_ratio:.4f}, "
                f"selected={optimal_ratio:.4f}"
            )

            return optimal_ratio

        # Fallback to default
        return self.config.pixel_to_char

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
