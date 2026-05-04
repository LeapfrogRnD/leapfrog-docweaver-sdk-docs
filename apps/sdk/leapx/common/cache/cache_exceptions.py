from collections.abc import Mapping

from leapx.common.exceptions import LeapXError


class InvalidCacheProviderError(LeapXError):
    """Raised when a class registered as Cache provider is invalid."""

    def __init__(self, cache_class: type):
        self.engine_class = cache_class
        super().__init__(f"{cache_class.__name__} is not a valid LeapXCache subclass.")


class UnsupportedCacheTypeError(LeapXError):
    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            cache_provider = details.get("cache_provider", "")
            if cache_provider:
                message = f"Unsupported cache type: {cache_provider}. "
        super().__init__(message, details)


class CacheProviderNotFoundError(LeapXError):
    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            cache_provider = details.get("cache_provider", "")
            if cache_provider:
                message = (
                    f"No cache implementation registered for type: {cache_provider}"
                )
        super().__init__(message, details)
