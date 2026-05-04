"""JWT token utilities."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config.settings import Settings
from app.core.auth.exceptions import InvalidTokenError, TokenExpiredError


def create_access_token(data: dict[str, Any], settings: Settings) -> str:
    """
    Create a new access token.

    Args:
        data: Data to encode in the token
        settings: Application settings

    Returns:
        Encoded JWT access token
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict[str, Any], settings: Settings) -> str:
    """
    Create a new refresh token.

    Args:
        data: Data to encode in the token
        settings: Application settings

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh", "jti": secrets.token_urlsafe(16)})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, settings: Settings, token_type: str = "access") -> dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify
        settings: Application settings
        token_type: Expected token type ('access' or 'refresh')

    Returns:
        Decoded token payload

    Raises:
        TokenExpiredError: If token has expired
        InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        # Verify token type
        if payload.get("type") != token_type:
            raise InvalidTokenError(f"Invalid token type. Expected '{token_type}'")

        return payload
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired") from e
    except JWTError as e:
        raise InvalidTokenError("Invalid token") from e
