"""Disk cache implementation for OCR results using SQLite."""

import pickle

import pandas as pd

from leapx.common.cache import (
    CacheConfig,
    CacheFacadeInterface,
    CacheFactory,
    CacheUtils,
)
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.structures.ocr_data import OCRData


class OCRCacheFacade(CacheFacadeInterface[bytes, list[OCRData]]):
    """
    Disk-based cache for OCR results using SQLite.

    Uses SqliteCache service which delegates to SqliteRepository for
    persistent, thread-safe caching with automatic eviction and TTL management.
    """

    def __init__(self, config: CacheConfig):
        """
        Initialize OCR disk cache.

        Args:
            config: Cache configuration (uses default if None)
        """
        self.cache = CacheFactory.create_cache(config, cache_name="ocr_cache")

    def _compute_cache_key(
        self, file_content: bytes, provider: str, additional_context: str = ""
    ) -> str:
        """Compute cache key for OCR data."""
        return CacheUtils.compute_cache_key(provider, file_content, additional_context)

    def _serialize_data(self, ocr_data_list: list[OCRData]) -> bytes:
        """
        Serialize list of OCRData for storage.

        Args:
            ocr_data_list: List of OCRData objects

        Returns:
            Serialized bytes
        """
        # Convert to serializable format
        serializable_data = [
            {
                "df": ocr_data.df.to_dict(orient="records"),
                "metadata": ocr_data.metadata,
            }
            for ocr_data in ocr_data_list
        ]

        return pickle.dumps(serializable_data)

    def _deserialize_data(self, serialized_data: bytes) -> list[OCRData]:
        """
        Deserialize cached data back to OCRData list.

        Args:
            serialized_data: Serialized bytes

        Returns:
            List of OCRData objects
        """
        data_list = pickle.loads(serialized_data)

        ocr_data_list = []
        for item in data_list:
            df = pd.DataFrame(item["df"])
            ocr_data = OCRData(df=df, metadata=item["metadata"])
            ocr_data_list.append(ocr_data)

        return ocr_data_list

    def get(
        self, file_content: bytes, provider: str, additional_context: str = ""
    ) -> list[OCRData] | None:
        """
        Get cached OCR result.

        Args:
            file_content: Raw file content bytes
            provider: OCR provider name
            additional_context: Optional additional context for cache key

        Returns:
            List of OCRData if cache hit, None if cache miss
        """
        cache_key = self._compute_cache_key(file_content, provider, additional_context)
        serialized_data = self.cache._get_cached_entry(cache_key)

        if serialized_data is not None:
            logger.info(
                "OCR cache HIT",
                cache_key=cache_key[:16] + "...",
                provider=provider,
            )
            return self._deserialize_data(serialized_data)

        logger.debug(
            "OCR cache MISS",
            cache_key=cache_key[:16] + "...",
            provider=provider,
        )
        return None

    def set(
        self,
        file_content: bytes,
        provider: str,
        ocr_data_list: list[OCRData],
        additional_context: str = "",
    ) -> bool:
        """
        Store OCR result in cache.

        Args:
            file_content: Raw file content bytes
            provider: OCR provider name
            ocr_data_list: List of OCRData to cache
            additional_context: Optional additional context for cache key

        Returns:
            True if successfully cached, False otherwise
        """
        cache_key = self._compute_cache_key(file_content, provider, additional_context)

        # TODO the return value consist of ocrdata instance and a none// need to fix this [OCRData(8 words, 1 pages), None] #pramesh
        # sample page 50 pages pdf.
        ocr_data_list = [value for value in ocr_data_list if value is not None]
        serialized_data = self._serialize_data(ocr_data_list)

        success = self.cache._set_cached_entry(
            cache_key,
            serialized_data,
            provider=provider,
            file_size=len(file_content),
            pages=len(ocr_data_list),
        )

        if success:
            logger.info(
                "OCR result cached",
                cache_key=cache_key[:16] + "...",
                provider=provider,
                pages=len(ocr_data_list),
            )

        return success

    def delete(
        self, file_content: bytes, provider: str, additional_context: str = ""
    ) -> bool:
        """
        Delete specific cache entry.

        Args:
            file_content: Raw file content bytes
            provider: OCR provider name
            additional_context: Optional additional context for cache key
                ttl=self.config.ttl,

        Returns:
            True if deleted, False otherwise
        """
        cache_key = self._compute_cache_key(file_content, provider, additional_context)
        return self.cache.delete(cache_key)
