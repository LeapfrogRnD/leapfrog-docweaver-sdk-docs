"""SMTP email provider implementation."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config.settings import Settings
from app.logger import logger
from app.providers.email.base import EmailProvider


class SMTPEmailProvider(EmailProvider):
    """SMTP email provider using smtplib."""

    def __init__(self, settings: Settings):
        """Initialize SMTP email provider."""
        super().__init__()
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.smtp_use_ssl = settings.smtp_use_ssl
        self.from_email = settings.email_from
        self.from_name = settings.email_from_name

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
    ) -> bool:
        """Send an email using SMTP."""
        try:
            if not self.smtp_host or not self.smtp_port:
                logger.error("SMTP host or port not configured")
                return False

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)

            if self.smtp_use_ssl:
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30) as server:
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                    server.ehlo()
                    if self.smtp_use_tls:
                        server.starttls()
                        server.ehlo()
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(message)

            logger.info(
                "Email sent successfully via SMTP",
                to_email=to_email,
                smtp_host=self.smtp_host,
            )
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(
                "SMTP authentication failed",
                error=str(e),
                to_email=to_email,
                smtp_host=self.smtp_host,
            )
            return False
        except smtplib.SMTPException as e:
            logger.error(
                "SMTP error sending email",
                error=str(e),
                to_email=to_email,
                smtp_host=self.smtp_host,
            )
            return False
        except TimeoutError as e:
            logger.error(
                "Timeout connecting to SMTP server",
                error=str(e),
                to_email=to_email,
                smtp_host=self.smtp_host,
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error sending email via SMTP",
                error=str(e),
                to_email=to_email,
                smtp_host=self.smtp_host,
            )
            return False
