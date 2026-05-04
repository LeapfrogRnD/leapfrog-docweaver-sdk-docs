import os

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError
from pydantic import AliasChoices, Field

from leapx.services.credentials.base import Credential
from leapx.services.credentials.exceptions import (
    InvalidAwsCredentialsError,
    MissingAwsCredentialsError,
)


class AwsOcrCredential(Credential):
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

    def _is_valid_keys(self) -> bool:
        try:
            sts = boto3.client(
                "sts",
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                aws_session_token=self.session_token,
                region_name=self.region_name,
            )
            sts.get_caller_identity()
        except (ClientError, NoCredentialsError, EndpointConnectionError, Exception):
            return False
        return True

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
            raise MissingAwsCredentialsError(
                details={
                    "credential_type": type(self).__name__,
                    "missing_fields": missing,
                },
            )

        if not self._is_valid_keys():
            raise InvalidAwsCredentialsError(
                details={
                    "credential_type": type(self).__name__,
                },
            )
