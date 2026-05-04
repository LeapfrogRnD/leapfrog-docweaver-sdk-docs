from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.config import get_config
from app.api.dependencies.db_session import get_db_session
from app.api.dependencies.email import get_email_provider
from app.config.settings import Settings
from app.core.auth.repository import AuthRepository
from app.core.auth.service import AuthService
from app.providers.email.base import EmailProvider


def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
    email_provider: EmailProvider = Depends(get_email_provider),
) -> AuthService:
    return AuthService(AuthRepository(session), settings, email_provider)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
