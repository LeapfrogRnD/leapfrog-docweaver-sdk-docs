"""Cached extractor service wrapper for transparent caching."""

import contextlib

from leapx.common.cache import CacheConfig, CacheFacadeInterface
from leapx.common.observability.logger import logger
from leapx.pipeline.stages.constants import METADATA
from leapx.services.extractor.base_extractor import ExtractorInterface
from leapx.services.extractor.extractor_cache import ExtractorCacheFacade
from leapx.services.extractor.schemas import ExtractionRequest, ExtractionResponse


class CachedExtractorService(ExtractorInterface):
    """
    Wrapper around ExtractorService to add transparent disk caching.

    This wrapper intercepts extract calls and checks the cache first.
    If cache miss, delegates to the underlying service and caches the result.

    Can be used as a context manager for automatic cleanup:
        with CachedExtractorService(service, cache_config) as cached_service:
            result = await cached_service.extract(request)
    """

    def __init__(
        self,
        service: ExtractorInterface,
        cache_config: CacheConfig,
        cache_facade: CacheFacadeInterface | None = None,
    ):
        """
        Initialize cached extractor service.

        Args:
            service: The underlying ExtractorService to wrap
            cache_config: Cache configuration (uses default if None)
        """
        self.service = service
        self.cache_service = cache_facade or ExtractorCacheFacade(cache_config)

        logger.info(
            "Cached extractor service initialized",
            underlying_service=service.__class__.__name__,
        )

    async def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        """
        Extract structured data with caching.

        First checks cache for existing result. On cache miss,
        delegates to underlying service and caches the result.

        Args:
            request: ExtractionRequest containing system prompt, user prompt,
                    and response model

        Returns:
            ExtractionResponse with extracted data or error information
        """
        # Try to get from cache
        cached_data = self.cache_service.get(request)

        if cached_data is not None:
            # Reconstruct the response from cached data
            logger.info(
                "Using cached extraction result",
                model=request.config.model,
            )

            # Reconstruct the data using the response_model from the request
            if cached_data["data_dict"]:
                reconstructed_data = request.response_model(**cached_data["data_dict"])

                return ExtractionResponse(
                    data=reconstructed_data,
                    metadata=cached_data.get(METADATA, {}),
                )

        # Cache miss - call underlying service
        logger.debug(
            "Cache miss - calling underlying extractor service",
            model=request.config.model,
        )

        extraction_result = await self.service.extract(request)
        # Cache the result
        self.cache_service.set(request, extraction_result)

        return extraction_result

    def validate_request(self, request: ExtractionRequest) -> tuple[bool, str | None]:
        """
        Validate the extraction request before processing.

        Delegates to the underlying service's validation.

        Args:
            request: ExtractionRequest to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
        """
        return self.service.validate_request(request)

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


def create_cached_extractor_service(
    service: ExtractorInterface, cache_config: CacheConfig | None = None
) -> CachedExtractorService:
    """
    Factory function to create a CachedExtractorService instance.

    Args:
        service: The underlying ExtractorService to wrap
        cache_config: Cache configuration (uses default if None)

    Returns:
        CachedExtractorService instance
    """
    return CachedExtractorService(service, cache_config)
