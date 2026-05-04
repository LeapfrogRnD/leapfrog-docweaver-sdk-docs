"""S3 client manager for centralized boto3 client initialization."""

import contextlib
from typing import Any, Self

import boto3
from botocore.client import BaseClient


class S3ClientManager:
    """Singleton manager for S3 client to avoid repeated initialization."""

    _instance: "S3ClientManager | None" = None
    _client: BaseClient | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, **kwargs: Any) -> None:
        """
        Initialize the S3 client with optional configuration.

        Args:
            **kwargs: Optional boto3 client configuration parameters
                     (e.g., region_name, aws_access_key_id, etc.)
        """
        if self._client is None:
            with contextlib.suppress(Exception):
                self._client = boto3.client("s3", **kwargs)

    def get_client(self) -> BaseClient:
        """
        Get the S3 client instance.

        Returns:
            BaseClient: The boto3 S3 client

        Raises:
            RuntimeError: If the client hasn't been initialized
        """
        if self._client is None:
            self.initialize()
        return self._client

    def reset(self) -> None:
        """Reset the client (useful for testing or reconfiguration)."""
        self._client = None


_manager = S3ClientManager()


def initialize_s3_client(**kwargs: Any) -> None:
    """
    Initialize the S3 client at application startup.

    This should be called once at application startup with any desired
    configuration parameters.

    Args:
        **kwargs: Optional boto3 client configuration parameters
                 (e.g., region_name, aws_access_key_id, etc.)

    Example:
        >>> # At application startup
        >>> initialize_s3_client(region_name='us-west-2')
    """
    _manager.initialize(**kwargs)


def get_s3_client() -> BaseClient:
    """
    Get the initialized S3 client.

    Returns:
        BaseClient: The boto3 S3 client

    Example:
        >>> client = get_s3_client()
        >>> response = client.get_object(Bucket='my-bucket', Key='my-key')
    """
    return _manager.get_client()
