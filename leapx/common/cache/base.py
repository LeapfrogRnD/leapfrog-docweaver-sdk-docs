"""Base cache service interface."""

from abc import ABC, abstractmethod
from typing import Any


class LeapXCache(ABC):
    """
    Abstract base class for cache services.

    Subclasses must implement all methods to define their specific caching behavior,
    serialization, and key generation.
    """

    @abstractmethod
    def init_cache(self):
        "Initialize the cache storage"
        pass

    @abstractmethod
    def _get_data_size_column(self) -> str:
        """
        Get the column name that stores data size for eviction.

        Returns:
            Column name (e.g., 'LENGTH(data)' or a specific column)
        """
        pass

    @abstractmethod
    def _get_cached_entry(self, cache_key: str) -> bytes | str | None:
        """
        Get cached data by key from repository.

        Args:
            cache_key: Cache key to look up

        Returns:
            Serialized data (bytes for BLOB, str for TEXT) if found and not
            expired, None otherwise
        """
        pass

    @abstractmethod
    def _set_cached_entry(
        self, cache_key: str, serialized_data: bytes | str, **extra_fields
    ) -> bool:
        """
        Store data in cache via repository.

        Args:
            cache_key: Cache key
            serialized_data: Serialized data (bytes for BLOB, str for TEXT)
            **extra_fields: Additional fields to store (must match table schema)

        Returns:
            True if successfully cached, False otherwise
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
    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
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
    def close(self):
        """Close the cache repository connection."""
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if cache service is enabled."""
        pass
