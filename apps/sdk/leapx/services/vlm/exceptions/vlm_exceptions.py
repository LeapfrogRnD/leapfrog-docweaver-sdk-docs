"""VLM parser specific exceptions.

All exceptions inherit from LeapXError (defined in leapx.common.exceptions).
Exception names are specific to VLM Parser domain to avoid conflicts.
"""

from collections.abc import Mapping
from typing import Any

from leapx.common.exceptions import LeapXError


class VLMError(LeapXError):
    """
    Base exception for all VLM errors.

    All VLMs exceptions inherit from this class.
    This allows catching all VLMs specific errors with a single except clause.
    """

    def __init__(
        self, message: str = "", details: Mapping[str, Any] | None = None
    ) -> None:
        super().__init__(message, details)


class VLMValidationError(VLMError):
    """
    Raised when input request validation fails.

    This category includes errors related to input request validation,
    missing system prompt, user prompt, and response schemas.
    """

    pass


class InvalidVLMModelError(VLMError):
    """
    Raised when invalid vlm model is passed
    """

    def __init__(
        self, message: str = "", details: Mapping[str, Any] | None = None
    ) -> None:
        if not message and details:
            message = details.get("error", "")

        super().__init__(message, details)
