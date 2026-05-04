"""Authentication schemas."""

import re

from pydantic import EmailStr, Field, field_validator

from app.core.common.schema import OrmResponseModel, RequestModel

MIN_PASSWORD_LIMIT = 8
MAX_PASSWORD_LIMIT = 128


def check_user_password_rule(v):
    if not v or not v.strip():
        raise ValueError("Password cannot be empty")

    if len(v) < MIN_PASSWORD_LIMIT:
        raise ValueError("Password must be at least 8 characters long")
    if len(v) > MAX_PASSWORD_LIMIT:
        raise ValueError("Password must not exceed 128 characters")

    if not re.search(r"[a-z]", v):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"\d", v):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        raise ValueError("Password must contain at least one special character")


class LoginRequest(RequestModel):
    """Login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password is not empty."""
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class ForgotPasswordRequest(RequestModel):
    """Forgot password request schema."""

    email: EmailStr = Field(..., description="User email address")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        if "@" not in v.strip():
            raise ValueError("Email should have @")
        return v.strip().lower()


class ResetPasswordRequest(RequestModel):
    """Reset password request schema."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=6, description="New password")
    confirm_password: str = Field(..., min_length=6, description="Confirm new password")

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate token is not empty."""
        if not v or not v.strip():
            raise ValueError("Reset token cannot be empty")
        return v.strip()

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        check_user_password_rule(v)
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate that passwords match."""
        if not v:
            raise ValueError("Confirm password cannot be empty")
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class UserResponse(OrmResponseModel):
    """User response schema."""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")
    is_active: bool = Field(..., description="Whether user is active")
    is_profile_verified: bool = Field(..., description="Whether user profile is verified")
    role: str | None = Field(None, description="User role")
    status: str | None = Field(str, description="user status")


class UpdateProfileRequest(RequestModel):
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User last name")
    password: str = Field(..., min_length=6, description="Password")
    current_password: str | None = Field(
        None, min_length=6, description="Old password"
    )
    token: str | None = Field(None, description="Token for validation (optional if authenticated)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.strip().lower()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        """Validate that names are not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace-only")
        if len(v.strip()) < 1:
            raise ValueError("Name must be at least 1 character long")
        if len(v.strip()) > 50:
            raise ValueError("Name must not exceed 50 characters")
        if not re.match(r"^[a-zA-Z\s\'-]+$", v.strip()):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength for length and complexity."""
        check_user_password_rule(v)
        return v

    @field_validator("current_password")
    @classmethod
    def passwords_different(cls, v: str | None, info) -> str | None:
        """Validate that new password is different from current password."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Current password cannot be empty")
        if "password" in info.data and v == info.data["password"]:
            raise ValueError("New password must be different from current password")
        return v


class SendVerificationRequest(RequestModel):
    email: EmailStr = Field(..., description="User email address")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.strip().lower()
class CsrfTokenResponse(OrmResponseModel):
    """Response schema carrying a rotated CSRF plain token."""

    csrf_token: str
