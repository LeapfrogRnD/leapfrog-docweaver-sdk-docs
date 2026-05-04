from collections.abc import Mapping

from leapx.common.exceptions import LeapXError


class InvalidChunkingError(LeapXError):
    """Raised invalid chunking method is passed."""

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            chunking_method = details.get("chunking_method") or details.get(
                "chunking_strategy", "Unknown"
            )
            message = f"Invalid chunking method {chunking_method}"
        super().__init__(message, details)


class InvalidChunkingClassError(LeapXError):
    """Raised for invalid chunking class"""

    def __init__(self, message=None, details=None, *args, **kwargs):
        if not message and details:
            message = "Invalid Chunking class"
        super().__init__(message, details, *args, **kwargs)
