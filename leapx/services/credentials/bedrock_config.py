import os

from pydantic import AliasChoices, Field

from leapx.services.credentials.base import Credential
from leapx.services.credentials.exceptions import (
    MissingBedrockCredentialsError,
)


class BedrockCredential(Credential):
    access_key_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("access_key_id", "AWS_ACCESS_KEY_ID"),
    )
    secret_access_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("secret_access_key", "AWS_SECRET_ACCESS_KEY"),
    )
    session_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("session_token", "AWS_SESSION_TOKEN"),
    )
    region_name: str | None = Field(
        default=None, validation_alias=AliasChoices("region_name", "AWS_REGION_NAME")
    )

    def validate_for_use(self) -> None:
        mode = os.getenv("MODE", "development").lower()
        if mode in ("staging", "production"):
            return

        missing: list[str] = []
        if not self.access_key_id:
            missing.append("access_key_id")
        if not self.secret_access_key:
            missing.append("secret_access_key")
        if not self.region_name:
            missing.append("region_name")
        if missing:
            raise MissingBedrockCredentialsError(
                details={
                    "credential_type": type(self).__name__,
                    "missing_fields": missing,
                },
            )
