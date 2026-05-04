"""Authentication dependencies."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.config import get_config
from app.api.dependencies.db_session import get_db_session
from app.config.settings import Settings
from app.core.auth.exceptions import (
    InvalidTokenError,
    ProfileNotSetupError,
    TokenNotFoundError,
    UserNotFoundError,
)
from app.core.auth.repository import AuthRepository
from app.core.auth.utils import verify_token
from app.db.models import User, UserStatus
from app.shared.constants.app_constants import RolesClass
from app.shared.exceptions.user_exceptions import InactiveAccountError

ALLOWED_ROUTES = {
    "/api/auth/me",
    "/api/auth/logout",
    "/api/auth/profile",
    "/api/auth/send-verification-email",
    "/api/auth/verify-profile",
}


def can_login(user_instance: User) -> bool:
    return user_instance.is_active and user_instance.status in {
        UserStatus.ACTIVE,
        UserStatus.PENDING,
    }


def is_not_verified_and_allowed(request: Request, user_instance: User) -> bool:
    return (
        not user_instance.is_profile_verified and request.url.path not in ALLOWED_ROUTES
    )


def is_not_setup_and_allowed(request: Request, user_instance: User) -> bool:
    return (
        user_instance.status == UserStatus.PENDING
        and request.url.path not in ALLOWED_ROUTES
    )


async def get_auth_tokens(
    request: Request,
) -> tuple[str | None, str | None]:
    """
    Extract access and refresh tokens from cookies.
    """
    access_token: str | None = request.cookies.get("access_token")
    refresh_token: str | None = request.cookies.get("refresh_token")

    return access_token, refresh_token


async def get_access_token_from_cookie(
    auth_tokens: tuple[str | None, str | None] = Depends(get_auth_tokens),
) -> str:
    """
    Extract access token from cookie.
    """
    access_token, _ = auth_tokens
    if not access_token:
        raise InvalidTokenError("Access token not provided")
    return access_token


async def get_refresh_token_from_cookie(
    auth_tokens: tuple[str | None, str | None] = Depends(get_auth_tokens),
) -> str:
    """Extract refresh token from cookie."""
    _, refresh_token = auth_tokens
    if not refresh_token:
        raise TokenNotFoundError()
    return refresh_token


async def get_current_user(
    request: Request,
    auth_tokens: tuple[str | None, str | None] = Depends(get_auth_tokens),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
) -> User:
    """
    Get the current authenticated user from the access token cookie.
    """
    access_token, _ = auth_tokens

    if not access_token:
        raise TokenNotFoundError()

    payload = verify_token(access_token, settings, token_type="access")

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token payload")

    repository = AuthRepository(session)
    user = await repository.get_user_by_id(int(user_id))
    if not user:
        raise UserNotFoundError()
    if not can_login(user):
        raise InactiveAccountError()

    if is_not_verified_and_allowed(request, user):
        raise InactiveAccountError()

    if is_not_setup_and_allowed(request, user):
        raise ProfileNotSetupError()
    return user


async def get_current_user_optional(
    request: Request,
    auth_tokens: tuple[str | None, str | None] = Depends(get_auth_tokens),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_config),
) -> User | None:
    """
    Get the current authenticated user from the access token cookie.
    Returns None if no valid authentication token is provided.
    """
    access_token, _ = auth_tokens

    if not access_token:
        return None

    try:
        payload = verify_token(access_token, settings, token_type="access")

        user_id = payload.get("sub")
        if not user_id:
            return None

        repository = AuthRepository(session)
        user = await repository.get_user_by_id(int(user_id))

        if not user or not user.is_active:
            return None

        return user
    except Exception:
        return None


def require_roles(role: RolesClass):
    min_required = RolesClass.rank(role)

    def _dep(current_user: User = Depends(get_current_user)) -> User:
        role = current_user.role
        if current_user.is_superuser:
            role = "superadmin"
            
        if RolesClass.rank(role) < min_required:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _dep
