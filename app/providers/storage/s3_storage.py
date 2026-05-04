"""AWS S3 storage provider."""

from botocore.exceptions import ClientError, NoCredentialsError

from app.config.settings import Settings
from app.logger import logger
from app.providers.clients.aws_boto import get_boto_client
from app.providers.storage.base import StorageInterface
from app.providers.storage.exceptions import (
    StorageDeleteError,
    StorageNotFoundError,
    StorageUploadError,
)
from app.shared.constants.app_constants import (
    DEFAULT_CONTENT_TYPE,
    DOWNLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
    UPLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
)


class S3Storage(StorageInterface):
    """AWS S3 storage implementation."""

    def __init__(
        self,
        settings: Settings,
        prefix: str = "uploads",
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
            prefix: Key prefix for uploaded files
        """
        self.settings = settings
        self.bucket_name = settings.aws_s3_bucket_name
        self.region = settings.aws_region
        self.prefix = prefix

        try:
            self.s3_client = get_boto_client("s3", region_name=self.region)
        except NoCredentialsError as e:
            logger.error("AWS credentials not configured", error=str(e))
            raise

    def _get_s3_key(self, filepath: str) -> str:
        """
        Get full S3 key for a filename.

        Args:
            filename: Name of the file
            task_id: Optional task ID to organize files in folders

        Returns:
            S3 key in format: prefix/task_id/filename or prefix/filename
        """
        return f"{self.prefix}/{filepath}"

    async def generate_presigned_upload_url(
        self,
        file_key: str,
        content_type: str = DEFAULT_CONTENT_TYPE,
        expires_in: int = UPLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
    ) -> dict[str, str]:
        """
        Generate a presigned URL for uploading a file to S3.
        """
        try:
            presigned_post = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": file_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return {
                "url": presigned_post,
                "file_key": file_key,
            }
        except ClientError as e:
            raise StorageUploadError(detail=str(e)) from e

    async def confirm_upload(self, file_key: str) -> bool:
        """
        Confirm that a file has been uploaded to S3 by checking if it exists.

        Args:
            file_key: The S3 key of the file to check
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.warning("File not found in S3", file_key=file_key)
                raise StorageNotFoundError() from e
            logger.error("Error confirming file upload to S3", error=str(e), file_key=file_key)
            raise StorageUploadError(detail=str(e)) from e

    async def generate_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = DOWNLOAD_PRESIGNED_URL_EXPIRATION_SECONDS,
    ) -> str:
        """
        Generate a presigned URL for downloading/viewing a file from S3.

        Args:
            file_key: The S3 key of the file
            expires_in: Expiration time in seconds (default 1 hour)

        Returns:
            Presigned URL for downloading/viewing the file
        """
        try:
            return self.s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": file_key,
                },
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error("Error generating presigned download URL", error=str(e), file_key=file_key)
            raise StorageUploadError(detail=str(e)) from e

    async def upload(self, content: bytes, filename: str, content_type: str | None = None) -> str:
        """
        Upload file to S3.

        Args:
            content: File content as bytes
            filename: Name of the file
            content_type: MIME type of the file

        Returns:
            S3 URL to access the file

        Raises:
            StorageUploadError: If upload fails
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=content,
                ContentType=content_type or "application/octet-stream",
            )

            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
            logger.info(f"File uploaded to S3: {url}")
            return url

        except ClientError as e:
            logger.error("S3 upload failed", error=str(e), filename=filename)
            raise StorageUploadError(detail=str(e)) from e

    async def delete(self, file_key: str) -> bool:
        """
        Delete file from S3.

        Args:
            filename: Name of the file to delete

        Returns:
            True if deletion was successful

        Raises:
            StorageDeleteError: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key,
            )

            logger.info(f"File deleted from S3: {file_key}")
            return True

        except ClientError as e:
            logger.error("S3 deletion failed", error=str(e), filename=file_key)
            raise StorageDeleteError(detail=str(e)) from e

    def get_file_path(self, filename: str) -> str:
        """
        Get S3 URI for a file.

        Args:
            filename: Name of the file

        Returns:
            S3 URI (s3://bucket/key)
        """
        s3_key = self._get_s3_key(filename)
        return f"s3://{self.bucket_name}/{s3_key}"
