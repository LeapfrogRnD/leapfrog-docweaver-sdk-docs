"""Authentication repository for database operations."""

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.repository import BaseRepository
from app.db.models import RefreshToken, User
from app.shared.exceptions.common import BadRequestException


class AuthRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where((User.email == email) & (User.is_active))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def valid_user_token(self, token: str) -> User | None:
        stmt = select(User).where(User.verification_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where((User.id == user_id) & (User.is_active))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_refresh_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, user_id: int, token: str) -> bool:
        stmt = (
            update(RefreshToken)
            .where((RefreshToken.token == token) & (RefreshToken.user_id == user_id))
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def save_password_reset_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> bool:
        """Save password reset token for a user."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                forget_password_token=token,
                forget_password_token_expiry=expires_at,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def get_user_by_reset_token(self, token: str) -> User | None:
        """Get user by password reset token."""
        stmt = select(User).where((User.forget_password_token == token) & (User.is_active))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def clear_password_reset_token(self, user_id: int) -> bool:
        """Clear password reset token after successful reset."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                forget_password_token=None,
                forget_password_token_expiry=None,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password."""
        stmt = update(User).where(User.id == user_id).values(password=hashed_password)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def update_user(self, user_id: int, update_payload: dict) -> User | None:
        stmt = (
            update(User).where(User.id == user_id).values(**update_payload).returning(User)
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            error_text = str(exc.orig) if exc.orig else str(exc)
            if "uq_user_active_email" in error_text:
                raise BadRequestException("Email already in use") from exc
            raise

        return result.scalar_one_or_none()

    async def get_user_by_verification_token(self, token: str) -> User | None:
        stmt = select(User).where(User.verification_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
