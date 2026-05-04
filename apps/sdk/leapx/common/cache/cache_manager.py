"""Cache repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CacheManager(ABC):
    """
    Abstract repository interface for cache operations.

    Defines the contract that all cache repository implementations must follow.
    Manager handle low-level data persistence operations.
    """

    @abstractmethod
    def get(self, cache_key: str) -> bytes | None:
        """
        Get cached data by key.

        Args:
            cache_key: Cache key to look up

        Returns:
            Serialized data bytes if found and not expired, None otherwise
        """
        pass

    @abstractmethod
    def set(
        self,
        cache_key: str,
        serialized_data: bytes,
        data_size_column: str,
        **extra_fields,
    ) -> bool:
        """
        Store data in cache.

        Args:
            cache_key: Cache key
            serialized_data: Serialized data bytes
            data_size_column: SQL expression for data size (for eviction)
            **extra_fields: Additional fields to store (must match table schema)

        Returns:
            True if successfully cached, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, cache_key: str) -> bool:
        """
        Delete specific cache entry.

        Args:
            cache_key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_stats(self, data_size_column: str) -> dict[str, Any]:
        """
        Get cache statistics.

        Args:
            data_size_column: SQL expression for data size

        Returns:
            Dictionary with cache statistics
        """
        pass

    @abstractmethod
    def cleanup_expired(self):
        """Remove expired cache entries."""
        pass

    @abstractmethod
    def close(self):
        """Close the cache database connection."""
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if cache is enabled and connected."""
        pass
