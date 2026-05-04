from leapx.common.types.providers import (
    LLMProviderType,
    OCRProviderType,
)
from leapx.services.credentials.base import Credential
from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential
from leapx.services.credentials.ocr.azure_config import AzureOcrCredential
from leapx.services.credentials.openai_config import OpenAICredential

#  mapping used for validating configuration

OCR_CREDENTIAL_BY_PROVIDER: dict[OCRProviderType, type[Credential]] = {
    OCRProviderType.AWS_TEXTRACT: AwsOcrCredential,
    OCRProviderType.AZURE: AzureOcrCredential,
}

LLM_PROVIDER_CREDENTIAL_BY_PROVIDER: dict[LLMProviderType, type[Credential]] = {
    LLMProviderType.BEDROCK: BedrockCredential,
    LLMProviderType.OPENAI: OpenAICredential,
}
