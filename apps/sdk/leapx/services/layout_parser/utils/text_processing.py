"""Text processing utilities for layout parsing."""

from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any

import numpy as np
import pandas as pd

from leapx.common.observability.logger import logger


def reset_lines(df_word_level: pd.DataFrame, factor: int = 1) -> list[dict[str, Any]]:
    """
    Reassign line numbers based on y-coordinate proximity.

    Groups words with similar y-coordinates (vertical positions) into the same line.
    This is useful when OCR line detection is inaccurate or when you need to
    regroup words based on their actual vertical alignment.

    Algorithm:
        1. Calculate median word height from DataFrame
        2. Use median height * factor as threshold
        3. Group words within threshold into same line
        4. Reset line numbers sequentially

    Args:
        df_word_level: DataFrame with word-level OCR data
                      Required columns: x0, y0, x2, y2
        factor: Multiplier for threshold calculation (default: 1)
               Higher values = more tolerance for vertical variance
               Lower values = stricter line grouping

    Returns:
        List of dictionaries with updated line numbers

    Raises:
        ValueError: If DataFrame is None or empty
        KeyError: If required columns missing

    Example:
        >>> df = pd.DataFrame({
        ...     'x0': [0, 50, 5], 'y0': [10, 12, 50],
        ...     'x2': [40, 90, 45], 'y2': [20, 22, 60],
        ...     'value': ['Hello', 'World', 'Next']
        ... })
        >>> reset_lines(df, factor=1)
        [
            {'line': 0, 'y0': 10, ...}, {'line': 0, 'y0': 10, ...},
            {'line': 1, 'y0': 50, ...},
        ]
    """
    if df_word_level is None or df_word_level.empty:
        logger.warning("reset_lines called with empty DataFrame")
        return []

    # Convert DataFrame to list of tuples for processing
    df_word_level_lst = list(df_word_level.itertuples())

    # Calculate threshold based on median word height
    try:
        heights = [w.y2 - w.y0 for w in df_word_level_lst]
        th = median(heights) * factor
    except (AttributeError, IndexError, ValueError) as e:
        logger.warning(
            f"Could not calculate median height: {e}, using default threshold"
        )
        th = 10.0  # Default threshold

    # Group words by y-coordinate
    rows_dict = defaultdict(list)
    row_key = 0

    for word in sorted(df_word_level_lst, key=lambda w: w.y0):
        # If y0 difference exceeds 30% of threshold, start new line
        if word.y0 - row_key >= 0.3 * th:
            row_key = word.y0
        rows_dict[row_key].append(word)

    # Sort words within each line by x-coordinate (left to right)
    rows_list = [sorted(r, key=lambda x: x.x0) for r in rows_dict.values()]

    # Rebuild list with updated line numbers
    items_list = []
    for line_num, (sublist, row_y) in enumerate(
        zip(rows_list, rows_dict, strict=False)
    ):
        for item in sublist:
            # Convert namedtuple to dict for modification
            item_dict = item._asdict()
            item_dict["line"] = line_num
            item_dict["y0"] = row_y  # Normalize y0 to row key
            items_list.append(item_dict)

    logger.debug(
        f"reset_lines: Processed {len(items_list)} words into {len(rows_list)} lines"
    )
    return items_list


def combine(df: pd.DataFrame, gap_factor: float = 0.75) -> pd.DataFrame:
    """
    Merge adjacent words into phrases based on spacing.

    Combines words that are close together (same line, small gap) into single
    text units. This is useful for grouping words into phrases or sentences
    while preserving document structure.

    Merging rules:
        1. Always break on space_type > 1 (explicit line breaks)
        2. Always break on text ending with ':' (labels/keys)
        3. Break when page/block/line changes
        4. Break when horizontal gap > gap_factor * max(word_height, next_word_height)

    Args:
        df: DataFrame with word-level OCR data
           Required columns: x0, y0, x2, y2, value
           Optional columns: page, block, line, space_type, confidence
        gap_factor: Threshold for gap detection (default: 0.75)
                   Lower = more aggressive merging
                   Higher = more conservative merging

    Returns:
        DataFrame with merged words/phrases

    Raises:
        ValueError: If DataFrame is None

    Example:
        >>> df = pd.DataFrame({
        ...     'x0': [0, 50], 'y0': [10, 10],
        ...     'x2': [40, 90], 'y2': [20, 20],
        ...     'value': ['Hello', 'World'],
        ...     'space_type': [1, 2]
        ... })
        >>> combine(df, gap_factor=0.75)
        # Returns DataFrame with 'Hello World' merged if gap is small
    """
    if df is None:
        logger.warning("combine called with None DataFrame")
        return pd.DataFrame()

    if df.empty:
        logger.warning("combine called with empty DataFrame")
        return df

    # Sort by index to maintain word order
    dflist = list(df.sort_index().itertuples())

    # Process words and merge
    merged_words = _combine_list(dflist, gap_factor)

    # Convert back to DataFrame
    result_df = pd.DataFrame(merged_words)
    logger.debug(f"combine: Merged {len(dflist)} words into {len(result_df)} phrases")

    return result_df


def _combine_list(dflist: list, gap_factor: float = 0.75) -> list[dict[str, Any]]:
    """
    Internal function to combine words from list of tuples.

    Args:
        dflist: List of namedtuples from DataFrame.itertuples()
        gap_factor: Threshold for gap detection

    Returns:
        List of dictionaries representing merged words
    """
    merged_data = []
    current_word = defaultdict(list)
    confidence_weights = []

    for i, word in enumerate(dflist):
        # Accumulate word properties
        current_word["index_sort"] = word.Index
        current_word["page"] = getattr(word, "page", 0)
        current_word["block"] = getattr(word, "block", None)
        current_word["line"] = getattr(word, "line", None)
        current_word["value"].append(
            word.value if hasattr(word, "value") else word.Text
        )
        current_word["x0"].append(word.x0)
        current_word["y0"].append(word.y0)
        current_word["x2"].append(word.x2)
        current_word["y2"].append(word.y2)
        current_word["space_type"] = getattr(word, "space_type", 1)

        # Handle confidence
        confidence = getattr(word, "confidence", 1.0)
        current_word["confidence"].append(confidence if confidence != -1 else 1.0)
        confidence_weights.append(
            len(word.value if hasattr(word, "value") else word.Text)
        )

        # Check if we should break here
        should_break = False

        # Rule 1: Break on explicit line breaks (space_type > 1)
        if getattr(word, "space_type", 0) > 1:
            should_break = True

        # Rule 2: Break if text ends with ':' (labels/keys)
        text_value = word.value if hasattr(word, "value") else word.Text
        if not should_break and text_value.strip().endswith(":"):
            should_break = True

        # Rule 3 & 4: Check next word for gap or property changes
        if not should_break and i < len(dflist) - 1:
            next_word = dflist[i + 1]

            # Check if page, block, or line changes
            if (
                getattr(next_word, "page", 0) != getattr(word, "page", 0)
                or getattr(next_word, "block", None) != getattr(word, "block", None)
                or getattr(next_word, "line", None) != getattr(word, "line", None)
            ):
                should_break = True
            else:
                # Check horizontal gap
                word_height = word.y2 - word.y0
                next_height = next_word.y2 - next_word.y0
                gap = next_word.x0 - word.x2

                if gap > gap_factor * max(word_height, next_height):
                    should_break = True

        # If last word, always break
        if i == len(dflist) - 1:
            should_break = True

        # Finalize current word if breaking
        if should_break:
            finalized_word = _finalize_word(current_word, confidence_weights)
            merged_data.append(finalized_word)

            # Reset for next word
            current_word = defaultdict(list)
            confidence_weights = []

    return merged_data


def _finalize_word(
    word_dict: dict[str, list],
    confidence_weights: list[int],
) -> dict[str, Any]:
    """
    Finalize a merged word by computing aggregated properties.

    Args:
        word_dict: Dictionary with accumulated word properties
        confidence_weights: List of text lengths for weighted average

    Returns:
        Dictionary with finalized word properties
    """
    finalized = {}

    # Merge text
    finalized["value"] = " ".join(word_dict["value"])

    # Take min/max for bbox
    finalized["x0"] = min(word_dict["x0"])
    finalized["y0"] = min(word_dict["y0"])
    finalized["x2"] = max(word_dict["x2"])
    finalized["y2"] = max(word_dict["y2"])

    # Copy scalar properties
    finalized["index_sort"] = word_dict["index_sort"]
    finalized["page"] = word_dict["page"]
    finalized["block"] = word_dict["block"]
    finalized["line"] = word_dict["line"]
    finalized["space_type"] = word_dict["space_type"]

    # Calculate weighted average confidence
    try:
        finalized["confidence"] = float(
            np.average(word_dict["confidence"], weights=confidence_weights)
        )
    except (ValueError, ZeroDivisionError):
        finalized["confidence"] = 0.99

    return finalized
