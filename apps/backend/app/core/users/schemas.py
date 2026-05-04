"""User schemas."""

from datetime import datetime

from pydantic import EmailStr, Field, field_validator, model_validator

from app.core.common.schema import OrmResponseModel, RequestModel
from app.db.models import UserStatus
from app.shared.constants.app_constants import Roles


class UserInviteRequest(RequestModel):
    """User invite request schema."""

    email: EmailStr = Field(..., description="User email address to invite")
    role: str = Field(..., description="Role to assign to the invited user")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v.strip().lower() not in Roles.__members__.values():
            raise ValueError(
                f"Invalid role: {v}. Must be one of: {', '.join(Roles.__members__.values())}"
            )
        return v.strip().lower()


class UserListResponse(OrmResponseModel):
    """User response schema."""

    id: int = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email address")
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")
    full_name: str | None = Field(..., description="User full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    status: str = Field(UserStatus.PENDING.value, description="User status")

    @model_validator(mode="after")
    def set_computed_fields(self) -> "UserListResponse":
        """Set created"""
        if self.created_at and isinstance(self.created_at, datetime):
            formatted_date = self.created_at.strftime("%d %B %Y")
            if formatted_date[0] == "0":
                formatted_date = formatted_date[1:]
            self.created_at = formatted_date
        return self


class UserStatsResponse(OrmResponseModel):
    """User statistics response schema."""

    total: int = Field(..., description="Total number of users")
    active: int = Field(..., description="Number of users in active status")
    pending: int = Field(..., description="Number of users in pending status")
    blocked: int = Field(..., description="Number of users in blocked status")
    admin: int = Field(..., description="Number of users in admins status")
