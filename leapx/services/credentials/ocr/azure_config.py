from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ClientAuthenticationError
from pydantic import AliasChoices, Field

from leapx.common.observability.logger import logger
from leapx.services.credentials.base import Credential
from leapx.services.credentials.constant import test_image
from leapx.services.credentials.exceptions import (
    InvalidAzureCredentialsError,
    MissingAzureCredentialsError,
)


class AzureOcrCredential(Credential):
    endpoint: str | None = Field(
        default=None, validation_alias=AliasChoices("endpoint", "AZURE_OCR_ENDPOINT")
    )
    api_key: str | None = Field(
        default=None, validation_alias=AliasChoices("api_key", "AZURE_OCR_API_KEY")
    )

    def _is_valid_keys(self) -> bool:
        """
        Validate Azure Document Intelligence credentials.

        Tests the configured credentials by making a minimal request
        to the Azure service using a small test image. This helps
        verify that the endpoint and API key are valid before
        processing actual documents.

        Returns:
            bool: True if credentials are valid and service is accessible,
                 False otherwise

        Raises:
            ClientAuthenticationError: If credentials are invalid
            Exception: For other service or network errors
        """

        try:
            analyze_request = {"base64Source": test_image}
            client = DocumentIntelligenceClient(
                endpoint=self.endpoint,
                credential=AzureKeyCredential(self.api_key),
            )
            client.begin_analyze_document(
                "prebuilt-read", analyze_request=analyze_request
            )
            logger.info("Azure credentials validated successfully")
        except (ClientAuthenticationError, Exception):
            logger.error("Azure credential validation failed - invalid credentials")
            return False
        return True

    def validate_for_use(self) -> None:
        missing: list[str] = []
        if not self.endpoint:
            missing.append("endpoint")
        if not self.api_key:
            missing.append("api_key")

        if missing:
            raise MissingAzureCredentialsError(
                details={
                    "credential_type": type(self).__name__,
                    "missing_fields": missing,
                    "hint": "Provide values directly or set AZURE_OCR_ENDPOINT and AZURE_OCR_API_KEY in .env file",
                },
            )
        if not self._is_valid_keys():
            raise InvalidAzureCredentialsError(
                details={
                    "credential_type": type(self).__name__,
                },
            )
