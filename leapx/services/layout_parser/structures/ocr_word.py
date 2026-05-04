"""OCRWord structure - WordBox with OCR metadata."""

from __future__ import annotations

from dataclasses import dataclass, field

from leapx.services.layout_parser.structures.word_box import WordBox


@dataclass
class OCRWord(WordBox):
    """
    WordBox with OCR-specific metadata.

    Extends WordBox with additional information from OCR engines
    such as confidence scores, page/block/line numbers, and spacing.

    Attributes:
        x0: Left x-coordinate (inherited)
        y0: Top y-coordinate (inherited)
        x2: Right x-coordinate (inherited)
        y2: Bottom y-coordinate (inherited)
        value: Text content (inherited)
        index: Word index (inherited)
        space_type: Type of space after word (0=none, 1=space, 2+=newline)
        block: Block number from OCR
        confidence: OCR confidence score (0.0 to 1.0, -1 if unknown)
        page: Page number (0-indexed)
        line: Line number within page
        metadata: Additional metadata dictionary

    Example:
        >>> word = OCRWord(
        ...     x0=10, y0=20, x2=50, y2=40,
        ...     value="Hello",
        ...     confidence=0.95,
        ...     page=0,
        ...     block=1,
        ...     line=0
        ... )
        >>> word.confidence
        0.95
    """

    space_type: int | None = None
    block: int | None = None
    confidence: float = -1
    page: int = 0
    line: int | None = None
    metadata: dict = field(default_factory=dict)

    def __hash__(self) -> int:
        """
        Make OCRWord hashable.

        Note: metadata dict is excluded from hash to allow hashing.
        """
        dct = self.__dict__.copy()
        dct.pop("metadata", None)
        return hash(tuple(dct.items()))
