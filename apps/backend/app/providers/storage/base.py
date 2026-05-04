"""Storage interface for abstracting storage operations."""

from abc import ABC, abstractmethod

from app.shared.constants.app_constants import (
    DEFAULT_CONTENT_TYPE,
    DOWNLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
    UPLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
)


class StorageInterface(ABC):
    """Abstract interface for storage operations."""

    @abstractmethod
    async def upload(self, content: bytes, filename: str, content_type: str | None = None) -> str:
        """
        Upload file to storage.

        Args:
            content: File content as bytes
            filename: Name of the file
            content_type: MIME type of the file

        Returns:
            URL or path to the uploaded file
        """

    @abstractmethod
    async def generate_presigned_upload_url(
        self,
        file_key: str,
        content_type: str = DEFAULT_CONTENT_TYPE,
        expires_in: int = UPLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
    ) -> dict[str, str]:
        """
        Generate a presigned URL for uploading a file.

        Args:
            filename: Name of the file to upload
            expires_in: Expiration time in seconds (default 1 hour)

        Returns:
            Dictionary containing the presigned URL and fields for upload
        """

    @abstractmethod
    async def delete(self, file_key: str) -> bool:
        """
        Delete file from storage.

        Args:
            filename: Name of the file to delete

        Returns:
            True if deletion was successful, False otherwise
        """

    @abstractmethod
    async def confirm_upload(self, file_key: str) -> bool:
        """
        Confirm that a file has been uploaded by checking if it exists.

        Args:
            file_key: The key/path of the file to check
        Returns:
            True if file exists, False otherwise
        """

    @abstractmethod
    async def generate_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = DOWNLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
    ) -> str:
        """
        Generate a presigned URL for downloading/viewing a file.

        Args:
            file_key: The key/path of the file
            expires_in: Expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL for downloading/viewing the file
        """

    @abstractmethod
    def get_file_path(self, filename: str) -> str:
        """
        Get the full path to a file.

        Args:
            filename: Name of the file

        Returns:
            Full path to the file
        """
