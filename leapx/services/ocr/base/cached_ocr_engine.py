"""Cached OCR engine wrapper for transparent caching."""

import contextlib

from leapx.common.cache import CacheConfig, CacheFacadeInterface
from leapx.common.observability.logger import logger
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.base.ocr_engine import OCREngine
from leapx.services.ocr.common.ocr_cache import OCRCacheFacade


class CachedOCREngine(OCREngine):
    """
    Wrapper around OCR engines to add transparent disk caching.

    This wrapper intercepts extract_text calls and checks the cache first.
    If cache miss, delegates to the underlying engine and caches the result.

    Can be used as a context manager for automatic cleanup:
        with CachedOCREngine(engine, cache_config) as cached_engine:
            result = await cached_engine.extract_text(data)
    """

    def __init__(
        self,
        engine: OCREngine,
        cache_config: CacheConfig,
        cache_facade: CacheFacadeInterface | None = None,
    ):
        """
        Initialize cached OCR engine.

        Args:
            engine: The underlying OCR engine to wrap
            cache_config: Cache configuration (uses default if None)
        """
        super().__init__()
        self.engine = engine
        self.cache_service = cache_facade or OCRCacheFacade(cache_config)
        self.is_configured = engine.is_configured

        logger.info(
            "Cached OCR engine initialized",
            underlying_engine=engine.__class__.__name__,
        )

    def initialize(self, **kwargs) -> bool:
        """
        Initialize the underlying engine.

        Args:
            **kwargs: Arguments to pass to the underlying engine

        Returns:
            True if initialization successful
        """
        success = self.engine.initialize(**kwargs)
        self.is_configured = success
        return success

    async def extract_text(self, input_data: str | bytes) -> list[OCRData]:
        """
        Extract text with caching.

        First checks cache for existing result. On cache miss,
        delegates to underlying engine and caches the result.

        Args:
            input_data: File path or raw bytes

        Returns:
            List of OCRData objects (one per page)
        """
        # Ensure we have bytes
        if isinstance(input_data, str):
            with open(input_data, "rb") as f:  # noqa: PTH123
                file_content = f.read()
        else:
            file_content = input_data

        # Get provider name for cache key
        provider_name = self._get_provider_name()

        # Try to get from cache
        cached_result = self.cache_service.get(file_content, provider_name)

        if cached_result is not None:
            logger.info(
                "Using cached OCR result",
                provider=provider_name,
                pages=len(cached_result),
            )
            return cached_result

        # Cache miss - call underlying engine
        logger.debug(
            "Cache miss - calling underlying OCR engine",
            provider=provider_name,
        )

        ocr_result = await self.engine.extract_text(input_data)

        # Cache the result
        self.cache_service.set(file_content, provider_name, ocr_result)

        return ocr_result

    def _get_provider_name(self) -> str:
        """
        Get provider name from the underlying engine.

        Returns:
            Provider name string
        """
        engine_class = self.engine.__class__.__name__.lower()

        if "azure" in engine_class:
            return "azure"
        if "aws" in engine_class or "textract" in engine_class:
            return "aws"
        return engine_class

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return self.cache_service.cache.get_stats()

    def clear_cache(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful
        """
        return self.cache_service.cache.clear()

    def close(self):
        """Close the cache."""
        self.cache_service.cache.close()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and ensure cleanup."""
        self.close()
        return False

    def __del__(self):
        """Cleanup on deletion."""
        with contextlib.suppress(Exception):
            self.close()
