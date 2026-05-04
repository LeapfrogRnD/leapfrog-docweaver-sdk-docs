"""Abstract base class for cache implementations."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class CacheFacadeInterface[TInput, TOutput](ABC):
    """
    Abstract base class for cache implementations.

    Provides common cache interface and utilities that concrete cache
    implementations can use. Handles cache key computation, serialization,
    and interaction with underlying cache storage.

    Type parameters:
        TInput: Type of input data used to generate cache keys
        TOutput: Type of output data stored in and retrieved from cache
    """

    @abstractmethod
    def _compute_cache_key(self, *args: Any, **kwargs: Any) -> str:
        """
        Compute cache key from input parameters.

        Must be implemented by concrete classes to define how cache keys
        are generated from input data.

        Returns:
            Cache key string
        """
        pass

    @abstractmethod
    def _serialize_data(self, data: TOutput) -> bytes | str:
        """
        Serialize data for storage.

        Must be implemented by concrete classes to define how output
        data is converted to a storable format.

        Args:
            data: Data to serialize

        Returns:
            Serialized data as bytes or string
        """
        pass

    @abstractmethod
    def _deserialize_data(self, serialized_data: bytes | str) -> TOutput:
        """
        Deserialize cached data back to original format.

        Must be implemented by concrete classes to define how stored
        data is converted back to the output type.

        Args:
            serialized_data: Serialized data from cache

        Returns:
            Deserialized data
        """
        pass

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> TOutput | None:
        """
        Get cached result.

        Must be implemented by concrete classes to define the interface
        for retrieving cached data.

        Returns:
            Cached data if cache hit, None if cache miss
        """
        pass

    @abstractmethod
    def set(self, *args: Any, **kwargs: Any) -> bool:
        """
        Store result in cache.

        Must be implemented by concrete classes to define the interface
        for storing data in cache.

        Returns:
            True if successfully cached, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, *args: Any, **kwargs: Any) -> bool:
        """
        Delete specific cache entry.

        Default implementation - can be overridden by concrete classes
        if they need custom deletion logic.

        Returns:
            True if deleted, False otherwise
        """
        pass
