"""BBox (Bounding Box) structure for layout parser.

Represents a 2D rectangle defined by top-left (x0, y0) and
bottom-right (x2, y2) coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class BBox:
    """
    Represents a 2D rectangle (bounding box).

    A bounding box is defined by two points:
    - Top-left corner: (x0, y0)
    - Bottom-right corner: (x2, y2)

    Attributes:
        x0: Left x-coordinate
        y0: Top y-coordinate
        x2: Right x-coordinate
        y2: Bottom y-coordinate

    Properties:
        width: Calculated as x2 - x0
        height: Calculated as y2 - y0

    Example:
        >>> bbox = BBox(x0=10, y0=20, x2=100, y2=80)
        >>> bbox.width
        90
        >>> bbox.height
        60
    """

    x0: int
    y0: int
    x2: int
    y2: int

    def __post_init__(self) -> None:
        """Convert coordinates to integers, handling None values."""
        self.x0 = None if self.x0 is None else int(self.x0)
        self.y0 = None if self.y0 is None else int(self.y0)
        self.x2 = None if self.x2 is None else int(self.x2)
        self.y2 = None if self.y2 is None else int(self.y2)

    @property
    def width(self) -> int:
        """Calculate width of bounding box."""
        return self.x2 - self.x0

    @property
    def height(self) -> int:
        """Calculate height of bounding box."""
        return self.y2 - self.y0

    def to_tuple(self) -> tuple[int, int, int, int]:
        """
        Convert bounding box to tuple.

        Returns:
            Tuple of (x0, y0, x2, y2)
        """
        return self.x0, self.y0, self.x2, self.y2

    def __iter__(self) -> Iterator[int]:
        """
        Make BBox iterable.

        Yields coordinates in order: x0, y0, x2, y2

        Example:
            >>> bbox = BBox(10, 20, 100, 80)
            >>> list(bbox)
            [10, 20, 100, 80]
        """
        yield from [self.x0, self.y0, self.x2, self.y2]

    @classmethod
    def default_empty_bbox(cls) -> BBox:
        """
        Create an empty bounding box with None values.

        Returns:
            BBox with all coordinates set to None

        Example:
            >>> empty = BBox.default_empty_bbox()
            >>> empty.is_empty()
            True
        """
        return cls(x0=None, y0=None, x2=None, y2=None)

    def is_empty(self) -> bool:
        """
        Check if bounding box is empty (all None values).

        Returns:
            True if all coordinates are None, False otherwise

        Example:
            >>> bbox = BBox.default_empty_bbox()
            >>> bbox.is_empty()
            True
        """
        return (
            self.x0 is None and self.y0 is None and self.x2 is None and self.y2 is None
        )

    def is_invalid(self) -> bool:
        """
        Check if bounding box has invalid values.

        Invalid cases:
        - Any coordinate is None
        - x2 <= x0 (invalid width)
        - y2 <= y0 (invalid height)
        - Any coordinate is negative

        Returns:
            True if bounding box is invalid, False otherwise

        Example:
            >>> bbox = BBox(x0=10, y0=20, x2=5, y2=30)  # x2 < x0
            >>> bbox.is_invalid()
            True
        """
        bbox = self.to_tuple()
        x0, y0, x2, y2 = bbox
        return any(x is None for x in bbox) or x2 <= x0 or y2 <= y0 or min(bbox) < 0

    def copy(self) -> BBox:
        """
        Create a copy of the bounding box.

        Returns:
            New BBox instance with same coordinates

        Example:
            >>> original = BBox(10, 20, 100, 80)
            >>> copy = original.copy()
            >>> copy == original
            False  # Different objects
            >>> copy.to_tuple() == original.to_tuple()
            True  # Same values
        """
        return BBox(x0=self.x0, y0=self.y0, x2=self.x2, y2=self.y2)

    @classmethod
    def from_iterator(cls, iterator: Iterator[int] | BBox) -> BBox:
        """
        Create BBox from an iterable or another BBox.

        Args:
            iterator: Either a BBox instance (returns copy) or
                     an iterable of 4 integers [x0, y0, x2, y2]

        Returns:
            New BBox instance

        Raises:
            TypeError: If iterator type is invalid or elements are not numeric
            ValueError: If iterator doesn't contain exactly 4 elements

        Example:
            >>> bbox = BBox.from_iterator([10, 20, 100, 80])
            >>> bbox.to_tuple()
            (10, 20, 100, 80)
        """
        if isinstance(iterator, BBox):
            return iterator.copy()

        if not isinstance(iterator, (list, tuple)):
            raise TypeError(
                f"Invalid type for BBox. Expected [list, tuple]. Got {type(iterator)}"
            )

        if len(iterator) != 4:
            raise ValueError(
                f"Invalid length of iterator for BBox. Expected 4. Got {len(iterator)}"
            )

        for i in range(4):
            if not isinstance(iterator[i], (int, float)):
                raise TypeError(
                    f"Invalid element type in iterator. Expected: [int, float]. Got {type(iterator[i])}"
                )

        return cls(x0=iterator[0], y0=iterator[1], x2=iterator[2], y2=iterator[3])

    def __hash__(self) -> int:
        """Make BBox hashable for use in sets and as dict keys."""
        return hash(tuple(self.__dict__.items()))
