from abc import ABC, abstractmethod
from typing import Any

from app.providers.email.template_manager import EmailTemplateManager


class EmailProvider(ABC):
    """Base email provider interface."""

    def __init__(self):
        """Initialize email provider with template manager."""
        self.template_manager = EmailTemplateManager()

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
    ) -> bool:
        """Send an email."""

    async def send_templated_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: dict[str, Any],
    ) -> bool:
        html_body = self.template_manager.render(template_name, template_data)
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
        )
