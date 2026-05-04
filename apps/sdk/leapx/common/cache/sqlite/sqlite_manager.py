"""SQLite cache manager implementation."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple

from leapx.common.cache.cache_manager import CacheManager
from leapx.common.observability.logger import logger

if TYPE_CHECKING:
    from leapx.common.cache.cache_config import CacheConfig


class SqliteCacheSchema(NamedTuple):
    """Schema definition for cache table."""

    table_schemas: list[str]
    index_definitions: list[str]


class SqliteManager(CacheManager):
    """
    SQLite implementation of the cache manager.

    Handles all SQLite database interactions including initialization, CRUD operations,
    expiration cleanup, and size limit enforcement.
    """

    def __init__(
        self,
        config: CacheConfig,
        *,
        cache_name: str = "Cache",
    ):
        """
        Initialize SQLite cache manager.

        Args:
            config: Cache configuration
            schema: Cache schema definition (table name, schema, and indexes)
            db_name: Name of the SQLite database file
            cache_name: Human-readable cache name for logging
        """
        self._conn: sqlite3.Connection | None = None
        self._db_path: Path | None = None
        self._lock = threading._RLock()
        self.config = config
        self.cache_name = cache_name
        self._cache_dir = Path("/tmp") / ".leapx_cache"
        self.table_name = self._get_table_name()
        self.schema = self._get_cache_schema()
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize the SQLite database."""
        try:
            # Ensure cache directory exists
            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Create database file
            self._db_path = self._cache_dir / "leapx_cache.db"
            self._conn = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                isolation_level=None,  # Autocommit mode
            )

            # Enable WAL mode for better concurrency
            self._conn.execute("PRAGMA journal_mode=WAL")

            # Create cache tables
            for index_sql in self.schema.table_schemas:
                self._conn.execute(index_sql)

            # Create indexes
            for index_sql in self.schema.index_definitions:
                self._conn.execute(index_sql)

            # Clean up expired entries on initialization
            self.cleanup_expired()

            logger.info(
                f"{self.cache_name} initialized",
                cache_dir=str(self._cache_dir),
                ttl=self.config.ttl,
                size_limit=self.config.size_limit,
            )

        except Exception as e:
            logger.error(f"Failed to initialize SQLite cache: {e}")
            self.config.enabled = False
            if self._conn:
                self._conn.close()
                self._conn = None

    def _get_table_name(self) -> str:
        """Get the table name based on cache type."""
        cache_name_lower = self.cache_name.lower()
        if "ocr" in cache_name_lower:
            return "ocr_cache"
        if "extraction" in cache_name_lower:
            return "extraction_cache"

        return None

    def _get_table_schemas(self) -> str:
        """
        Get the CREATE TABLE SQL statement.

        Override this in subclasses for specific schemas.

        Returns:
            SQL CREATE TABLE statement
        """
        return [
            """
            CREATE TABLE IF NOT EXISTS ocr_cache (
                cache_key TEXT PRIMARY KEY,
                data BLOB NOT NULL,
                provider TEXT NOT NULL,
                cached_at TEXT NOT NULL,
                expires_at TEXT,
                file_size INTEGER,
                pages INTEGER,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS extraction_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                model TEXT NOT NULL,
                cached_at TEXT NOT NULL,
                expires_at TEXT,
                request_size INTEGER,
                response_size INTEGER,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT
            )
            """,
        ]

    def _get_index_definitions(self) -> list[str]:
        """
        Get list of CREATE INDEX SQL statements.

        Override this in subclasses for specific indexes.

        Returns:
            List of CREATE INDEX statements
        """
        return [
            "CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON ocr_cache(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_cache_cached_at ON ocr_cache(cached_at)",
            "CREATE INDEX IF NOT EXISTS idx_cache_last_accessed ON ocr_cache(last_accessed)",
            "CREATE INDEX IF NOT EXISTS idx_extraction_expires_at ON extraction_cache(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_extraction_model ON extraction_cache(model)",
        ]

    def _get_cache_schema(self) -> SqliteCacheSchema:
        """
        Get the cache schema for this service.

        Returns:
            CacheSchema instance
        """
        return SqliteCacheSchema(
            table_schemas=self._get_table_schemas(),
            index_definitions=self._get_index_definitions(),
        )

    def cleanup_expired(self):
        """Remove expired cache entries."""
        if not self._conn:
            return

        try:
            with self._lock:
                now = datetime.now().isoformat()
                cursor = self._conn.execute(
                    f"DELETE FROM {self.table_name} WHERE expires_at IS NOT NULL AND expires_at < ?",
                    (now,),
                )
                deleted = cursor.rowcount
                if deleted > 0:
                    logger.debug(f"Cleaned up {deleted} expired cache entries")
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")

    def _enforce_size_limit(self, data_size_column: str):
        """
        Enforce cache size limit using configured eviction policy.

        Args:
            data_size_column: SQL expression for data size (e.g., 'LENGTH(data)')
        """
        if not self._conn or self.config.size_limit <= 0:
            return

        try:
            with self._lock:
                # Get current total size
                cursor = self._conn.execute(
                    f"SELECT SUM({data_size_column}) FROM {self.table_name}"
                )
                total_size = cursor.fetchone()[0] or 0

                if total_size > self.config.size_limit:
                    # Evict entries based on policy
                    if self.config.eviction_policy == "least-recently-stored":
                        order_by = "cached_at ASC"
                    elif self.config.eviction_policy == "least-recently-used":
                        order_by = "last_accessed ASC, cached_at ASC"
                    else:
                        order_by = "cached_at ASC"  # Default

                    # Remove oldest entries until under limit
                    cursor = self._conn.execute(f"""
                        SELECT cache_key, {data_size_column} as size
                        FROM {self.table_name}
                        ORDER BY {order_by}
                    """)

                    size_to_free = total_size - self.config.size_limit
                    freed = 0
                    keys_to_delete = []

                    for cache_key, entry_size in cursor:
                        keys_to_delete.append(cache_key)
                        freed += entry_size
                        if freed >= size_to_free:
                            break

                    if keys_to_delete:
                        placeholders = ",".join("?" * len(keys_to_delete))
                        self._conn.execute(
                            f"DELETE FROM {self.table_name} WHERE cache_key IN ({placeholders})",
                            keys_to_delete,
                        )
                        logger.debug(
                            f"Evicted {len(keys_to_delete)} cache entries to enforce size limit"
                        )

        except Exception as e:
            logger.error(f"Error enforcing size limit: {e}")

    def get(self, cache_key: str) -> bytes | str | None:
        """
        Get cached data by key.

        Args:
            cache_key: Cache key to look up

        Returns:
            Serialized data (bytes for BLOB, str for TEXT) if found and not
            expired, None otherwise
        """
        if not self.config.enabled or self._conn is None:
            return None

        try:
            now = datetime.now().isoformat()
            cursor = self._conn.execute(
                f"""
                SELECT data
                FROM {self.table_name}
                WHERE cache_key = ?
                AND (expires_at IS NULL OR expires_at > ?)
                """,
                (cache_key, now),
            )

            row = cursor.fetchone()

            if row is not None:
                # Update access statistics - this is a write operation, needs lock
                with self._lock:
                    self._conn.execute(
                        f"""
                        UPDATE {self.table_name}
                        SET access_count = access_count + 1,
                            last_accessed = ?
                        WHERE cache_key = ?
                        """,
                        (now, cache_key),
                    )

                logger.info(
                    f"{self.cache_name} cache HIT",
                    cache_key=cache_key[:16] + "...",
                )
                return row[0]

            logger.debug(
                f"{self.cache_name} cache MISS",
                cache_key=cache_key[:16] + "...",
            )
        except Exception as e:
            logger.error(f"Error reading from cache: {e}", cache_key=cache_key[:16])

        return None

    def set(
        self,
        cache_key: str,
        serialized_data: bytes | str,
        data_size_column: str,
        **extra_fields,
    ) -> bool:
        """
        Store data in cache.

        Args:
            cache_key: Cache key
            serialized_data: Serialized data (bytes for BLOB or str for TEXT)
            data_size_column: SQL expression for data size (for eviction)
            **extra_fields: Additional fields to store (must match table schema)

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.config.enabled or self._conn is None:
            return False

        try:
            with self._lock:
                now = datetime.now()

                # Calculate expiration time
                expires_at = None
                if self.config.ttl > 0:
                    expires_at = (now + timedelta(seconds=self.config.ttl)).isoformat()

                # Build INSERT statement dynamically
                base_fields = {
                    "cache_key": cache_key,
                    "data": serialized_data,
                    "cached_at": now.isoformat(),
                    "expires_at": expires_at,
                    "access_count": 0,
                    "last_accessed": now.isoformat(),
                }
                base_fields.update(extra_fields)

                columns = ", ".join(base_fields.keys())
                placeholders = ", ".join("?" * len(base_fields))
                values = tuple(base_fields.values())

                self._conn.execute(
                    f"""
                    INSERT OR REPLACE INTO {self.table_name}
                    ({columns})
                    VALUES ({placeholders})
                    """,
                    values,
                )

                # Enforce size limit if configured
                self._enforce_size_limit(data_size_column)

                logger.info(
                    f"{self.cache_name} data cached",
                    cache_key=cache_key[:16] + "...",
                    ttl=self.config.ttl,
                )
        except Exception as e:
            logger.error(f"Error writing to cache: {e}", cache_key=cache_key[:16])
            return False
        else:
            return True

    def delete(self, cache_key: str) -> bool:
        """
        Delete specific cache entry.

        Args:
            cache_key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if not self.config.enabled or self._conn is None:
            return False

        try:
            with self._lock:
                cursor = self._conn.execute(
                    f"DELETE FROM {self.table_name} WHERE cache_key = ?",
                    (cache_key,),
                )
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
            return False
        else:
            if cursor.rowcount > 0:
                logger.info("Cache entry deleted", cache_key=cache_key[:16] + "...")
                return True
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled or self._conn is None:
            return False

        try:
            with self._lock:
                self._conn.execute(f"DELETE FROM {self.table_name}")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
        else:
            logger.info(f"{self.cache_name} cache cleared")
            return True

    def get_stats(self, data_size_column: str) -> dict[str, Any]:
        """
        Get cache statistics.

        Args:
            data_size_column: SQL expression for data size

        Returns:
            Dictionary with cache statistics
        """
        if not self.config.enabled or self._conn is None:
            return {"enabled": False}

        try:
            cursor = self._conn.execute(
                f"""
                SELECT
                    COUNT(*) as count,
                    SUM({data_size_column}) as total_size,
                    SUM(access_count) as total_accesses
                FROM {self.table_name}
                """
            )
            row = cursor.fetchone()

            return {
                "enabled": True,
                "cache_dir": str(self._cache_dir),
                "db_path": str(self._db_path),
                "count": row[0] or 0,
                "size": row[1] or 0,
                "size_limit": self.config.size_limit,
                "ttl": self.config.ttl,
                "total_accesses": row[2] or 0,
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}

    def close(self):
        """Close the cache database connection."""
        if self._conn is not None:
            try:
                with self._lock:
                    self._conn.close()
                    logger.debug(f"{self.cache_name} cache closed")
            except Exception as e:
                logger.error(f"Error closing cache: {e}")
            finally:
                self._conn = None

    @property
    def is_enabled(self) -> bool:
        """Check if cache is enabled and connected."""
        return self.config.enabled and self._conn is not None
