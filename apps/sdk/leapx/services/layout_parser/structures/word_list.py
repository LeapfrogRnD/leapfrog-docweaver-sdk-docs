"""WordList structure - Collection of WordBox objects with list operations."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from leapx.services.layout_parser.structures.bbox import BBox
from leapx.services.layout_parser.structures.word_box import WordBox


class WordListMixin:
    """
    Mixin providing list-like operations for collections of WordBox objects.

    This mixin provides core list operations (append, extend, indexing)
    and WordBox-specific operations (filtering, aggregation).

    Note: Classes using this mixin must define a `_words` attribute
    that is a list of WordBox objects.
    """

    _words: list[WordBox]

    def __len__(self) -> int:
        """Return number of words."""
        return len(self._words)

    def __iter__(self) -> Iterator[WordBox]:
        """Iterate over words."""
        return iter(self._words)

    def __getitem__(self, key: int | slice) -> WordBox | WordList:
        """
        Get word(s) by index or slice.

        Args:
            key: Integer index or slice

        Returns:
            WordBox if key is int, WordList if key is slice

        Example:
            >>> words = WordList([word1, word2, word3])
            >>> words[0]  # Get first word
            >>> words[1:3]  # Get slice as WordList
        """
        if isinstance(key, slice):
            from leapx.services.layout_parser.structures.word_list import WordList

            return WordList(self._words[key])
        return self._words[key]

    def __contains__(self, item: WordBox) -> bool:
        """Check if word is in collection."""
        return item in self._words

    def append(self, word: WordBox) -> None:
        """
        Add a word to the end.

        Args:
            word: WordBox to append
        """
        self._words.append(word)

    def extend(self, words: list[WordBox]) -> None:
        """
        Add multiple words to the end.

        Args:
            words: List of WordBox objects to append
        """
        self._words.extend(words)

    def insert(self, index: int, word: WordBox) -> None:
        """
        Insert word at specified index.

        Args:
            index: Position to insert at
            word: WordBox to insert
        """
        self._words.insert(index, word)

    def remove(self, word: WordBox) -> None:
        """
        Remove first occurrence of word.

        Args:
            word: WordBox to remove

        Raises:
            ValueError: If word not in collection
        """
        self._words.remove(word)

    def pop(self, index: int = -1) -> WordBox:
        """
        Remove and return word at index.

        Args:
            index: Position to pop from (default: -1, last item)

        Returns:
            WordBox that was removed

        Raises:
            IndexError: If index out of range
        """
        return self._words.pop(index)

    def clear(self) -> None:
        """Remove all words."""
        self._words.clear()

    def reverse(self) -> None:
        """Reverse the order of words in place."""
        self._words.reverse()

    def sort(self, key=None, reverse: bool = False) -> None:
        """
        Sort words in place.

        Args:
            key: Function to extract comparison key (default: None)
            reverse: Sort in descending order (default: False)
        """
        self._words.sort(key=key, reverse=reverse)

    @property
    def is_empty(self) -> bool:
        """Check if collection is empty."""
        return len(self._words) == 0

    def filter_by_text(self, text: str, case_sensitive: bool = False) -> WordList:
        """
        Filter words by text content.

        Args:
            text: Text to match
            case_sensitive: Whether to match case exactly (default: False)

        Returns:
            New WordList with matching words
        """
        from leapx.services.layout_parser.structures.word_list import WordList

        if case_sensitive:
            filtered = [w for w in self._words if w.text == text]
        else:
            text_lower = text.lower()
            filtered = [w for w in self._words if w.text.lower() == text_lower]

        return WordList(filtered)

    def filter_by_bbox(self, bbox: BBox, strict: bool = False) -> WordList:
        """
        Filter words that overlap with bbox.

        Args:
            bbox: Bounding box to filter by
            strict: If True, only include words fully contained in bbox

        Returns:
            New WordList with words overlapping bbox
        """
        from leapx.services.layout_parser.structures.word_list import WordList

        if strict:
            filtered = [
                w
                for w in self._words
                if w.x0 >= bbox.x0
                and w.y0 >= bbox.y0
                and w.x2 <= bbox.x2
                and w.y2 <= bbox.y2
            ]
        else:
            # Check for any overlap
            filtered = [
                w
                for w in self._words
                if not (
                    w.x2 < bbox.x0 or w.x0 > bbox.x2 or w.y2 < bbox.y0 or w.y0 > bbox.y2
                )
            ]

        return WordList(filtered)

    def get_text(self, separator: str = " ") -> str:
        """
        Get concatenated text of all words.

        Args:
            separator: String to join words with (default: space)

        Returns:
            Concatenated text string
        """
        return separator.join(w.text for w in self._words)

    def get_bounding_box(self) -> BBox | None:
        """
        Get bounding box encompassing all words.

        Returns:
            BBox covering all words, or None if empty
        """
        if self.is_empty:
            return None

        x0 = min(w.x0 for w in self._words)
        y0 = min(w.y0 for w in self._words)
        x2 = max(w.x2 for w in self._words)
        y2 = max(w.y2 for w in self._words)

        return BBox(x0=x0, y0=y0, x2=x2, y2=y2)


@dataclass
class WordList:
    """
    Collection of WordBox objects with list-like operations.

    Provides a convenient container for working with multiple WordBox objects,
    with methods for filtering, sorting, and aggregating.

    Attributes:
        _words: Internal list of WordBox objects

    Example:
        >>> word1 = WordBox(x0=0, y0=0, x2=10, y2=10, value="Hello")
        >>> word2 = WordBox(x0=15, y0=0, x2=35, y2=10, value="World")
        >>> words = WordList([word1, word2])
        >>> words.get_text()
        'Hello World'
        >>> len(words)
        2
    """

    _words: list[WordBox]

    def __init__(self, words: list[WordBox] | None = None):
        """
        Initialize WordList.

        Args:
            words: Initial list of WordBox objects (default: empty list)
        """
        self._words = words if words is not None else []

    # Include mixin functionality
    def __len__(self) -> int:
        return WordListMixin.__len__(self)

    def __iter__(self) -> Iterator[WordBox]:
        return WordListMixin.__iter__(self)

    def __getitem__(self, key: int | slice) -> WordBox | WordList:
        return WordListMixin.__getitem__(self, key)

    def __contains__(self, item: WordBox) -> bool:
        return WordListMixin.__contains__(self, item)

    def append(self, word: WordBox) -> None:
        WordListMixin.append(self, word)

    def extend(self, words: list[WordBox]) -> None:
        WordListMixin.extend(self, words)

    def insert(self, index: int, word: WordBox) -> None:
        WordListMixin.insert(self, index, word)

    def remove(self, word: WordBox) -> None:
        WordListMixin.remove(self, word)

    def pop(self, index: int = -1) -> WordBox:
        return WordListMixin.pop(self, index)

    def clear(self) -> None:
        WordListMixin.clear(self)

    def reverse(self) -> None:
        WordListMixin.reverse(self)

    def sort(self, key=None, reverse: bool = False) -> None:
        WordListMixin.sort(self, key=key, reverse=reverse)

    @property
    def is_empty(self) -> bool:
        return WordListMixin.is_empty.fget(self)

    def filter_by_text(self, text: str, case_sensitive: bool = False) -> WordList:
        return WordListMixin.filter_by_text(self, text, case_sensitive)

    def filter_by_bbox(self, bbox: BBox, strict: bool = False) -> WordList:
        return WordListMixin.filter_by_bbox(self, bbox, strict)

    def get_text(self, separator: str = " ") -> str:
        return WordListMixin.get_text(self, separator)

    def get_bounding_box(self) -> BBox | None:
        return WordListMixin.get_bounding_box(self)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"WordList({len(self._words)} words)"
