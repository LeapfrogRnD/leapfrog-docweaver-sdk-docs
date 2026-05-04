"""Local file storage provider."""

from pathlib import Path

from app.logger import logger
from app.providers.storage.base import StorageInterface
from app.providers.storage.exceptions import StorageDeleteError, StorageUploadError


class LocalStorage(StorageInterface):
    """Local filesystem storage implementation."""

    def __init__(self, storage_path: str | None = None):
        """
        Initialize local storage.

        Args:
            storage_path: Base path for file storage
        """
        self.storage_path = Path(storage_path)

    def _ensure_directory(self) -> None:
        """Ensure storage directory exists."""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def generate_presigned_upload_url(
        self,
        file_key: str,
        content_type: str,
        expires_in: int = 3600,  # noqa: ARG002
    ) -> dict[str, str]:
        """
        Generate a presigned URL for uploading a file (not applicable for local storage).

        For local storage, this returns a placeholder response since presigned URLs
        are primarily used for cloud storage like S3.

        Args:
            file_key: Name of the file to upload
            content_type: MIME type of the file
            expires_in: Expiration time in seconds (unused for local storage)
            task_id: Optional task ID for folder organization (unused for local storage)

        Returns:
            Dictionary indicating local storage doesn't support presigned URLs
        """
        logger.warning("Presigned URLs are not supported for local storage")
        return {
            "url": "tasks/upload/" + file_key,
            "method": "PUT",
            "message": "Local storage does not support presigned URLs. Use direct upload instead.",
            "filename": file_key,
        }

    async def upload(
        self,
        content: bytes,
        filename: str,
        content_type: str | None = None,  # noqa: ARG002
    ) -> str:
        """
        Upload file to local storage.

        Args:
            content: File content as bytes
            filename: Name of the file
            content_type: MIME type (unused for local storage)

        Returns:
            URL path to access the file

        Raises:
            StorageUploadError: If upload fails
        """
        try:
            self._ensure_directory()
            file_path = self.storage_path / filename

            logger.info(f"Uploading file to local storage: {file_path}")

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)

            if not file_path.exists():
                raise StorageUploadError(detail=f"File was not created at {file_path}")  # noqa: TRY301

            logger.info(f"File successfully uploaded to {file_path}")
            return f"/api/files/{filename}"

        except StorageUploadError:
            raise
        except Exception as e:
            logger.error("Local file upload failed", error=str(e), filename=filename)
            raise StorageUploadError(detail=str(e)) from e

    async def delete(self, file_key: str) -> bool:
        """
        Delete file from local storage.

        Args:
            filename: Name of the file to delete

        Returns:
            True if deletion was successful

        Raises:
            StorageDeleteError: If deletion fails
        """
        try:
            file_path = self.storage_path / file_key

            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True

            logger.warning(f"File not found for deletion: {file_path}")
            return False

        except Exception as e:
            logger.error("Local file deletion failed", error=str(e), filename=file_key)
            raise StorageDeleteError(detail=str(e)) from e

    async def exists(self, file_key: str) -> bool:
        """
        Check if a file exists in local storage.

        Args:
            file_key: The path of the file to check

        Returns:
            True if file exists, False otherwise
        """
        file_path = self.storage_path / file_key
        return file_path.exists()

    async def confirm_upload(self, file_key: str) -> bool:
        """
        Confirm that a file has been uploaded by checking if it exists.

        Args:
            file_key: The path of the file to check
        Returns:
            True if file exists, False otherwise
        """
        return await self.exists(file_key)

    async def generate_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = 3600,  # noqa: ARG002
    ) -> str:
        """
        Generate a presigned URL for downloading/viewing a file (not applicable for local storage).

        For local storage, this returns a local file path or API endpoint.

        Args:
            file_key: The path of the file
            expires_in: Expiration time in seconds (unused for local storage)

        Returns:
            Local URL path to access the file
        """
        logger.warning("Presigned URLs are not supported for local storage, returning local path")
        return f"/api/files/{file_key}"

    def get_file_path(self, filename: str) -> str:
        """
        Get full path to a file.

        Args:
            filename: Name of the file

        Returns:
            Full filesystem path to the file
        """
        return str(self.storage_path / filename)
