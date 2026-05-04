"""Authentication service for business logic."""

import secrets
from datetime import UTC, datetime, timedelta

from app.config.settings import Settings
from app.core.auth.exceptions import (
    InvalidResetTokenError,
    InvalidTokenError,
    TokenExpiredError,
    TokenNotFoundError,
)
from app.core.auth.repository import AuthRepository
from app.core.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SendVerificationRequest,
    UpdateProfileRequest,
)
from app.core.auth.utils import create_access_token, create_refresh_token, verify_token
from app.core.common.service import BaseService
from app.db.models import User, UserStatus
from app.providers.email.base import EmailProvider
from app.shared.exceptions.common import BadRequestException
from app.shared.exceptions.user_exceptions import (
    BlockedAccountError,
    InactiveAccountError,
    UserNotFoundError,
    WrongPasswordError,
)
from app.shared.utils.password import hash_password, verify_password


class AuthService(BaseService):
    def __init__(
        self,
        repository: AuthRepository,
        settings: Settings,
        email_provider: EmailProvider | None = None,
    ):
        super().__init__()
        self.repository = repository
        self.settings = settings
        self.email_provider = email_provider

    async def login(self, request: LoginRequest) -> tuple[str, str, int]:
        user = await self.repository.get_user_by_email(request.email)
        if not user:
            self.logger.warning(f"Login failed: User not found for email {request.email}")
            raise UserNotFoundError()

        if not verify_password(request.password, user.password):
            self.logger.warning(f"Login failed: Invalid password for email {request.email}")
            raise WrongPasswordError()
        if not user.is_active:
            self.logger.warning(f"Login failed: Inactive user account for email {request.email}")
            raise InactiveAccountError()
        if user.status.value == "blocked":
            self.logger.warning(f"Login failed: User Blocked for email {request.email}")
            raise BlockedAccountError()

        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data, self.settings)
        refresh_token = create_refresh_token(token_data, self.settings)

        expires_at = datetime.now(UTC) + timedelta(days=self.settings.jwt_refresh_token_expire_days)
        await self.repository.save_refresh_token(user.id, refresh_token, expires_at)

        self.logger.info(f"Login successful for user: {user.email}")

        return (
            access_token,
            refresh_token,
        )

    async def profile_setup(self, request: UpdateProfileRequest, user: User | None):
        # If user is not provided (not authenticated), verify using token
        if user is None:
            if not request.token:
                raise BadRequestException("Token is required when not authenticated")

            user = await self.repository.get_user_by_verification_token(request.token)
            if not user:
                raise InvalidTokenError("Invalid verification token")

        existing_user = await self.repository.get_user_by_email(request.email)

        if existing_user and existing_user.id != user.id:
            raise BadRequestException("Email already in use")

        if user.status == UserStatus.ACTIVE.value:
            raise BadRequestException("Profile is already set up for this user")

        verification_token = secrets.token_urlsafe(16)

        update_payload = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "password": hash_password(request.password),
            "status": UserStatus.ACTIVE,
            "is_profile_verified": True,
            "verification_token": verification_token,
        }

        if user.is_superuser:
            update_payload["email"] = request.email

        await self.repository.update_user(user.id, update_payload)

    async def verify_email_for_profile_setup(self, request: SendVerificationRequest, user: User):
        existing_user = await self.repository.get_user_by_email(request.email)

        if existing_user and existing_user.id != user.id:
            raise BadRequestException("Email already in use")

        if user.status.value == UserStatus.ACTIVE:
            raise BadRequestException("Profile is already set up for this user")

        verification_token = secrets.token_urlsafe(16)
        update_payload = {
            "verification_token": verification_token,
        }
        if user.is_superuser:
            update_payload["email"] = request.email

        await self.repository.update_user(user.id, update_payload)
        await self.email_provider.send_templated_email(
            to_email=request.email,
            subject="Verify Your Email Address",
            template_name="verify_profile.html",
            template_data={
                "user_name": user.full_name,
                "verify_link": f"{self.settings.frontend_url}/complete-profile?email={request.email}&token={verification_token}",
                "year": datetime.now().year,
            },
        )

    async def verify_profile(self, token: str):
        user = await self.repository.get_user_by_verification_token(token)

        if not user:
            self.logger.warning("Profile verification failed: Invalid token")
            raise InvalidTokenError("Invalid verification token")

        await self.repository.update_user(
            user.id,
            {
                "is_profile_verified": True,
                "verification_token": None,
            },
        )

    async def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        if not refresh_token:
            raise TokenNotFoundError()

        payload = verify_token(refresh_token, self.settings, token_type="refresh")
        db_token = await self.repository.get_refresh_token(refresh_token)
        if not db_token or db_token.is_revoked:
            self.logger.warning("Refresh token is invalid or revoked")
            raise InvalidTokenError("Invalid or revoked refresh token")

        current_time = datetime.now(UTC)
        token_expires_at = (
            db_token.expires_at.replace(tzinfo=UTC)
            if db_token.expires_at.tzinfo is None
            else db_token.expires_at
        )

        if token_expires_at < current_time:
            self.logger.warning("Refresh token has expired")
            raise TokenExpiredError("Refresh token has expired")

        user_id = payload.get("sub")
        if not user_id:
            self.logger.warning("Refresh token missing user ID")
            raise InvalidTokenError("Invalid token payload")

        user = await self.repository.get_user_by_id(int(user_id))
        if not user:
            self.logger.warning(f"Refresh token failed: User not found for ID {user_id}")
            raise UserNotFoundError()

        if not user.is_active:
            self.logger.warning(f"Refresh token failed: Inactive user account for ID {user_id}")
            raise InactiveAccountError()

        await self.repository.revoke_refresh_token(int(user_id), refresh_token)

        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data, self.settings)
        new_refresh_token = create_refresh_token(token_data, self.settings)

        expires_at = datetime.now(UTC) + timedelta(days=self.settings.jwt_refresh_token_expire_days)
        await self.repository.save_refresh_token(user.id, new_refresh_token, expires_at)

        self.logger.info(f"Access token refreshed for user: {user.email}")

        return (
            access_token,
            new_refresh_token,
        )

    async def forgot_password(self, request: ForgotPasswordRequest) -> bool:
        user = await self.repository.get_user_by_email(request.email)
        if not user:
            self.logger.warning(f"Forgot password: User not found for email {request.email}")
            raise UserNotFoundError()

        if not user.is_active:
            self.logger.warning(f"Forgot password: Inactive user account for email {request.email}")
            raise UserNotFoundError()

        reset_token = secrets.token_urlsafe(16)

        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.settings.password_reset_token_expire_minutes
        )

        await self.repository.save_password_reset_token(user.id, reset_token, expires_at)

        reset_link = f"{self.settings.frontend_url}/reset-password?token={reset_token}"

        await self.email_provider.send_templated_email(
            to_email=user.email,
            subject="Reset Your Password",
            template_name="forgot_password.html",
            template_data={
                "user_name": user.full_name,
                "user_email": user.email,
                "reset_link": reset_link,
                "year": datetime.now().year,
            },
        )

        return True

    async def reset_password(self, request: ResetPasswordRequest) -> bool:
        user = await self.repository.get_user_by_reset_token(request.token)

        if not user:
            self.logger.warning("Password reset failed: Invalid token")
            raise InvalidResetTokenError()

        if not user.forget_password_token_expiry:
            self.logger.warning(f"Password reset failed: No expiry set for user {user.email}")
            raise InvalidResetTokenError()

        current_time = datetime.now(UTC)
        token_expiry = (
            user.forget_password_token_expiry.replace(tzinfo=UTC)
            if user.forget_password_token_expiry.tzinfo is None
            else user.forget_password_token_expiry
        )

        if token_expiry < current_time:
            self.logger.warning(f"Password reset failed: Expired token for user {user.email}")
            raise InvalidResetTokenError("Password reset token has expired")

        hashed_password = hash_password(request.new_password)

        await self.repository.update_user_password(user.id, hashed_password)

        await self.repository.clear_password_reset_token(user.id)

        return True

    async def logout(self, user_id: int, refresh_token: str):
        if not refresh_token:
            raise TokenNotFoundError()
        try:
            verify_token(refresh_token, self.settings, token_type="refresh")
        except Exception as e:
            self.logger.warning(f"Logout failed: Invalid refresh token - {e}")
            raise InvalidTokenError("Invalid refresh token") from e

        revoked = await self.repository.revoke_refresh_token(user_id, refresh_token)

        if not revoked:
            self.logger.warning("Logout failed: Token not found in database")
            raise InvalidTokenError("Invalid refresh token")
