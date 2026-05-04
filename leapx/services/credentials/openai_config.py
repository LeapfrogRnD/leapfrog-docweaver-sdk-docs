from pydantic import Field

from leapx.services.credentials.base import Credential
from leapx.services.credentials.exceptions import InvalidCredentialsError


class OpenAICredential(Credential):
    api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")

    def validate_for_use(self) -> None:
        if not self.api_key:
            raise InvalidCredentialsError(
                details={
                    "credential_type": type(self).__name__,
                    "missing_fields": ["api_key"],
                },
            )
