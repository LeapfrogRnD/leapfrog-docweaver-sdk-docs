"""File-based cache manager implementation."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from leapx.common.cache.cache_manager import CacheManager
from leapx.common.observability.logger import logger

if TYPE_CHECKING:
    from leapx.common.cache.cache_config import CacheConfig


class FileCacheMetadata:
    """Metadata for a cache entry."""

    def __init__(  # noqa: PLR0913
        self,
        cache_key: str,
        cached_at: str,
        expires_at: str | None = None,
        access_count: int = 0,
        last_accessed: str | None = None,
        data_size: int = 0,
        **extra_fields,
    ):
        self.cache_key = cache_key
        self.cached_at = cached_at
        self.expires_at = expires_at
        self.access_count = access_count
        self.last_accessed = last_accessed
        self.data_size = data_size
        self.extra_fields = extra_fields

    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        data = {
            "cache_key": self.cache_key,
            "cached_at": self.cached_at,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "data_size": self.data_size,
        }
        data.update(self.extra_fields)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> FileCacheMetadata:
        """Create metadata from dictionary."""
        return cls(**data)


class FileManager(CacheManager):
    """
    File-based implementation of the cache manager.

    Stores cache entries as individual files in a directory structure,
    with metadata stored in JSON sidecar files.
    """

    def __init__(
        self,
        config: CacheConfig,
        *,
        cache_name: str = "Cache",
    ):
        """
        Initialize file-based cache manager.

        Args:
            config: Cache configuration
            cache_subdir: Subdirectory name for this cache type
            cache_name: Human-readable cache name for logging
        """
        self._lock = threading.RLock()
        self.config = config
        self.cache_name = cache_name
        self._cache_dir: Path | None = None
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize the file-based cache."""
        try:
            # Create cache directory structure
            self._cache_dir = Path("/tmp") / ".leapx_cache" / "file_cache"
            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for data and metadata
            (self._cache_dir / "data").mkdir(exist_ok=True)
            (self._cache_dir / "metadata").mkdir(exist_ok=True)

            # Clean up expired entries on initialization
            self.cleanup_expired()

            logger.info(
                f"{self.cache_name} initialized",
                cache_dir=str(self._cache_dir),
                ttl=self.config.ttl,
                size_limit=self.config.size_limit,
            )

        except Exception as e:
            logger.error(f"Failed to initialize file cache: {e}")
            self.config.enabled = False
            self._cache_dir = None

    def _get_data_path(self, cache_key: str) -> Path:
        """Get the path to the data file for a cache key."""
        return self._cache_dir / "data" / f"{cache_key}.bin"

    def _get_metadata_path(self, cache_key: str) -> Path:
        """Get the path to the metadata file for a cache key."""
        return self._cache_dir / "metadata" / f"{cache_key}.json"

    def _read_metadata(self, cache_key: str) -> FileCacheMetadata | None:
        """Read metadata for a cache entry."""
        metadata_path = self._get_metadata_path(cache_key)
        if not metadata_path.exists():
            return None

        try:
            with metadata_path.open() as f:
                data = json.load(f)
            return FileCacheMetadata.from_dict(data)
        except Exception as e:
            logger.error(f"Error reading metadata: {e}", cache_key=cache_key[:16])
            return None

    def _write_metadata(self, metadata: FileCacheMetadata) -> bool:
        """Write metadata for a cache entry."""
        metadata_path = self._get_metadata_path(metadata.cache_key)
        try:
            with metadata_path.open("w") as f:
                json.dump(metadata.to_dict(), f)
        except Exception as e:
            logger.error(
                f"Error writing metadata: {e}", cache_key=metadata.cache_key[:16]
            )
            return False
        else:
            return True

    def _delete_entry(self, cache_key: str) -> bool:
        """Delete both data and metadata files for a cache entry."""
        data_path = self._get_data_path(cache_key)
        metadata_path = self._get_metadata_path(cache_key)

        success = True
        if data_path.exists():
            try:
                data_path.unlink()
            except Exception as e:
                logger.error(f"Error deleting data file: {e}")
                success = False

        if metadata_path.exists():
            try:
                metadata_path.unlink()
            except Exception as e:
                logger.error(f"Error deleting metadata file: {e}")
                success = False

        return success

    def _is_expired(self, metadata: FileCacheMetadata) -> bool:
        """Check if a cache entry is expired."""
        if metadata.expires_at is None:
            return False

        now = datetime.now()
        expires_at = datetime.fromisoformat(metadata.expires_at)
        return now > expires_at

    def _list_all_cache_keys(self) -> list[str]:
        """List all cache keys in the cache directory."""
        if not self._cache_dir:
            return []

        metadata_dir = self._cache_dir / "metadata"
        if not metadata_dir.exists():
            return []

        cache_keys = []
        for metadata_file in metadata_dir.glob("*.json"):
            cache_key = metadata_file.stem
            cache_keys.append(cache_key)

        return cache_keys

    def cleanup_expired(self):
        """Remove expired cache entries."""
        if not self._cache_dir:
            return

        try:
            with self._lock:
                cache_keys = self._list_all_cache_keys()
                deleted = 0

                for cache_key in cache_keys:
                    metadata = self._read_metadata(cache_key)
                    if (
                        metadata
                        and self._is_expired(metadata)
                        and self._delete_entry(cache_key)
                    ):
                        deleted += 1

                if deleted > 0:
                    logger.debug(f"Cleaned up {deleted} expired cache entries")
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")

    def _enforce_size_limit(self, data_size_column: str):  # noqa: ARG002
        """
        Enforce cache size limit using configured eviction policy.

        Args:
            data_size_column: Not used for file cache (kept for interface compatibility)
        """
        if not self._cache_dir or self.config.size_limit <= 0:
            return

        try:
            with self._lock:
                # Get all cache entries with their metadata
                cache_keys = self._list_all_cache_keys()
                entries = []
                total_size = 0

                for cache_key in cache_keys:
                    metadata = self._read_metadata(cache_key)
                    if metadata:
                        entries.append(metadata)
                        total_size += metadata.data_size

                if total_size > self.config.size_limit:
                    # Sort entries based on eviction policy
                    if self.config.eviction_policy == "least-recently-stored":
                        entries.sort(key=lambda x: x.cached_at)
                    elif self.config.eviction_policy == "least-recently-used":
                        entries.sort(
                            key=lambda x: (
                                x.last_accessed or x.cached_at,
                                x.cached_at,
                            )
                        )
                    else:
                        entries.sort(key=lambda x: x.cached_at)

                    # Remove oldest entries until under limit
                    size_to_free = total_size - self.config.size_limit
                    freed = 0
                    deleted_count = 0

                    for entry in entries:
                        if self._delete_entry(entry.cache_key):
                            freed += entry.data_size
                            deleted_count += 1

                        if freed >= size_to_free:
                            break

                    if deleted_count > 0:
                        logger.debug(
                            f"Evicted {deleted_count} cache entries to enforce size limit"
                        )

        except Exception as e:
            logger.error(f"Error enforcing size limit: {e}")

    def get(self, cache_key: str) -> bytes | None:
        """
        Get cached data by key.

        Args:
            cache_key: Cache key to look up

        Returns:
            Serialized data bytes if found and not expired, None otherwise
        """
        if not self.config.enabled or not self._cache_dir:
            return None

        try:
            # Read metadata first
            metadata = self._read_metadata(cache_key)
            if not metadata:
                logger.debug(
                    f"{self.cache_name} cache MISS (no metadata)",
                    cache_key=cache_key[:16] + "...",
                )
                return None

            # Check expiration
            if self._is_expired(metadata):
                logger.debug(
                    f"{self.cache_name} cache MISS (expired)",
                    cache_key=cache_key[:16] + "...",
                )
                self._delete_entry(cache_key)
                return None

            # Read data
            data_path = self._get_data_path(cache_key)
            if not data_path.exists():
                logger.debug(
                    f"{self.cache_name} cache MISS (no data)",
                    cache_key=cache_key[:16] + "...",
                )
                # Clean up orphaned metadata
                self._delete_entry(cache_key)
                return None

            with data_path.open("rb") as f:
                data = f.read()

            # Update access statistics
            with self._lock:
                metadata.access_count += 1
                metadata.last_accessed = datetime.now().isoformat()
                self._write_metadata(metadata)

            logger.info(
                f"{self.cache_name} cache HIT",
                cache_key=cache_key[:16] + "...",
            )
        except Exception as e:
            logger.error(f"Error reading from cache: {e}", cache_key=cache_key[:16])
            return None
        else:
            return data

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
            data_size_column: Not used for file cache (kept for interface compatibility)
            **extra_fields: Additional fields to store in metadata

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.config.enabled or not self._cache_dir:
            return False

        try:
            with self._lock:
                now = datetime.now()

                # Calculate expiration time
                expires_at = None
                if self.config.ttl > 0:
                    expires_at = (now + timedelta(seconds=self.config.ttl)).isoformat()

                # Write data file
                data_path = self._get_data_path(cache_key)
                with data_path.open("wb") as f:
                    f.write(serialized_data)

                # Create and write metadata
                metadata = FileCacheMetadata(
                    cache_key=cache_key,
                    cached_at=now.isoformat(),
                    expires_at=expires_at,
                    access_count=0,
                    last_accessed=now.isoformat(),
                    data_size=len(serialized_data),
                    **extra_fields,
                )

                if not self._write_metadata(metadata):
                    # Clean up data file if metadata write failed
                    data_path.unlink(missing_ok=True)
                    return False

                # Enforce size limit if configured
                self._enforce_size_limit(data_size_column)

                logger.info(
                    f"{self.cache_name} data cached",
                    cache_key=cache_key[:16] + "...",
                    ttl=self.config.ttl,
                )
                return True

        except Exception as e:
            logger.error(f"Error writing to cache: {e}", cache_key=cache_key[:16])
            # Clean up partial files
            self._delete_entry(cache_key)
            return False

    def delete(self, cache_key: str) -> bool:
        """
        Delete specific cache entry.

        Args:
            cache_key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if not self.config.enabled or not self._cache_dir:
            return False

        try:
            with self._lock:
                success = self._delete_entry(cache_key)
                if success:
                    logger.info("Cache entry deleted", cache_key=cache_key[:16] + "...")
                return success
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or not self._cache_dir:
            return False

        try:
            with self._lock:
                cache_keys = self._list_all_cache_keys()
                for cache_key in cache_keys:
                    self._delete_entry(cache_key)

                logger.info(f"{self.cache_name} cache cleared")
                return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def get_stats(self, data_size_column: str) -> dict[str, Any]:  # noqa: ARG002
        """
        Get cache statistics.

        Args:
            data_size_column: Not used for file cache (kept for interface compatibility)

        Returns:
            Dictionary with cache statistics
        """
        if not self.config.enabled or not self._cache_dir:
            return {"enabled": False}

        try:
            cache_keys = self._list_all_cache_keys()
            total_size = 0
            total_accesses = 0
            count = 0

            for cache_key in cache_keys:
                metadata = self._read_metadata(cache_key)
                if metadata:
                    total_size += metadata.data_size
                    total_accesses += metadata.access_count
                    count += 1

            return {
                "enabled": True,
                "cache_dir": str(self._cache_dir),
                "count": count,
                "size": total_size,
                "size_limit": self.config.size_limit,
                "ttl": self.config.ttl,
                "total_accesses": total_accesses,
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}

    def close(self):
        """Close the cache (no-op for file-based cache)."""
        if self._cache_dir is not None:
            logger.debug(f"{self.cache_name} cache closed")

    @property
    def is_enabled(self) -> bool:
        """Check if cache is enabled and initialized."""
        return self.config.enabled and self._cache_dir is not None
