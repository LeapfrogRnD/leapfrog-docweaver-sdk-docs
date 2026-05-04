"""TextLine structure - Represents single line of text with words."""

from __future__ import annotations

from dataclasses import dataclass, field

from leapx.services.layout_parser.structures.bbox import BBox
from leapx.services.layout_parser.structures.ocr_word import OCRWord
from leapx.services.layout_parser.structures.word_list import WordListMixin


@dataclass
class TextLine(WordListMixin):
    """
    Represents a single line of text with its words.

    A text line is a horizontal sequence of words that appear
    on the same baseline. Used in layout analysis and text extraction.

    Attributes:
        _words: List of OCRWord objects in this line
        line_number: Line number within page/block
        page: Page number
        block: Block number
        metadata: Additional metadata dictionary

    Example:
        >>> word1 = OCRWord(x0=0, y0=0, x2=30, y2=10, value="Hello")
        >>> word2 = OCRWord(x0=35, y0=0, x2=70, y2=10, value="World")
        >>> line = TextLine(words=[word1, word2], line_number=0)
        >>> line.get_text()
        'Hello World'
        >>> line.word_count
        2
    """

    _words: list[OCRWord] = field(default_factory=list)
    line_number: int | None = None
    page: int = 0
    block: int | None = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialize from first word if available."""
        if self._words and self.page == 0:
            self.page = self._words[0].page
        if self._words and self.block is None:
            self.block = self._words[0].block

    @property
    def word_count(self) -> int:
        """Number of words in line."""
        return len(self._words)

    @property
    def text(self) -> str:
        """Get line text with words separated by spaces."""
        return self.get_text(separator=" ")

    @property
    def bbox(self) -> BBox | None:
        """Get bounding box of entire line."""
        return self.get_bounding_box()

    @property
    def avg_confidence(self) -> float:
        """
        Get average OCR confidence for line.

        Returns:
            Average confidence score, or -1 if no valid scores
        """
        if not self._words:
            return -1

        confidences = [w.confidence for w in self._words if w.confidence != -1]
        if not confidences:
            return -1

        return sum(confidences) / len(confidences)

    @property
    def height(self) -> float:
        """Get line height."""
        bbox = self.get_bounding_box()
        return bbox.height if bbox else 0

    @property
    def width(self) -> float:
        """Get line width."""
        bbox = self.get_bounding_box()
        return bbox.width if bbox else 0

    def get_words_by_confidence(self, min_confidence: float = 0.0) -> list[OCRWord]:
        """
        Get words with confidence above threshold.

        Args:
            min_confidence: Minimum confidence score (0.0 to 1.0)

        Returns:
            List of OCRWord objects meeting threshold
        """
        return [w for w in self._words if w.confidence >= min_confidence]

    def sort_by_position(self, vertical: bool = False) -> None:
        """
        Sort words by position.

        Args:
            vertical: If True, sort by y-coordinate (top to bottom)
                     If False, sort by x-coordinate (left to right)
        """
        if vertical:
            self._words.sort(key=lambda w: (w.y0, w.x0))
        else:
            self._words.sort(key=lambda w: (w.x0, w.y0))

    def __repr__(self) -> str:
        """Return string representation."""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f'TextLine(line={self.line_number}, words={self.word_count}, text="{text_preview}")'
