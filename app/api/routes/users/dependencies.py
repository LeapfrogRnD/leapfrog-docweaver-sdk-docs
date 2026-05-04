"""User API dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.config import get_config
from app.api.dependencies.db_session import get_db_session
from app.api.dependencies.email import get_email_provider
from app.config.settings import Settings
from app.core.users.repository import UserRepository
from app.core.users.service import UserService
from app.providers.email.base import EmailProvider


def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
    email_provider: EmailProvider = Depends(get_email_provider),
) -> UserService:
    """Get user service instance."""
    return UserService(UserRepository(session), settings, email_provider)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
