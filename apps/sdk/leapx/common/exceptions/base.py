"""Base exception classes for LeapX."""

from collections.abc import Mapping


class LeapXError(Exception):
    """
    Base exception for all LeapX errors.

    All custom exceptions in LeapX services should inherit from this class.
    This allows for easy catching of all LeapX-specific errors.

    Example:
        >>> try:
        ...     # Some LeapX operation
        ...     pass
        ... except LeapXError as e:
        ...     # Handle any LeapX error
        ...     logger.error("LeapX error occurred: %s", e)
    """

    def __init__(
        self, message: str, details: Mapping[str, any] | None = None, *args, **kwargs
    ):
        """
        Initialize LeapX error.

        Args:
            message: Error message describing what went wrong
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.message = message
        self.details = details or {}
        super().__init__(message, details, *args, **kwargs)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"


class S3ReadError(LeapXError):
    """Error raised when reading a file from S3 fails."""

    def __init__(self, s3_uri: str) -> None:
        super().__init__(f"Error reading from S3 ({s3_uri})")


class InvalidS3UriError(LeapXError):
    """Error raised when an invalid S3 URI is used."""

    def __init__(self, s3_uri: str) -> None:
        super().__init__(
            f"Invalid S3 URI format: {s3_uri}. Expected format: s3://bucket/key"
        )
