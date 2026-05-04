"""Super admin seeder."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserStatus
from app.db.seeders import BaseSeeder, register_seeder
from app.logger import logger
from app.shared.constants.app_constants import Roles
from app.shared.utils.password import hash_password


@register_seeder(order=1)
class SuperAdminSeeder(BaseSeeder):
    """Seeder for creating the super admin user."""

    @property
    def name(self) -> str:
        return "SuperAdminSeeder"

    async def seed(self, session: AsyncSession) -> None:
        """Create super admin user if it doesn't exist."""
        result = await session.execute(select(User).where(User.email == "admin@leapx.com"))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.info(f"{self.name}: Super admin already exists. Skipping.")
            return

        result = await session.scalar(
            select(func.count()).select_from(User).where(User.is_superuser.is_(True))
        )

        if result and result > 0:
            logger.info(f"{self.name}: Super admin already exists. Skipping.")
            return

        hashed_password = hash_password("Admin@123")

        super_admin = User(
            email="admin@docweaver.com",
            password=hashed_password,
            first_name="Super",
            last_name="Admin",
            is_active=True,
            is_superuser=True,
            status=UserStatus.PENDING,
            is_profile_verified=False,
            role=Roles.ADMIN,
        )

        session.add(super_admin)
        await session.flush()
