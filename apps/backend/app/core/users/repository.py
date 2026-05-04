"""User repository for database operations."""

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.repository import BaseRepository
from app.core.common.schema import (
    DataResultStatus,
    PaginationMetadata,
    PaginationParams,
)
from app.db.models import User, UserStatus


class UserRepository(BaseRepository):
    """Repository for user-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        # Ensure user_id is an integer to avoid SQL type mismatch when callers pass strings
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None

        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """Block a user by ID."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.soft_delete(user_id)
            user.is_active = False
            self.session.add(user)
            await self.session.flush()
            return True
        return False

    async def change_status(self, user_id: int, status: bool) -> bool:
        """Change user status ID."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.status = status
            await self.session.commit()
            await self.session.refresh(user)
            return True
        return False

    async def update_password(self, user_id: int, password: str) -> bool:
        """Change user password."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.password = password
            await self.session.flush()
            return True
        return False

    async def toggle_user_status(self, user_id: int) -> User | None:
        """Toggle user active status."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = not user.is_active
            await self.session.commit()
            await self.session.refresh(user)
            return user
        return None

    async def user_exists(self, email: str) -> bool:
        """Check if user exists by email."""
        user = await self.get_user_by_email(email)
        return user is not None

    async def get_all_users(
        self, params: PaginationParams
    ) -> tuple[list[User], PaginationMetadata]:
        stmt = select(User).filter(User.is_active).filter(~User.is_superuser)

        stmt = stmt.order_by(User.id.desc())
        if params.search:
            pattern = f"{params.search}%"
            full_name = func.concat(User.first_name, " ", User.last_name)
            stmt = stmt.filter(
                full_name.ilike(pattern)
                | User.email.ilike(pattern)
                | User.last_name.ilike(pattern)
                | User.first_name.ilike(pattern)
            )

        if params.status and params.status != DataResultStatus.all:
            status_map = {
                DataResultStatus.active: UserStatus.ACTIVE,
                DataResultStatus.inactive: UserStatus.INACTIVE,
                UserStatus.BLOCKED: UserStatus.BLOCKED,
                UserStatus.PENDING: UserStatus.PENDING,
            }
            user_status = status_map.get(params.status)
            if user_status:
                stmt = stmt.filter(User.status == user_status)
        users, meta = await self.paginate(self.session, stmt, params)
        return users, meta

    async def get_stats(self) -> tuple[int, int, int, int]:
        stmt = select(
            func.count(User.id).label("total"),
            func.sum(case((User.status == UserStatus.ACTIVE, 1), else_=0)).label(
                "active"
            ),
            func.sum(case(((User.role == "admin") & (~User.is_superuser), 1), else_=0)).label("admin"),
            func.sum(case((User.status == UserStatus.BLOCKED, 1), else_=0)).label(
                "blocked"
            ),
            func.sum(case((User.status == UserStatus.PENDING, 1), else_=0)).label(
                "pending"
            ),
            func.sum(case((User.is_profile_verified, 1), else_=0)).label("verified"),
        ).filter(~User.is_superuser)

        result = await self.session.execute(stmt)
        row = result.one()

        return {
            "total": row.total,
            "active": row.active,
            "admin": row.admin,
            "blocked": row.blocked,
            "pending": row.pending,
            "verified": row.verified,
        }
