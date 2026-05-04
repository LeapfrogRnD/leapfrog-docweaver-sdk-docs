"""TableData structure - Representation for table extraction (future use)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from leapx.services.layout_parser.structures.bbox import BBox


@dataclass
class TableData:
    """
    Structure for table data representation.

    Placeholder for future table extraction functionality.
    Will store structured table data with cell information,
    row/column headers, and table boundaries.

    Attributes:
        df: DataFrame containing table data
        bbox: Bounding box of table
        page: Page number
        table_id: Unique table identifier
        headers: Column headers
        metadata: Additional metadata

    Note:
        This is a placeholder structure for future implementation.
        Table extraction will be added in later versions.

    Example:
        >>> table = TableData(
        ...     df=pd.DataFrame({'A': [1, 2], 'B': [3, 4]}),
        ...     bbox=BBox(x0=0, y0=0, x2=100, y2=50),
        ...     page=0
        ... )
    """

    df: pd.DataFrame
    bbox: BBox | None = None
    page: int = 0
    table_id: str | None = None
    headers: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def row_count(self) -> int:
        """Number of rows in table."""
        return len(self.df)

    @property
    def column_count(self) -> int:
        """Number of columns in table."""
        return len(self.df.columns)

    @property
    def is_empty(self) -> bool:
        """Check if table is empty."""
        return len(self.df) == 0

    def get_cell(self, row: int, col: int) -> str | None:
        """
        Get cell value at row, column.

        Args:
            row: Row index
            col: Column index

        Returns:
            Cell value as string, or None if out of bounds
        """
        try:
            return str(self.df.iloc[row, col])
        except (IndexError, KeyError):
            return None

    def __repr__(self) -> str:
        """Return string representation."""
        return f"TableData({self.row_count}x{self.column_count}, page={self.page})"
