"""Storage factory for initializing storage providers based on configuration."""

from typing import Literal

from app.config.settings import Settings
from app.logger import logger
from app.providers.storage.base import StorageInterface
from app.providers.storage.local_storage import LocalStorage
from app.providers.storage.s3_storage import S3Storage


class StorageProviderFactory:
    """Factory class for creating storage instances based on configuration."""

    @classmethod
    def create(
        cls,
        settings: Settings,
        storage_type: Literal["local", "s3"] | None = None,
        prefix: str = "uploads",
    ) -> StorageInterface:
        """
        Create a storage instance based on configuration.
        """
        storage_mode = storage_type or settings.storage_mode

        logger.info(f"Initializing storage with mode: {storage_mode}")

        try:
            if storage_mode == "s3":
                return StorageProviderFactory._create_s3_storage(settings, prefix)
            if storage_mode == "local":
                return StorageProviderFactory._create_local_storage(settings)
            return StorageProviderFactory._raise_unsupported_storage_error(storage_mode)

        except Exception as e:
            logger.error(
                f"Failed to initialize {storage_mode} storage",
                error=str(e),
                storage_mode=storage_mode,
            )
            raise

    @classmethod
    def _raise_unsupported_storage_error(cls, storage_mode: str) -> None:
        """Raise an error for unsupported storage types."""
        raise ValueError(
            f"Unsupported storage type: {storage_mode}. Supported types are: 'local', 's3'"
        )

    @classmethod
    def _create_s3_storage(cls, settings: Settings, prefix: str | None) -> S3Storage:
        """
        Create S3 storage instance.
        """
        if not settings.aws_s3_bucket_name:
            raise ValueError("AWS S3 bucket name is required for S3 storage")

        if not settings.aws_region:
            raise ValueError("AWS region is required for S3 storage")

        logger.info(
            f"Creating S3 storage with bucket: {settings.aws_s3_bucket_name}, "
            f"region: {settings.aws_region}, prefix: {prefix}"
        )

        return S3Storage(
            settings=settings,
            prefix=prefix,
        )

    @classmethod
    def _create_local_storage(cls, settings: Settings) -> LocalStorage:
        """
        Create local storage instance.
        """
        if not settings.local_storage_path:
            raise ValueError("Local storage path is required for local storage")

        logger.info(f"Creating local storage with path: {settings.local_storage_path}")

        return LocalStorage(storage_path=settings.local_storage_path)
