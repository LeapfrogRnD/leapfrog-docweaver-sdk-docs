from fastapi import Response

from app.config.settings import Settings


def set_token_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    settings: Settings,
) -> None:
    """
    Set access and refresh tokens in HTTP-only cookies.

    Args:
        response: FastAPI response object
        access_token: JWT access token
        refresh_token: JWT refresh token
        settings: Application settings
    """
    # Set access token cookie
    is_dev = settings.mode.lower() in ("development", "local")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        samesite="strict" if not is_dev else "none",
    )

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict" if not is_dev else "none",
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
    )

def clear_token_cookies(response: Response) -> None:
    """
    Clear access and refresh token cookies.

    Args:
        response: FastAPI response object
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
