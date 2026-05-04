"""CombinedWord structure - Merges multiple OCRWords into single entity."""

from __future__ import annotations

from dataclasses import dataclass, field

from leapx.services.layout_parser.structures.ocr_word import OCRWord
from leapx.services.layout_parser.structures.word_list import WordListMixin


@dataclass
class CombinedWord(WordListMixin):
    """
    Represents multiple OCRWords combined into a single logical word.

    Used when OCR splits a single word into multiple fragments,
    or when combining words across line breaks.

    Attributes:
        _words: List of OCRWord objects being combined
        index: Combined word index
        space_type: Space type after combined word
        block: Block number (from first word)
        page: Page number (from first word)
        line: Line number (from first word)
        confidence: Average confidence of all words

    Example:
        >>> word1 = OCRWord(x0=0, y0=0, x2=20, y2=10, value="hel", confidence=0.9)
        >>> word2 = OCRWord(x0=20, y0=0, x2=40, y2=10, value="lo", confidence=0.95)
        >>> combined = CombinedWord(words=[word1, word2])
        >>> combined.text
        'hello'
        >>> combined.confidence
        0.925
    """

    _words: list[OCRWord] = field(default_factory=list)
    index: int | None = None
    space_type: int | None = None
    block: int | None = None
    page: int = 0
    line: int | None = None

    def __post_init__(self):
        """Initialize from first word if available."""
        if self._words:
            first_word = self._words[0]
            if self.block is None:
                self.block = first_word.block
            if self.page == 0:
                self.page = first_word.page
            if self.line is None:
                self.line = first_word.line
            if self.index is None:
                self.index = first_word.index

    @property
    def text(self) -> str:
        """Get combined text from all words."""
        return "".join(w.text for w in self._words)

    @property
    def confidence(self) -> float:
        """
        Get average confidence of all words.

        Returns:
            Average confidence score, or -1 if no words or all unknown
        """
        if not self._words:
            return -1

        confidences = [w.confidence for w in self._words if w.confidence != -1]
        if not confidences:
            return -1

        return sum(confidences) / len(confidences)

    @property
    def bbox(self):
        """Get bounding box encompassing all words."""
        return self.get_bounding_box()

    @property
    def x0(self) -> float:
        """Left x-coordinate."""
        bbox = self.get_bounding_box()
        return bbox.x0 if bbox else 0

    @property
    def y0(self) -> float:
        """Top y-coordinate."""
        bbox = self.get_bounding_box()
        return bbox.y0 if bbox else 0

    @property
    def x2(self) -> float:
        """Right x-coordinate."""
        bbox = self.get_bounding_box()
        return bbox.x2 if bbox else 0

    @property
    def y2(self) -> float:
        """Bottom y-coordinate."""
        bbox = self.get_bounding_box()
        return bbox.y2 if bbox else 0

    def to_ocr_word(self) -> OCRWord:
        """
        Convert to single OCRWord.

        Returns:
            OCRWord with combined text and averaged properties
        """
        bbox = self.get_bounding_box()
        return OCRWord(
            x0=bbox.x0 if bbox else 0,
            y0=bbox.y0 if bbox else 0,
            x2=bbox.x2 if bbox else 0,
            y2=bbox.y2 if bbox else 0,
            value=self.text,
            index=self.index,
            space_type=self.space_type,
            block=self.block,
            confidence=self.confidence,
            page=self.page,
            line=self.line,
        )

    def __repr__(self) -> str:
        """Return string representation."""
        return f'CombinedWord("{self.text}", {len(self._words)} words)'
