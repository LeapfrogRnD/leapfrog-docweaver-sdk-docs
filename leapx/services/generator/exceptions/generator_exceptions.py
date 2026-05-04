"""Generator parser specific exceptions.

All exceptions inherit from LeapXError (defined in leapx.common.exceptions).
Exception names are specific to generator domain to avoid conflicts.
"""

from collections.abc import Mapping

from leapx.common.exceptions import LeapXError


class GeneratorError(LeapXError):
    """
    Base exception for all generator errors.

    All generator exceptions inherit from this class.
    This allows catching all generator specific errors with a single except clause.
    """

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        super().__init__(message, details)


class GeneratorValidationError(GeneratorError):
    """
    Raised when input request validation fails.

    This category includes errors related to input request validation,
    missing system prompt, user prompt, and response schemas.
    """

    pass


class GeneratorCreationError(GeneratorError):
    """
    Raised when generator creation fails.

    This includes errors during instantiation of generator services,
    such as misconfiguration or initialization failures.
    """

    pass


class MissingInputForGenerationError(GeneratorError):
    """
    Raised when no valid text input is found for generation.

    This occurs when neither direct text input nor combined text from previous stages is available.
    """

    def __init__(
        self,
        message: str = "No valid text input found for generation.",
        details: Mapping[str, any] | None = None,
    ) -> None:
        super().__init__(message, details)


class InvalidLLMModelError(GeneratorError):
    """
    Raised when invalid llm model is passed
    """

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            message = details.get("error", "")

        super().__init__(message, details)
