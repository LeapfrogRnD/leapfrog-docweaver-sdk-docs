"""Amazon SES email provider implementation."""

from botocore.exceptions import ClientError

from app.config.settings import Settings
from app.logger import logger
from app.providers.clients.aws_boto import get_boto_client
from app.providers.email.base import EmailProvider
from app.providers.email.exceptions import (
    SesClientError,
    SesSystemError,
    SesUnverifiedEmailError,
)


class SESEmailProvider(EmailProvider):
    """Amazon SES email provider."""

    def __init__(self, settings: Settings):
        """Initialize SES email provider."""
        super().__init__()
        self.settings = settings
        self.client = get_boto_client(
            service_name="ses",
            region_name=settings.aws_region,
        )
        self.from_email = settings.email_from
        self.from_name = settings.email_from_name

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
    ) -> bool:
        """Send an email using Amazon SES."""
        try:
            source = f"{self.from_name} <{self.from_email}>"

            message = {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            }

            response = self.client.send_email(
                Source=source,
                Destination={"ToAddresses": [to_email]},
                Message=message,
            )

            logger.info(
                "Email sent successfully via SES",
                message_id=response["MessageId"],
                to_email=to_email,
            )
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            # Specific handling for Unverified Identities
            if (
                error_code == "MessageRejected"
                and "Email address is not verified" in error_message
            ):
                logger.warning(
                    "Attempted to send to unverified email in Sandbox",
                    to_email=to_email,
                )
                raise SesUnverifiedEmailError

            if error_code == "ThrottlingException":
                logger.error("SES Speed limit reached")
                raise SesSystemError

            logger.error(
                "Failed to send email via SES",
                error=str(e),
                to_email=to_email,
                error_code=error_code,
            )
            raise SesClientError
        except Exception as e:
            logger.error(
                "Unexpected error sending email via SES",
                error=str(e),
                to_email=to_email,
            )
            return SesClientError
