"""AWS Secrets Manager provider."""

import json

from botocore.exceptions import ClientError

from app.logger import logger
from app.providers.clients.aws_boto import get_boto_client


class SecretsManager:
    """AWS Secrets Manager utility to fetch and cache secrets."""

    def __init__(self, secret_name: str, region_name: str):
        """
        Initialize Secrets Manager client.

        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            region_name: AWS region where the secret is stored
        """
        self.secret_name = secret_name
        self.region_name = region_name
        self._secrets_cache: dict[str, str] | None = None

        self.client = get_boto_client(service_name="secretsmanager", region_name=self.region_name)

    def get_secrets(self, force_refresh: bool = False) -> dict[str, str]:
        """
        Fetch secrets from AWS Secrets Manager.

        Args:
            force_refresh: If True, bypass cache and fetch fresh secrets

        Returns:
            Dictionary containing all secrets

        Raises:
            ClientError: If unable to fetch secrets from AWS
        """
        if self._secrets_cache is not None and not force_refresh:
            return self._secrets_cache

        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)

            if "SecretString" in response:
                secret_dict = json.loads(response["SecretString"])
                self._secrets_cache = secret_dict
                logger.info(
                    "Successfully fetched secrets from Secrets Manager",
                    secret_count=len(secret_dict),
                )
                return secret_dict
            raise ValueError("Secret does not contain SecretString")  # noqa: TRY301

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(
                "Error fetching secrets from AWS Secrets Manager",
                error_code=error_code,
                secret_name=self.secret_name,
                region=self.region_name,
            )

            if error_code == "ResourceNotFoundException":
                logger.error(
                    "Secret not found",
                    secret_name=self.secret_name,
                    region=self.region_name,
                )
            elif error_code == "InvalidRequestException":
                logger.error("Invalid request for secret", secret_name=self.secret_name)
            elif error_code == "InvalidParameterException":
                logger.error("Invalid parameter for secret", secret_name=self.secret_name)
            elif error_code == "DecryptionFailure":
                logger.error("Failed to decrypt the secret")
            elif error_code == "InternalServiceError":
                logger.error("Internal service error from AWS Secrets Manager")

            raise
        except Exception as e:
            logger.error("Unexpected error fetching secrets", error=str(e))
            raise

    def get_secret_value(self, key: str, default: str | None = None) -> str | None:
        """
        Get a specific secret value by key.

        Args:
            key: The key of the secret to retrieve
            default: Default value if key not found

        Returns:
            The secret value or default if not found
        """
        try:
            secrets = self.get_secrets()
            return secrets.get(key, default)
        except Exception:
            return default

    def refresh_secrets(self) -> dict[str, str]:
        """
        Force refresh secrets from AWS Secrets Manager.

        Returns:
            Dictionary containing refreshed secrets
        """
        return self.get_secrets(force_refresh=True)


# Singleton instance
_secrets_manager_instance: SecretsManager | None = None


def get_secrets_manager(
    secret_name: str | None = None, region_name: str | None = None
) -> SecretsManager:
    """
    Get or create a singleton instance of SecretsManager.

    Args:
        secret_name: Name of the secret
        region_name: AWS region

    Returns:
        SecretsManager instance
    """
    global _secrets_manager_instance

    if _secrets_manager_instance is None:
        _secrets_manager_instance = SecretsManager(secret_name=secret_name, region_name=region_name)

    return _secrets_manager_instance
