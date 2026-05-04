"""Pipeline error handling."""

from litellm import AuthenticationError, NotFoundError

from leapx.common.observability.logger import logger
from leapx.services.credentials.exceptions import (
    InvalidCredentialsError,
    ProviderMismatchError,
)
from leapx.services.extractor.exceptions.extractor_exceptions import (
    InvalidLLMModelError,
)


class PipelineErrorHandler:
    """Handles pipeline initialization errors."""

    @staticmethod
    def handle_initialization_error(exc: Exception) -> None:
        """Handle various initialization errors with appropriate logging."""
        error_handlers = {
            InvalidCredentialsError: lambda e: logger.error(
                "Credential validation failed",
                error=e.__class__.__name__,
                details=e.details or {},
            ),
            ProviderMismatchError: lambda e: logger.error(
                "Provider mismatch",
                error=str(e),
                error_type=type(e).__name__,
            ),
            InvalidLLMModelError: lambda e: logger.error(
                "Invalid LLM Model",
                error=e.__class__.__name__,
                details=e.details or {},
            ),
            ValueError: lambda e: logger.error(
                "Invalid pipeline configuration",
                error=str(e),
                error_type=type(e).__name__,
            ),
            AuthenticationError: lambda e: logger.error(
                "LLM Authentication Error",
                error=str(e),
                error_type=type(e).__name__,
            ),
            NotFoundError: lambda e: logger.error(
                "LLM Model Not Found Error",
                error=str(e),
                error_type=type(e).__name__,
            ),
        }

        handler = error_handlers.get(type(exc))
        if handler:
            handler(exc)
        else:
            logger.error(
                "Unexpected error during pipeline initialization",
                error=str(exc),
                error_type=type(exc).__name__,
            )
