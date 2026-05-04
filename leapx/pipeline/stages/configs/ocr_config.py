from typing import Any

from pydantic import model_validator

from leapx.common.types.providers import OCRProviderType
from leapx.pipeline.stages.configs.base import BlockConfig
from leapx.services.credentials.base import Credential
from leapx.services.credentials.mapping import OCR_CREDENTIAL_BY_PROVIDER


class OCRConfig(BlockConfig):
    """ """

    provider: OCRProviderType
    credential: Credential | None

    @model_validator(mode="before")
    @classmethod
    def validate_model_input(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Validate OCR credential type and required fields.

        Raises:
            ProviderMismatchError: If the credential type does not match the provider
                or the provider is not supported.
        """
        ocr_provider: OCRProviderType = values.get("provider")
        credential: Credential = values.get("credential")
        if isinstance(ocr_provider, str):
            ocr_provider = OCRProviderType(ocr_provider)
        if credential is None:
            credential = OCR_CREDENTIAL_BY_PROVIDER.get(ocr_provider.value)()

        credential.validate_for_use()
        return values
