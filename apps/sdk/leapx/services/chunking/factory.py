from typing import ClassVar

from leapx.services.chunking.config import ChunkingConfig
from leapx.services.chunking.exceptions import InvalidChunkingError
from leapx.services.chunking.schemas import ChunkingMethod
from leapx.services.chunking.strategy.base import ChunkingStrategy
from leapx.services.chunking.strategy.batch_wise import BatchWiseChunking
from leapx.services.chunking.strategy.page_wise import PageWiseChunking


class ChunkingStrategyFactory:
    """Factory for creating chunking strategies.

    Keeps a registry of available strategies and instantiates the correct
    implementation based on configuration.
    """

    _strategies: ClassVar[dict[ChunkingMethod, type[ChunkingStrategy]]] = {
        ChunkingMethod.BATCH_WISE: BatchWiseChunking,
        ChunkingMethod.PAGE_WISE: PageWiseChunking,
    }

    @classmethod
    def create(cls, config: ChunkingConfig) -> ChunkingStrategy:
        """Create a chunking strategy from configuration.

        Args:
            config: Chunking configuration.

        Returns:
            An instantiated ChunkingStrategy implementation.

        Raises:
            InvalidChunkingError: If no strategy is registered for the method.
        """
        strategy_class = cls._strategies.get(config.method)

        if not strategy_class:
            raise InvalidChunkingError
        return strategy_class(config)

    @classmethod
    def register(
        cls,
        method: ChunkingMethod,
        strategy_class: type[ChunkingStrategy],
    ) -> None:
        """Register a custom chunking strategy implementation.

        Args:
            method: Chunking method identifier.
            strategy_class: Strategy class to register.
        """
        cls._strategies[method] = strategy_class
