from abc import ABC, abstractmethod

from leapx.services.chunking.config import ChunkingConfig
from leapx.services.chunking.schemas import ChunkResult, InputType


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies.

    Args:
        config: Chunking configuration used by the strategy.
    """

    def __init__(self, config: ChunkingConfig) -> None:
        self.config = config

    @abstractmethod
    def chunk(
        self, input_data: str | bytes, input_type: InputType = InputType.FILE
    ) -> list[ChunkResult]:
        """Split input into chunks.

        Args:
            input_data: Path to PDF file, raw PDF bytes, or text string.
            input_type: Type of input (FILE or TEXT).

        Returns:
            List of ChunkResult objects representing chunks.
        """
        pass
