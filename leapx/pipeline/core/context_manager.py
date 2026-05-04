"""Context manager for maintaining state across chunk processing."""

from collections import deque
from typing import Any


class ContextProcessor:
    """Stores context from previous chunk processing.

    Attributes:
        chunk_index: Index of the chunk this context belongs to.
        ocr_output: OCR stage output.
        parsed_text: Parsed text from parser stage.
        llm_output: LLM extraction output.
        metadata: Additional metadata.
    """

    def __init__(
        self,
        chunk_index: int,
        ocr_output: dict[str, Any] | None = None,
        parsed_text: str | None = None,
        llm_output: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.chunk_index = chunk_index
        self.ocr_output = ocr_output
        self.parsed_text = parsed_text
        self.llm_output = llm_output
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "chunk_index": self.chunk_index,
            "ocr_output": self.ocr_output,
            "parsed_text": self.parsed_text,
            "llm_output": self.llm_output,
            "metadata": self.metadata,
        }


class ContextManager:
    """Manages context across chunk processing.

    Maintains a sliding window of previous chunk results to provide
    context for subsequent processing stages.

    Args:
        window_size: Number of previous chunks to maintain in context.
    """

    def __init__(self, window_size: int = 1):
        self.window_size = window_size
        self._context_history: deque[ContextProcessor] = deque(maxlen=window_size)
        self._current_context: ContextProcessor | None = None

    def start_chunk(self, chunk_index: int) -> None:
        """Start processing a new chunk.

        Args:
            chunk_index: Index of the chunk being processed.
        """
        self._current_context = ContextProcessor(chunk_index=chunk_index)

    def update_ocr(self, output: dict[str, Any]) -> None:
        """Update OCR output for current chunk.

        Args:
            output: OCR stage output data.
        """
        if self._current_context:
            self._current_context.ocr_output = output

    def update_parsed_text(
        self, text: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Update parsed text for current chunk.

        Args:
            text: Parsed text from parser stage.
            metadata: Optional metadata from parser stage.
        """
        if self._current_context:
            self._current_context.parsed_text = text
            if metadata:
                self._current_context.metadata.update(metadata)

    def update_llm_output(self, output: dict[str, Any]) -> None:
        """Update LLM output for current chunk.

        Args:
            output: LLM extraction output.
        """
        if self._current_context:
            self._current_context.llm_output = output

    def finalize_chunk(self) -> None:
        """Finalize current chunk and add to history."""
        if self._current_context:
            self._context_history.append(self._current_context)
            self._current_context = None

    def get_previous_contexts(self, count: int | None = None) -> list[ContextProcessor]:
        """Get previous chunk contexts.

        Args:
            count: Number of previous contexts to retrieve.
                  If None, returns all available contexts up to window_size.

        Returns:
            List of previous processing contexts, most recent first.
        """
        if count is None:
            count = self.window_size

        # Return most recent contexts first
        return list(reversed(list(self._context_history)))[:count]

    def get_previous_parsed_texts(self, count: int | None = None) -> list[str]:
        """Get parsed texts from previous chunks.

        Args:
            count: Number of previous texts to retrieve.

        Returns:
            List of parsed texts from previous chunks, most recent first.
        """
        contexts = self.get_previous_contexts(count)
        return [ctx.parsed_text for ctx in contexts if ctx.parsed_text]

    def get_previous_llm_outputs(
        self, count: int | None = None
    ) -> list[dict[str, Any]]:
        """Get LLM outputs from previous chunks.

        Args:
            count: Number of previous outputs to retrieve.

        Returns:
            List of LLM outputs from previous chunks, most recent first.
        """
        contexts = self.get_previous_contexts(count)
        return [ctx.llm_output for ctx in contexts if ctx.llm_output]

    def get_context_for_llm(self) -> dict[str, Any]:
        """Get formatted context for LLM processing.

        Returns:
            Dictionary containing:
            - previous_parsed_texts: List of parsed texts from previous chunks
            - previous_llm_outputs: List of LLM outputs from previous chunks
            - current_parsed_text: Parsed text from current chunk (if available)
        """
        previous_contexts = self.get_previous_contexts()

        return {
            "previous_parsed_texts": [
                ctx.parsed_text for ctx in previous_contexts if ctx.parsed_text
            ],
            "previous_llm_outputs": [
                ctx.llm_output for ctx in previous_contexts if ctx.llm_output
            ],
            "current_parsed_text": (
                self._current_context.parsed_text if self._current_context else None
            ),
        }

    def clear(self) -> None:
        """Clear all context history."""
        self._context_history.clear()
        self._current_context = None

    def to_dict(self) -> dict[str, Any]:
        """Convert context manager state to dictionary.

        Returns:
            Dictionary representation of context manager state.
        """
        return {
            "window_size": self.window_size,
            "context_history": [ctx.to_dict() for ctx in self._context_history],
            "current_context": (
                self._current_context.to_dict() if self._current_context else None
            ),
        }
