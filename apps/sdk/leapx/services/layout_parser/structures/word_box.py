"""WordBox structure - BBox with text value."""

from __future__ import annotations

import copy
from collections.abc import Iterator
from dataclasses import dataclass

from leapx.services.layout_parser.structures.bbox import BBox


@dataclass
class WordBox(BBox):
    """
    Bounding box with associated text value.

    Extends BBox with text content and index tracking.
    Commonly used to represent OCR words with their spatial location.

    Attributes:
        x0: Left x-coordinate (inherited from BBox)
        y0: Top y-coordinate (inherited from BBox)
        x2: Right x-coordinate (inherited from BBox)
        y2: Bottom y-coordinate (inherited from BBox)
        value: Text content of the word
        index: Optional index for ordering/tracking

    Example:
        >>> word = WordBox(x0=10, y0=20, x2=50, y2=40, value="Hello")
        >>> word.text
        'Hello'
        >>> word.width
        40
    """

    value: str | None = None
    index: int | None = None

    @property
    def text(self) -> str | None:
        """Get text content (alias for value)."""
        return self.value

    @text.setter
    def text(self, val: str) -> None:
        """Set text content."""
        self.value = val

    @property
    def Text(self) -> str | None:
        """Get text content (capitalized alias for pandas compatibility)."""
        return self.value

    @property
    def bbox(self) -> BBox:
        """Get underlying BBox without text."""
        return BBox(x0=self.x0, y0=self.y0, x2=self.x2, y2=self.y2)

    def to_bbox(self) -> BBox:
        """Convert to plain BBox."""
        return self.bbox

    def copy(self) -> WordBox:
        """
        Create a deep copy of the WordBox.

        Returns:
            New WordBox instance with same values
        """
        return copy.deepcopy(self)

    def __iter__(self) -> Iterator:
        """
        Make WordBox iterable.

        Yields: value, x0, y0, x2, y2 (in that order)

        Example:
            >>> word = WordBox(10, 20, 50, 40, value="Hello")
            >>> list(word)
            ['Hello', 10, 20, 50, 40]
        """
        yield from [self.value, self.x0, self.y0, self.x2, self.y2]

    def __hash__(self) -> int:
        """Make WordBox hashable."""
        return hash(tuple(self.__dict__.items()))

    @classmethod
    def from_iterator(cls, iterator: Iterator[int]) -> WordBox:
        """
        Create WordBox from an iterable.

        Args:
            iterator: Sequence of [text, x0, y0, x2, y2]

        Returns:
            New WordBox instance

        Raises:
            TypeError: If iterator type or element types are invalid
            ValueError: If iterator doesn't contain exactly 5 elements

        Example:
            >>> word = WordBox.from_iterator(["Hello", 10, 20, 50, 40])
            >>> word.text
            'Hello'
        """
        if not isinstance(iterator, (list, tuple)):
            raise TypeError(
                f"Invalid iterator type. Expected [list, tuple]. Got {type(iterator)}"
            )

        if len(iterator) != 5:
            raise ValueError(
                f"Invalid length of iterator. Expected 5. Got {len(iterator)}"
            )

        if not isinstance(iterator[0], str):
            raise TypeError(
                f"Invalid first element type in the iterator. Expected: str. Got {type(iterator[0])}"
            )

        for i in range(1, 5):
            if not isinstance(iterator[i], (int, float)):
                raise TypeError(
                    f"Invalid element type in iterator. Expected: [int, float]. Got {type(iterator[i])}"
                )

        return cls(
            value=iterator[0],
            x0=int(iterator[1]),
            y0=int(iterator[2]),
            x2=int(iterator[3]),
            y2=int(iterator[4]),
        )
