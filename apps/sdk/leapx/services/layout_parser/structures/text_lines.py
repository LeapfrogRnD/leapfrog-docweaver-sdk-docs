"""TextLines structure - Collection of TextLine objects with merge operations."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from leapx.services.layout_parser.structures.bbox import BBox
from leapx.services.layout_parser.structures.text_line import TextLine


@dataclass
class TextLines:
    """
    Collection of TextLine objects with merge and filtering operations.

    Provides methods for working with multiple text lines,
    including merging adjacent lines and filtering by properties.

    Attributes:
        _lines: List of TextLine objects
        page: Page number for all lines
        block: Block number for all lines

    Example:
        >>> line1 = TextLine(words=[word1, word2], line_number=0)
        >>> line2 = TextLine(words=[word3, word4], line_number=1)
        >>> lines = TextLines([line1, line2])
        >>> lines.line_count
        2
        >>> lines.get_text()
        'Hello World\\nFoo Bar'
    """

    _lines: list[TextLine] = field(default_factory=list)
    page: int = 0
    block: int | None = None

    def __init__(
        self,
        lines: list[TextLine] | None = None,
        page: int = 0,
        block: int | None = None,
    ):
        """
        Initialize TextLines.

        Args:
            lines: Initial list of TextLine objects
            page: Page number
            block: Block number
        """
        self._lines = lines if lines is not None else []
        self.page = page
        self.block = block

    def __len__(self) -> int:
        """Return number of lines."""
        return len(self._lines)

    def __iter__(self) -> Iterator[TextLine]:
        """Iterate over lines."""
        return iter(self._lines)

    def __getitem__(self, key: int | slice) -> TextLine | TextLines:
        """
        Get line(s) by index or slice.

        Args:
            key: Integer index or slice

        Returns:
            TextLine if key is int, TextLines if key is slice
        """
        if isinstance(key, slice):
            return TextLines(self._lines[key], self.page, self.block)
        return self._lines[key]

    def __contains__(self, item: TextLine) -> bool:
        """Check if line is in collection."""
        return item in self._lines

    def append(self, line: TextLine) -> None:
        """
        Add a line to the end.

        Args:
            line: TextLine to append
        """
        self._lines.append(line)

    def extend(self, lines: list[TextLine]) -> None:
        """
        Add multiple lines to the end.

        Args:
            lines: List of TextLine objects to append
        """
        self._lines.extend(lines)

    def insert(self, index: int, line: TextLine) -> None:
        """
        Insert line at specified index.

        Args:
            index: Position to insert at
            line: TextLine to insert
        """
        self._lines.insert(index, line)

    def remove(self, line: TextLine) -> None:
        """
        Remove first occurrence of line.

        Args:
            line: TextLine to remove

        Raises:
            ValueError: If line not in collection
        """
        self._lines.remove(line)

    def pop(self, index: int = -1) -> TextLine:
        """
        Remove and return line at index.

        Args:
            index: Position to pop from (default: -1, last item)

        Returns:
            TextLine that was removed

        Raises:
            IndexError: If index out of range
        """
        return self._lines.pop(index)

    def clear(self) -> None:
        """Remove all lines."""
        self._lines.clear()

    @property
    def is_empty(self) -> bool:
        """Check if collection is empty."""
        return len(self._lines) == 0

    @property
    def line_count(self) -> int:
        """Number of lines."""
        return len(self._lines)

    @property
    def word_count(self) -> int:
        """Total number of words across all lines."""
        return sum(line.word_count for line in self._lines)

    def get_text(self, line_separator: str = "\n") -> str:
        """
        Get text of all lines concatenated.

        Args:
            line_separator: String to join lines with (default: newline)

        Returns:
            Concatenated text string
        """
        return line_separator.join(line.text for line in self._lines)

    def get_bounding_box(self) -> BBox | None:
        """
        Get bounding box encompassing all lines.

        Returns:
            BBox covering all lines, or None if empty
        """
        if self.is_empty:
            return None

        bboxes = [line.bbox for line in self._lines if line.bbox is not None]
        if not bboxes:
            return None

        x0 = min(bbox.x0 for bbox in bboxes)
        y0 = min(bbox.y0 for bbox in bboxes)
        x2 = max(bbox.x2 for bbox in bboxes)
        y2 = max(bbox.y2 for bbox in bboxes)

        return BBox(x0=x0, y0=y0, x2=x2, y2=y2)

    def filter_by_bbox(self, bbox: BBox, strict: bool = False) -> TextLines:
        """
        Filter lines that overlap with bbox.

        Args:
            bbox: Bounding box to filter by
            strict: If True, only include lines fully contained in bbox

        Returns:
            New TextLines with lines overlapping bbox
        """
        filtered = []
        for line in self._lines:
            line_bbox = line.bbox
            if line_bbox is None:
                continue

            if strict:
                # Fully contained
                if (
                    line_bbox.x0 >= bbox.x0
                    and line_bbox.y0 >= bbox.y0
                    and line_bbox.x2 <= bbox.x2
                    and line_bbox.y2 <= bbox.y2
                ):
                    filtered.append(line)
            elif not (
                line_bbox.x2 < bbox.x0
                or line_bbox.x0 > bbox.x2
                or line_bbox.y2 < bbox.y0
                or line_bbox.y0 > bbox.y2
            ):
                filtered.append(line)

        return TextLines(filtered, self.page, self.block)

    def sort_by_position(self, vertical: bool = False) -> None:
        """
        Sort lines by position.

        Args:
            vertical: If True, sort by y-coordinate (top to bottom)
                     If False, sort by x-coordinate (left to right)
        """
        if vertical:
            self._lines.sort(key=lambda line: (line.bbox.y0 if line.bbox else 0))
        else:
            self._lines.sort(key=lambda line: (line.bbox.x0 if line.bbox else 0))

    def merge_adjacent_lines(
        self, max_gap: float = 5.0, max_height_diff: float = 2.0
    ) -> TextLines:
        """
        Merge lines that are adjacent and aligned.

        Args:
            max_gap: Maximum vertical gap to consider adjacent (pixels)
            max_height_diff: Maximum height difference ratio (0.0 to 1.0)

        Returns:
            New TextLines with merged lines
        """
        if len(self._lines) < 2:
            return TextLines(self._lines.copy(), self.page, self.block)

        # Sort by position first
        sorted_lines = sorted(
            self._lines, key=lambda line: (line.bbox.y0 if line.bbox else 0)
        )

        merged = []
        current_line = sorted_lines[0]

        for next_line in sorted_lines[1:]:
            current_bbox = current_line.bbox
            next_bbox = next_line.bbox

            if current_bbox is None or next_bbox is None:
                merged.append(current_line)
                current_line = next_line
                continue

            # Check vertical gap
            gap = next_bbox.y0 - current_bbox.y2

            # Check height similarity (handle zero height case)
            max_height = max(current_bbox.height, next_bbox.height)
            if max_height > 0:
                height_ratio = abs(current_bbox.height - next_bbox.height) / max_height
            else:
                # If both heights are zero, consider them similar
                height_ratio = 0.0

            if gap <= max_gap and height_ratio <= max_height_diff:
                # Merge lines
                current_line._words.extend(next_line._words)
            else:
                merged.append(current_line)
                current_line = next_line

        merged.append(current_line)

        return TextLines(merged, self.page, self.block)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"TextLines({self.line_count} lines, {self.word_count} words)"
