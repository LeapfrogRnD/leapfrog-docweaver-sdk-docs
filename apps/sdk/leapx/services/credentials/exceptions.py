from collections.abc import Mapping

from leapx.common.exceptions import LeapXError


class ProviderMismatchError(LeapXError):
    """Raised when credential type doesn't match the provider."""

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            provider = details.get("ocr_provider") or details.get(
                "extraction_provider", "Unknown"
            )
            expected = details.get("expected_type", "Unknown")
            received = details.get("received_type", "Unknown")
            message = (
                f"Invalid credential type for provider {provider}. "
                f"Expected {expected}, got {received}"
            )
        super().__init__(message, details)


class InvalidCredentialsError(LeapXError):
    """Raised when credentials are invalid or cannot be validated."""

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            if "extraction_provider" in details:
                provider = details.get("extraction_provider")
                message = f"Invalid credentials for extraction provider: {provider}"
            elif "llm_model" in details:
                model = details.get("llm_model")
                message = f"Cannot infer extraction provider from llm_model: {model}"
        super().__init__(message, details)


class MissingCredentialsError(InvalidCredentialsError):
    """Raised when required credentials are missing."""

    def __init__(
        self, message: str = "", details: Mapping[str, any] | None = None
    ) -> None:
        if not message and details:
            missing_fields = details.get("missing_fields", [])
            if missing_fields:
                message = (
                    f"Missing required credential fields: {', '.join(missing_fields)}"
                )
        super().__init__(message, details)


# Provider-specific exceptions
class MissingAzureCredentialsError(MissingCredentialsError):
    """Raised when Azure credentials are missing."""

    pass


class MissingAwsCredentialsError(MissingCredentialsError):
    """Raised when AWS credentials are missing."""

    pass


class MissingBedrockCredentialsError(MissingCredentialsError):
    """Raised when Bedrock credentials are missing."""

    pass


class InvalidBedrockCredentialsError(InvalidCredentialsError):
    """Raised when Bedrock credentials are invalid."""

    pass


class InvalidAzureCredentialsError(InvalidCredentialsError):
    """Raised when Azure credentials are invalid."""

    pass


class InvalidAwsCredentialsError(InvalidCredentialsError):
    """Raised when AWS credentials are invalid."""

    pass
