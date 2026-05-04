"""Authentication routes."""

import logging

from fastapi import APIRouter, Depends, Response
from fastapi_csrf_protect import CsrfProtect
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies.auth import (
    get_current_user,
    get_current_user_optional,
    get_refresh_token_from_cookie,
)
from app.api.dependencies.config import get_config
from app.api.routes.auth.dependencies import AuthServiceDep
from app.api.routes.auth.utils import (
    clear_token_cookies,
    set_token_cookies,
)
from app.config.settings import Settings
from app.core.auth.exceptions import (
    InvalidResetTokenError,
    InvalidTokenError,
    TokenExpiredError,
    TokenNotFoundError,
)
from app.core.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SendVerificationRequest,
    UpdateProfileRequest,
    UserResponse,
)
from app.core.common.schema import GenericResponse
from app.db.models import User
from app.shared.exceptions.base import AppException
from app.shared.exceptions.common import BadRequestException, ServerErrorException
from app.shared.exceptions.user_exceptions import (
    BlockedAccountError,
    InactiveAccountError,
    UserNotFoundError,
    WrongPasswordError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=GenericResponse[dict])
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
    csrf_protect: CsrfProtect = Depends(),
    settings: Settings = Depends(get_config),
):
    """Login endpoint with proper error handling."""
    try:
        access_token, refresh_token = await auth_service.login(request)

        set_token_cookies(response, access_token, refresh_token, settings)

        plain_csrf_token, signed_csrf_token = csrf_protect.generate_csrf_tokens()
        csrf_protect.set_csrf_cookie(signed_csrf_token, response)

        return GenericResponse[dict](data={"message": "Login successful", "csrf_token": plain_csrf_token})
    except (
        UserNotFoundError,
        WrongPasswordError,
        InactiveAccountError,
        BlockedAccountError,
    ):
        raise
    except ValidationError as e:
        raise BadRequestException("Invalid request data") from e
    except SQLAlchemyError as e:
        logger.exception("Database error during login")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during login")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.post("/refresh", response_model=GenericResponse[dict])
async def refresh_token(
    response: Response,
    auth_service: AuthServiceDep,
    refresh_token=Depends(get_refresh_token_from_cookie),
    settings: Settings = Depends(get_config),
    csrf_protect: CsrfProtect = Depends(),
):
    """Refresh token endpoint — also rotates the CSRF token inside the session."""
    try:
        access_token, refresh_token = await auth_service.refresh_token(refresh_token)

        set_token_cookies(response, access_token, refresh_token, settings)

        plain_csrf_token, signed_csrf_token = csrf_protect.generate_csrf_tokens()
        csrf_protect.set_csrf_cookie(signed_csrf_token, response)

        return GenericResponse[dict](data={"message": "Token refreshed successfully", "csrf_token": plain_csrf_token})
    except (
        TokenNotFoundError,
        InvalidTokenError,
        TokenExpiredError,
        UserNotFoundError,
        InactiveAccountError,
    ):
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error during token refresh")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during token refresh")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.post("/logout", response_model=GenericResponse[str])
async def logout(
    response: Response,
    auth_service: AuthServiceDep,
    user: User = Depends(get_current_user),
    refresh_token=Depends(get_refresh_token_from_cookie),
    csrf_protect: CsrfProtect = Depends(),
) -> dict[str, str]:
    """Logout endpoint with proper error handling."""
    try:
        await auth_service.logout(user.id, refresh_token)
        clear_token_cookies(response)
        csrf_protect.unset_csrf_cookie(response)

        return GenericResponse[str](data="Logged out successfully")
    except (TokenNotFoundError, InvalidTokenError):
        raise
    except SQLAlchemyError as e:
        logger.exception("Database error during logout")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during logout")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.post("/forgot-password", response_model=GenericResponse[str])
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthServiceDep,
):
    """Forgot password endpoint with proper error handling."""
    try:
        await auth_service.forgot_password(request)
        return GenericResponse[str](
            data="If the email exists, a password reset link has been sent"
        )
    except AppException:
        raise
    except ValidationError as e:
        raise BadRequestException("Invalid request data") from e
    except SQLAlchemyError as e:
        logger.exception("Database error during forgot password")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during forgot password")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.post("/reset-password", response_model=GenericResponse[str])
async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthServiceDep,
):
    """Reset password endpoint with proper error handling."""
    try:
        await auth_service.reset_password(request)

        return GenericResponse[str](data="Password has been reset successfully")
    except (InvalidResetTokenError, AppException):
        raise
    except ValidationError as e:
        raise BadRequestException("Invalid request data") from e
    except SQLAlchemyError as e:
        logger.exception("Database error during password reset")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during password reset")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.get("/me", response_model=GenericResponse[UserResponse])
async def get_current_user_info(
    user: User = Depends(get_current_user),
):
    """Get current user info with proper error handling."""
    try:
        data = UserResponse.model_validate(user)
        if user.is_superuser:
            data.role = "superadmin"
        return GenericResponse[UserResponse](data=data)
    except ValidationError as e:
        raise BadRequestException("Failed to process user data") from e
    except SQLAlchemyError as e:
        logger.exception("Database error during get current user")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during get current user")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.put("/verify-profile", response_model=GenericResponse[str])
async def update_profile(
    request: UpdateProfileRequest,
    auth_service: AuthServiceDep,
    user: User | None = Depends(get_current_user_optional),
):
    """Update profile endpoint with proper error handling.

    If user is authenticated, token is not required.
    If user is not authenticated, token must be provided for verification.
    """
    try:
        # If user is not authenticated, token is required
        if user is None and request.token is None:
            raise BadRequestException(
                "Authentication token is required when not logged in"
            )

        await auth_service.profile_setup(request, user)
        return GenericResponse[str](
            data="Profile updated successfully, please verify your profile"
        )
    except AppException:
        raise
    except ValidationError as e:
        raise BadRequestException("Invalid request data") from e
    except SQLAlchemyError as e:
        logger.exception("Database error during profile update")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during profile update")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e


@router.post("/send-verification-email", response_model=GenericResponse[str])
async def send_verification_email(
    request: SendVerificationRequest,
    auth_service: AuthServiceDep,
    user: User = Depends(get_current_user),
):
    """Send verification email endpoint with proper error handling."""
    try:
        await auth_service.verify_email_for_profile_setup(request, user)
        return GenericResponse[str](
            data="Email sent Successfully, Please Check your email and verify"
        )
    except AppException:
        raise
    except ValidationError as e:
        raise BadRequestException("Invalid request data") from e
    except SQLAlchemyError as e:
        logger.exception("Database error during send verification email")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during send verification email")
        raise ServerErrorException(
            "An unexpected error occurred. Please try again later."
        ) from e
