"""Factory for creating extractor service instances.

This module provides a factory implementation for creating different types
of extractor services with support for caching, custom implementations,
and service registration.
"""

from enum import Enum
from typing import ClassVar

from leapx.common.cache.cache_config import CacheConfig
from leapx.common.observability.logger import logger
from leapx.services.extractor.base_extractor import ExtractorInterface
from leapx.services.extractor.cached_extractor_service import CachedExtractorService
from leapx.services.extractor.exceptions.extractor_exceptions import (
    ExtractorCreationError,
    ExtractorNotRegisteredError,
)
from leapx.services.extractor.extractor_service import ExtractorService


class ExtractorProvider(str, Enum):
    """Enumeration of available extractor types."""

    LITE_LLM = "lite_llm"


class ExtractorFactory:
    """
    Factory for creating extractor service instances.

    Implements the Factory pattern with a registration system,
    allowing new extractor implementations to be registered dynamically
    without modifying existing code (Open/Closed Principle).

    """

    _registry: ClassVar[dict[str, type[ExtractorInterface]]] = {
        ExtractorProvider.LITE_LLM.value: ExtractorService,
    }

    @classmethod
    def create(
        cls,
        provider: str | ExtractorProvider = ExtractorProvider.LITE_LLM,
        cache_config: CacheConfig | None = None,
    ) -> ExtractorInterface:
        """
        Create an extractor service instance.

        Args:
            extractor_type: Type of extractor to create (default: LITE_LLM)
            instructor_client: Optional pre-configured instructor client
            cache_config: Cache configuration (only used for cached
                extractors)

        Returns:
            Instantiated extractor service

        Raises:
            ExtractorNotRegisteredError: If no extractor registered for type
            ExtractorCreationError: If extractor creation fails
        """
        # Convert enum to string if necessary

        if isinstance(provider, ExtractorProvider):
            extractor_type = provider.value

        if extractor_type not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise ExtractorNotRegisteredError(extractor_type, available)

        extractor_class = cls._registry[extractor_type]

        try:
            extractor = extractor_class()
            if cache_config and cache_config.enabled:
                extractor = CachedExtractorService(extractor, cache_config)
        except Exception as e:
            logger.exception(
                "Failed to create extractor service",
                extractor_type=extractor_type,
                error=str(e),
            )
            raise ExtractorCreationError(extractor_type, e) from e
        logger.info(
            "Created extractor service",
            extractor_type=extractor_type,
            extractor_class=extractor_class.__name__,
        )
        return extractor
