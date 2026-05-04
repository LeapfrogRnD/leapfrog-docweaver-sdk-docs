from typing import Annotated

from fastapi import Depends

from app.api.dependencies.config import get_config
from app.config.settings import Settings
from app.providers.email.aws_ses import SESEmailProvider
from app.providers.email.base import EmailProvider
from app.providers.email.smtp import SMTPEmailProvider


def get_email_provider(settings: Settings = Depends(get_config)) -> EmailProvider:
    """Get email provider instance based on configuration."""
    if settings.email_provider.lower() == "ses":
        return SESEmailProvider(settings=settings)
    return SMTPEmailProvider(settings=settings)


EmailProviderDep = Annotated[EmailProvider, Depends(get_email_provider)]
