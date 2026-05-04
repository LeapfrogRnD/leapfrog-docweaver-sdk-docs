"""Cache factory for creating cache instances."""

from typing import ClassVar

from leapx.common.cache.base import LeapXCache
from leapx.common.cache.cache_config import CacheConfig, CacheProviderType
from leapx.common.cache.cache_exceptions import (
    CacheProviderNotFoundError,
    InvalidCacheProviderError,
    UnsupportedCacheTypeError,
)
from leapx.common.observability.logger import logger


def register_cache_provider(provider_type: CacheProviderType):
    """
    Decorator to register cache provider automatically.

    Usage:
    @register_ocr_engine(CacheProvider.SQLITE)
        class FileCache(LeapXCache):
            ...
    """

    def decorator(cache_class: type[LeapXCache]) -> type[LeapXCache]:
        registry = CacheFactory()._cache_registry
        if not issubclass(cache_class, LeapXCache):
            raise InvalidCacheProviderError(cache_class)

        if provider_type in registry:
            logger.warning(
                "Cache provider type already registered, overriding",
                provider=provider_type.value,
                existing_engine=registry[provider_type].__name__,
                new_engine=cache_class.__name__,
            )

        registry[provider_type] = cache_class
        logger.info(
            "OCR engine registered via decorator",
            provider=provider_type.value,
            cache_class=cache_class.__name__,
        )
        return cache_class

    return decorator


class CacheFactory:
    """
    Factory for creating cache instances.

    Implements the factory pattern to create different types of cache
    implementations (SQLite, File-based, etc.) based on configuration.
    """

    _cache_registry: ClassVar[dict[CacheProviderType, type[LeapXCache]]] = {}

    @classmethod
    def create_cache(
        cls,
        config: CacheConfig,
        **kwargs,
    ) -> LeapXCache:
        """
        Create a cache instance based on the specified type.

        Args:
            cache_type: The type of cache to create (sqlite, file, etc.)
            config: Cache configuration
            **kwargs: Additional arguments specific to the cache type

        Returns:
            Cache instance of the specified type

        Raises:
            ValueError: If cache_type is not supported
        """
        # Convert string to CacheType enum if necessary
        if isinstance(config.provider, str):
            try:
                cache_provider = CacheProviderType(config.provider.lower())
            except ValueError as err:
                raise UnsupportedCacheTypeError(
                    details={
                        "cache_provider": config.provider,
                        "supported_types": ", ".join(
                            t.value for t in CacheProviderType
                        ),
                    },
                ) from err
        else:
            cache_provider = config.provider

        # Get the cache class from registry
        cache_class = cls._cache_registry.get(cache_provider)
        if cache_class is None:
            raise CacheProviderNotFoundError(
                details={"cache_provider": cache_provider.value},
            )

        # Create and return cache instance
        logger.info(
            f"Creating {cache_provider.value} cache", cache_class=cache_class.__name__
        )
        cache_service = cache_class(config=config, **kwargs)
        return cache_service.init_cache()

    @classmethod
    def get_available_cache_providers(cls) -> list[str]:
        """
        Get list of available cache types.

        Returns:
            List of cache type names
        """
        return [cache_provider.value for cache_provider in cls._cache_registry]
