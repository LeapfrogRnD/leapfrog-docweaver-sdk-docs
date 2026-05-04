"""extractor parser specific exceptions.

All exceptions inherit from LeapXError (defined in leapx.common.exceptions).
Exception names are specific to extractor domain to avoid conflicts.
"""

from collections.abc import Mapping

from leapx.common.exceptions import LeapXError


class ExtractorError(LeapXError):
    """
    Base exception for all extractor errors.

    All extractor exceptions inherit from this class.
    This allows catching all extractor specific errors with a single except clause.
    """

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        super().__init__(message, details)


class ExtractorValidationError(ExtractorError):
    """
    Raised when input request validation fails.

    This category includes errors related to input request validation,
    missing system prompt, user prompt, and response schemas.
    """

    pass


class ExtractorNotRegisteredError(ExtractorError):
    """Raised when attempting to use an unregistered extractor type."""

    def __init__(self, extractor_type: str, available: str | None = None) -> None:
        """
        Initialize ExtractorNotRegisteredError.

        Args:
            extractor_type: The extractor type that was not found
            available: Optional string of available types
        """
        if available:
            message = (
                f"No extractor registered for '{extractor_type}'. "
                f"Available: {available}"
            )
        else:
            message = f"No extractor registered for '{extractor_type}'"
        super().__init__(message)


class ExtractorCreationError(ExtractorError):
    """Raised when extractor creation fails."""

    def __init__(self, extractor_type: str, error: Exception) -> None:
        """
        Initialize ExtractorCreationError.

        Args:
            extractor_type: The extractor type that failed to create
            error: The underlying exception
        """
        message = f"Failed to create extractor '{extractor_type}': {error}"
        super().__init__(message)


class InvalidLLMModelError(ExtractorError):
    """
    Raised when invalid llm model is passed
    """

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            message = details.get("error", "")

        super().__init__(message, details)
