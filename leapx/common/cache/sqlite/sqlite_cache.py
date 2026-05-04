"""SQLite cache service implementation."""

from typing import Any

from leapx.common.cache.base import LeapXCache
from leapx.common.cache.cache_config import CacheConfig, CacheProviderType
from leapx.common.cache.cache_factory import register_cache_provider
from leapx.common.cache.sqlite.sqlite_manager import SqliteManager
from leapx.common.observability.logger import logger


@register_cache_provider(CacheProviderType.SQLITE)
class SqliteCache(LeapXCache):
    """
    SQLite-based cache service implementation.

    This is the base service class that uses SqliteManager for data persistence.
    Specific cache implementations (like OCR cache) should extend this class.
    """

    def __init__(self, config: CacheConfig, **kwargs):
        """
        Initialize SQLite cache service.

        Args:
            config: Cache configuration
            cache_name: Optional name for the cache (overrides class name)
        """
        self.config = config
        self._manager = None
        self._cache_name = kwargs.get("cache_name", "")

    def init_cache(self):
        """Initialize the file cache storage."""
        if self.config.enabled:
            cache_name = self._cache_name or self.__class__.__name__
            self._manager = SqliteManager(
                config=self.config,
                cache_name=cache_name,
            )
        else:
            logger.info(f"{self.__class__.__name__} disabled")
        return self

    def _get_data_size_column(self) -> str:
        """
        Get the column name that stores data size for eviction.

        Returns:
            Column name
        """
        return "LENGTH(data)"

    def _get_cached_entry(self, cache_key: str) -> bytes | str | None:
        """
        Get cached data by key from manager.

        Args:
            cache_key: Cache key to look up

        Returns:
            Serialized data (bytes for BLOB, str for TEXT) if found and not
            expired, None otherwise
        """
        if self._manager is None:
            return None
        return self._manager.get(cache_key)

    def _set_cached_entry(
        self, cache_key: str, serialized_data: bytes | str, **extra_fields
    ) -> bool:
        """
        Store data in cache via manager.

        Args:
            cache_key: Cache key
            serialized_data: Serialized data (bytes for BLOB, str for TEXT)
            **extra_fields: Additional fields to store (must match table schema)

        Returns:
            True if successfully cached, False otherwise
        """
        if self._manager is None:
            return False
        return self._manager.set(
            cache_key, serialized_data, self._get_data_size_column(), **extra_fields
        )

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        if self._manager is None:
            return False
        return self._manager.clear()

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if self._manager is None:
            return {"enabled": False}
        return self._manager.get_stats(self._get_data_size_column())

    def delete(self, cache_key: str) -> bool:
        """
        Delete specific cache entry.

        Args:
            cache_key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if self._manager is None:
            return False
        return self._manager.delete(cache_key)

    def close(self):
        """Close the cache manager connection."""
        if self._manager is not None:
            self._manager.close()

    @property
    def is_enabled(self) -> bool:
        """Check if cache service is enabled."""
        return self._manager is not None and self._manager.is_enabled
