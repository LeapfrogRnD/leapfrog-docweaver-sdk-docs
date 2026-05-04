from leapx.common.cache.cache_config import CacheConfig
from leapx.common.observability.logger import logger
from leapx.common.types.providers import OCRProviderType
from leapx.services.credentials.base import Credential
from leapx.services.ocr.base.cached_ocr_engine import CachedOCREngine
from leapx.services.ocr.base.ocr_engine import OCREngine
from leapx.services.ocr.exceptions import (
    InvalidOCREngineError,
    OCREngineInitializationError,
    UnknownOCREngineError,
)

_OCR_ENGINE_REGISTRY: dict[OCRProviderType, type[OCREngine]] = {}


def register_ocr_engine(provider_type: OCRProviderType):
    """
    Decorator to register OCR engines automatically.

    Args:
        provider_type: OCR provider enum value to register the engine under.

    Usage:
        @register_ocr_engine(OCRProviderType.AZURE)
        class AzureOCREngine(OCREngine):
            ...
    """

    def decorator(engine_class: type[OCREngine]) -> type[OCREngine]:
        if not issubclass(engine_class, OCREngine):
            raise InvalidOCREngineError(engine_class)

        if provider_type in _OCR_ENGINE_REGISTRY:
            logger.warning(
                "OCR engine provider type already registered, overriding",
                provider=provider_type.value,
                existing_engine=_OCR_ENGINE_REGISTRY[provider_type].__name__,
                new_engine=engine_class.__name__,
            )

        _OCR_ENGINE_REGISTRY[provider_type] = engine_class
        logger.info(
            "OCR engine registered via decorator",
            provider=provider_type.value,
            engine_class=engine_class.__name__,
        )
        return engine_class

    return decorator


class OCREngineFactory:
    """Factory for creating OCR engines.

    Provides creation with optional caching and registry introspection.
    """

    @classmethod
    def create_engine(
        cls,
        provider: OCRProviderType,
        credential: Credential,
        cache_config: CacheConfig | None = None,
    ) -> OCREngine:
        """
        Create and initialize an OCR engine with optional caching.

        Args:
            provider: OCR provider type.
            credential: Provider credentials.
            cache_config: Optional cache configuration.

        Returns:
            Initialized OCR engine (possibly wrapped with caching).

        Raises:
            UnknownOCREngineError: If no engine is registered for the provider.
            OCREngineInitializationError: If the engine fails to initialize.
        """
        engine_class = _OCR_ENGINE_REGISTRY.get(provider)
        if engine_class is None:
            raise UnknownOCREngineError(provider)

        engine = engine_class()
        success = engine.initialize(credential)
        if not success:
            raise OCREngineInitializationError(provider, engine_class)

        logger.info(
            "OCR engine created successfully",
            provider=provider.value,
            engine_class=engine_class.__name__,
            cache_enabled=cache_config.enabled,
        )

        # Wrap with caching if enabled
        if cache_config.enabled:
            engine = CachedOCREngine(engine, cache_config)

        return engine

    @classmethod
    def list_available_engines(cls) -> list[OCRProviderType]:
        """Return all registered OCR providers."""
        engines = list(_OCR_ENGINE_REGISTRY.keys())
        logger.debug(
            "Available OCR engines requested",
            engines=[e.value for e in engines],
        )
        return engines
