"""Disk cache implementation for extraction results using SQLite."""

import json
from datetime import datetime

from leapx.common.cache import (
    CacheConfig,
    CacheFacadeInterface,
    CacheFactory,
    CacheUtils,
)
from leapx.common.observability.logger import logger
from leapx.services.extractor.schemas import ExtractionRequest, ExtractionResponse


class ExtractorCacheFacade(CacheFacadeInterface[ExtractionRequest, dict]):
    """
    Disk-based cache for LLM extraction results using SQLite.

    Uses SQLite for persistent, thread-safe caching with
    automatic eviction and TTL management.
    """

    def __init__(self, config: CacheConfig | None = None):
        """
        Initialize extraction disk cache.

        Args:
            config: Cache configuration (uses default if None)
        """
        self.cache = CacheFactory.create_cache(config, cache_name="extraction_cache")

    def _compute_cache_key(
        self, request: ExtractionRequest, additional_context: str = ""
    ) -> str:
        """Compute cache key for extraction request."""
        hash_input = {
            "system_prompt": request.system_prompt.content,
            "user_prompt_content": request.user_prompt.content,
            "user_prompt_context": request.user_prompt.context or "",
            "model": request.config.model,
            "temperature": request.config.temperature,
            "max_tokens": request.config.max_tokens,
            "response_model_schema": request.response_model.model_json_schema(),
        }
        return CacheUtils.compute_cache_key(
            "extraction", hash_input, additional_context
        )

    def _serialize_data(self, response: ExtractionResponse) -> str:
        """
        Serialize ExtractionResponse for storage as JSON text.

        Args:
            response: ExtractionResponse object

        Returns:
            JSON string
        """
        serializable_data = {
            "data_dict": (
                response.data.model_dump(mode="json") if response.data else {}
            ),
            "data_model_name": response.data.__class__.__name__
            if response.data
            else None,
            "metadata": response.metadata,
        }

        return json.dumps(serializable_data, sort_keys=True)

    @staticmethod
    def _json_serializer(obj):
        """Custom JSON serializer for objects not serializable by default."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"{type(obj).__name__} is not JSON serializable")  # noqa: TRY003

    def _deserialize_data(self, serialized_data: str) -> dict:
        """
        Deserialize cached JSON data back to dictionary format.

        Note: Returns a dict since we don't store the response_model class.
        The CachedExtractorService will reconstruct the proper response.

        Args:
            serialized_data: JSON string

        Returns:
            Dictionary with cached data
        """
        return json.loads(serialized_data)

    def get(
        self, request: ExtractionRequest, additional_context: str = ""
    ) -> dict | None:
        """
        Get cached extraction result.

        Args:
            request: ExtractionRequest to look up
            additional_context: Optional additional context for cache key

        Returns:
            Dictionary with cached data if cache hit, None if cache miss
        """
        cache_key = self._compute_cache_key(request, additional_context)
        serialized_data = self.cache._get_cached_entry(cache_key)

        if serialized_data is not None:
            logger.info(
                "Extraction cache HIT",
                cache_key=cache_key[:16] + "...",
                model=request.config.model,
            )
            return self._deserialize_data(serialized_data)

        logger.debug(
            "Extraction cache MISS",
            cache_key=cache_key[:16] + "...",
            model=request.config.model,
        )
        return None

    def set(
        self,
        request: ExtractionRequest,
        response: ExtractionResponse,
        additional_context: str = "",
    ) -> bool:
        """
        Store extraction result in cache.

        Args:
            request: ExtractionRequest that generated the response
            response: ExtractionResponse to cache
            additional_context: Optional additional context for cache key

        Returns:
            True if successfully cached, False otherwise
        """
        cache_key = self._compute_cache_key(request, additional_context)
        serialized_data = self._serialize_data(response)

        # Calculate request size (approximate)
        request_size = (
            len(request.system_prompt.content)
            + len(request.user_prompt.content)
            + len(request.user_prompt.context or "")
        )

        success = self.cache._set_cached_entry(
            cache_key,
            serialized_data,
            model=request.config.model,
            request_size=request_size,
            response_size=len(serialized_data),
        )

        if success:
            logger.info(
                "Extraction result cached",
                cache_key=cache_key[:16] + "...",
                model=request.config.model,
            )

        return success

    def delete(self, request: ExtractionRequest, additional_context: str = "") -> bool:
        """
        Delete specific cache entry.

        Args:
            request: ExtractionRequest to delete from cache
            additional_context: Optional additional context for cache key

        Returns:
            True if deleted, False otherwise
        """
        cache_key = self._compute_cache_key(request, additional_context)
        return self.cache.delete(cache_key)
