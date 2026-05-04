"""OCRData structure - Main data structure for OCR output with DataFrame operations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

import pandas as pd

from leapx.common.observability.logger import logger
from leapx.services.layout_parser.exceptions.layout_parser_exceptions import (
    DataFrameColumnMissingError,
    DataFrameEmptyError,
    DataFrameValidationError,
)
from leapx.services.layout_parser.structures.bbox import BBox
from leapx.services.layout_parser.structures.ocr_word import OCRWord
from leapx.services.layout_parser.structures.text_line import TextLine
from leapx.services.layout_parser.structures.text_lines import TextLines


@dataclass
class OCRData:
    """
    Main data structure for OCR output with DataFrame operations.

    Wraps a pandas DataFrame containing OCR word-level data
    and provides methods for validation, filtering, and conversion
    to structured objects (OCRWord, TextLine, TextLines).

    Required DataFrame columns:
        - x0, y0, x2, y2: Bounding box coordinates
        - value: Text content

    Optional DataFrame columns:
        - index: Word index
        - space_type: Space after word (0=none, 1=space, 2+=newline)
        - block: Block number
        - confidence: OCR confidence (0.0 to 1.0, -1 if unknown)
        - page: Page number (default: 0)
        - line: Line number

    Attributes:
        df: Pandas DataFrame with OCR data
        metadata: Additional metadata dictionary

    Example:
        >>> df = pd.DataFrame({
        ...     'x0': [0, 10], 'y0': [0, 0],
        ...     'x2': [8, 18], 'y2': [10, 10],
        ...     'value': ['Hello', 'World']
        ... })
        >>> ocr_data = OCRData(df)
        >>> ocr_data.word_count
        2
        >>> words = ocr_data.to_ocr_words()
    """

    df: pd.DataFrame
    metadata: dict = field(default_factory=dict)

    _REQUIRED_COLUMNS = ["x0", "y0", "x2", "y2", "value"]
    _OPTIONAL_COLUMNS = [
        "index",
        "space_type",
        "block",
        "confidence",
        "page",
        "line",
        "bounding_box",
        "md",
    ]

    def __post_init__(self):
        """Validate DataFrame after initialization."""
        self.validate()

    def validate(self) -> None:
        """
        Validate DataFrame structure and content.

        Raises:
            DataFrameEmptyError: If DataFrame is empty
            DataFrameColumnMissingError: If required columns missing
            DataFrameValidationError: If column types invalid
        """
        # Check if empty
        if self.df is None or len(self.df) == 0:
            raise DataFrameEmptyError("OCR DataFrame is empty")

        # Check required columns
        missing_cols = [
            col for col in self._REQUIRED_COLUMNS if col not in self.df.columns
        ]
        if missing_cols:
            raise DataFrameColumnMissingError(
                f"Required columns missing: {missing_cols}",
                column_name=", ".join(missing_cols),
            )

        # Validate coordinate types
        for col in ["x0", "y0", "x2", "y2"]:
            if not pd.api.types.is_numeric_dtype(self.df[col]):
                raise DataFrameValidationError(f"Column '{col}' must be numeric")

        # Validate value column is string-like
        if not pd.api.types.is_string_dtype(
            self.df["value"]
        ) and not pd.api.types.is_object_dtype(self.df["value"]):
            logger.warning("Column 'value' is not string type, will convert")
            self.df["value"] = self.df["value"].astype(str)

        logger.debug(
            f"OCRData validated: {len(self.df)} rows, {len(self.df.columns)} columns"
        )

    @property
    def word_count(self) -> int:
        """Number of words in DataFrame."""
        return len(self.df)

    @property
    def page_count(self) -> int:
        """Number of unique pages."""
        if "page" not in self.df.columns:
            return 1
        return self.df["page"].nunique()

    @property
    def is_empty(self) -> bool:
        """Check if DataFrame is empty."""
        return len(self.df) == 0

    def copy(self) -> OCRData:
        """
        Create deep copy of OCRData.

        Returns:
            New OCRData instance with copied DataFrame
        """
        return OCRData(df=self.df.copy(), metadata=self.metadata.copy())

    def filter_by_page(self, page: int) -> OCRData:
        """
        Filter words by page number.

        Args:
            page: Page number to filter

        Returns:
            New OCRData with only words from specified page
        """
        if "page" not in self.df.columns:
            if page == 0:
                return self.copy()
            return OCRData(
                df=pd.DataFrame(columns=self.df.columns), metadata=self.metadata.copy()
            )

        filtered_df = self.df[self.df["page"] == page].copy()
        return OCRData(df=filtered_df, metadata=self.metadata.copy())

    def filter_by_bbox(self, bbox: BBox, strict: bool = False) -> OCRData:
        """
        Filter words by bounding box.

        Args:
            bbox: BBox to filter by
            strict: If True, only words fully contained in bbox

        Returns:
            New OCRData with filtered words
        """
        if strict:
            mask = (
                (self.df["x0"] >= bbox.x0)
                & (self.df["y0"] >= bbox.y0)
                & (self.df["x2"] <= bbox.x2)
                & (self.df["y2"] <= bbox.y2)
            )
        else:
            # Any overlap
            mask = ~(
                (self.df["x2"] < bbox.x0)
                | (self.df["x0"] > bbox.x2)
                | (self.df["y2"] < bbox.y0)
                | (self.df["y0"] > bbox.y2)
            )

        filtered_df = self.df[mask].copy()
        return OCRData(df=filtered_df, metadata=self.metadata.copy())

    def filter_by_confidence(self, min_confidence: float = 0.0) -> OCRData:
        """
        Filter words by OCR confidence threshold.

        Args:
            min_confidence: Minimum confidence score (0.0 to 1.0)

        Returns:
            New OCRData with only high-confidence words
        """
        if "confidence" not in self.df.columns:
            logger.warning("Confidence column not found, returning all data")
            return self.copy()

        filtered_df = self.df[self.df["confidence"] >= min_confidence].copy()
        return OCRData(df=filtered_df, metadata=self.metadata.copy())

    def to_ocr_words(self, page: int | None = None) -> list[OCRWord]:
        """
        Convert DataFrame rows to OCRWord objects.

        Args:
            page: Optional page number to filter

        Returns:
            List of OCRWord objects
        """
        df_to_use = self.df if page is None else self.filter_by_page(page).df

        words = []
        for _, row in df_to_use.iterrows():
            word = OCRWord(
                x0=float(row["x0"]),
                y0=float(row["y0"]),
                x2=float(row["x2"]),
                y2=float(row["y2"]),
                value=str(row["value"]),
                index=int(row["index"])
                if "index" in row and pd.notna(row["index"])
                else None,
                space_type=(
                    int(row["space_type"])
                    if "space_type" in row and pd.notna(row["space_type"])
                    else None
                ),
                block=int(row["block"])
                if "block" in row and pd.notna(row["block"])
                else None,
                confidence=(
                    float(row["confidence"])
                    if "confidence" in row and pd.notna(row["confidence"])
                    else -1
                ),
                page=int(row["page"]) if "page" in row and pd.notna(row["page"]) else 0,
                line=int(row["line"])
                if "line" in row and pd.notna(row["line"])
                else None,
            )
            words.append(word)

        return words

    def to_text_lines(self, page: int | None = None) -> TextLines:
        """
        Convert DataFrame to TextLines grouped by line number.

        Args:
            page: Optional page number to filter

        Returns:
            TextLines object with words grouped by line

        Raises:
            DataFrameColumnMissingError: If 'line' column not present
        """
        if "line" not in self.df.columns:
            raise DataFrameColumnMissingError(
                "Cannot create TextLines: 'line' column missing", column_name="line"
            )

        df_to_use = self.df if page is None else self.filter_by_page(page).df

        # Group by line number
        lines = []
        for line_num, group in df_to_use.groupby("line", sort=True):
            words = []
            for _, row in group.iterrows():
                word = OCRWord(
                    x0=float(row["x0"]),
                    y0=float(row["y0"]),
                    x2=float(row["x2"]),
                    y2=float(row["y2"]),
                    value=str(row["value"]),
                    index=(
                        int(row["index"])
                        if "index" in row and pd.notna(row["index"])
                        else None
                    ),
                    space_type=(
                        int(row["space_type"])
                        if "space_type" in row and pd.notna(row["space_type"])
                        else None
                    ),
                    block=(
                        int(row["block"])
                        if "block" in row and pd.notna(row["block"])
                        else None
                    ),
                    confidence=(
                        float(row["confidence"])
                        if "confidence" in row and pd.notna(row["confidence"])
                        else -1
                    ),
                    page=int(row["page"])
                    if "page" in row and pd.notna(row["page"])
                    else 0,
                    line=int(line_num),
                )
                words.append(word)

            text_line = TextLine(
                _words=words,
                line_number=int(line_num),
                page=words[0].page if words else 0,
                block=words[0].block if words else None,
            )
            lines.append(text_line)

        return TextLines(
            lines=lines,
            page=page if page is not None else (lines[0].page if lines else 0),
            block=lines[0].block if lines else None,
        )

    def get_text(self, separator: str = " ", page: int | None = None) -> str:
        """
        Get concatenated text from all words.

        Args:
            separator: String to join words with (default: space)
            page: Optional page number to filter

        Returns:
            Concatenated text string
        """
        df_to_use = self.df if page is None else self.filter_by_page(page).df
        return separator.join(df_to_use["value"].astype(str))

    def get_bounding_box(self, page: int | None = None) -> BBox | None:
        """
        Get bounding box encompassing all words.

        Args:
            page: Optional page number to filter

        Returns:
            BBox covering all words, or None if empty
        """
        df_to_use = self.df if page is None else self.filter_by_page(page).df

        if len(df_to_use) == 0:
            return None

        return BBox(
            x0=float(df_to_use["x0"].min()),
            y0=float(df_to_use["y0"].min()),
            x2=float(df_to_use["x2"].max()),
            y2=float(df_to_use["y2"].max()),
        )

    def sort_by_position(
        self, vertical: bool = False, inplace: bool = False
    ) -> OCRData | None:
        """
        Sort words by position.

        Args:
            vertical: If True, sort by y-coordinate (top to bottom)
                     If False, sort by x-coordinate (left to right)
            inplace: If True, modify this instance; if False, return new instance

        Returns:
            None if inplace=True, new OCRData if inplace=False
        """
        if vertical:
            sorted_df = self.df.sort_values(by=["y0", "x0"]).reset_index(drop=True)
        else:
            sorted_df = self.df.sort_values(by=["x0", "y0"]).reset_index(drop=True)

        if inplace:
            self.df = sorted_df
            return None
        return OCRData(df=sorted_df, metadata=self.metadata.copy())

    def __len__(self) -> int:
        """Return number of words."""
        return len(self.df)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"OCRData({self.word_count} words, {self.page_count} pages)"

    def to_dict(self):
        """Return dict suitable for JSON serialization."""
        data_dict = asdict(self)
        if isinstance(self.df, pd.DataFrame):
            data_dict["df"] = self.df.to_dict(orient="records")
        return data_dict

    def to_json(self):
        return json.dumps(self.to_dict())
