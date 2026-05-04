from datetime import datetime

from app.config.settings import Settings
from app.core.common.schema import PaginationParams
from app.core.common.service import BaseService
from app.core.users.repository import UserRepository
from app.core.users.schemas import (
    UserInviteRequest,
    UserListResponse,
    UserStatsResponse,
)
from app.db.models import User, UserStatus
from app.providers.email.base import EmailProvider
from app.shared.constants.app_constants import RolesClass
from app.shared.exceptions.common import BadRequestException
from app.shared.exceptions.user_exceptions import (
    InsufficientPermissionsError,
    UserNotFoundError,
)
from app.shared.utils.password import generate_password, hash_password

ACTION_MIN_ROLE: dict[str, str] = {
    "list users": RolesClass.ADMIN,
    "get user": RolesClass.ADMIN,
    "invite new users": RolesClass.ADMIN,
    "resend invite": RolesClass.ADMIN,
    "block users": RolesClass.ADMIN,
    "unblock users": RolesClass.ADMIN,
    "toggle user status": RolesClass.ADMIN,
    "delete": RolesClass.ADMIN,
    "get stats": RolesClass.ADMIN,
}

REQUIRES_HIGHER_RANK: set[str] = {
    "delete",
    "toggle user status",
    "block users",
    "unblock_users",
}


class UserService(BaseService):
    """Service for user-related business logic."""

    def __init__(
        self,
        repository: UserRepository,
        settings: Settings,
        email_provider: EmailProvider,
    ):
        super().__init__()
        self.repository = repository
        self.settings = settings
        self.email_provider = email_provider

    async def get_all_users(self, user: User, params: PaginationParams):
        self._validate_permission(actor=user, action="list users")
        users, meta = await self.repository.get_all_users(params)
        return [UserListResponse.model_validate(u) for u in users], meta

    async def get_user(self, user_id: int, current_user: User) -> UserListResponse:
        self._validate_permission(actor=current_user, action="get user")
        user = await self._get_user_or_raise(user_id)
        return UserListResponse.model_validate(user)

    async def delete_user(self, user_id: int, current_user: User) -> None:
        target = await self._get_user_or_raise(user_id)
        self._validate_permission(actor=current_user, action="delete", target=target)
        self._validate_not_self_operation(current_user.id, user_id, "delete")
        await self.repository.delete_user(user_id)

    async def change_status(
        self, user_id: int, current_user: User, status: bool
    ) -> None:
        target = await self._get_user_or_raise(user_id)
        self._validate_permission(
            actor=current_user, action="block users", target=target
        )
        self._validate_not_self_operation(current_user.id, user_id, "change status")
        await self.repository.change_status(user_id, status=status)

    async def toggle_user_status(self, user_id: int, current_user: User):
        target = await self._get_user_or_raise(user_id)
        self._validate_permission(
            actor=current_user, action="toggle user status", target=target
        )
        self._validate_not_self_operation(current_user.id, user_id, "toggle status")
        await self.repository.toggle_user_status(user_id)

    async def resend_invite(self, user_id: int, user: User):
        self._validate_permission(actor=user, action="resend invite")
        user_instance = await self._get_user_or_raise(user_id)
        password = generate_password()
        current_year = datetime.now().year
        await self.repository.update_password(user_id, hash_password(password))
        await self.email_provider.send_templated_email(
            to_email=user_instance.email,
            subject="Welcome! Your Account Has Been Created",
            template_name="user_invite.html",
            template_data={
                "user_email": user_instance.email,
                "password": password,
                "login_url": f"{self.settings.frontend_url}/login",
                "current_year": current_year,
            },
        )

    async def invite_user(self, request: UserInviteRequest, user: User):
        self._validate_permission(actor=user, action="invite new users")
        if await self.repository.user_exists(request.email):
            raise BadRequestException("User with this email already exists")

        password = generate_password()
        current_year = datetime.now().year
        await self.repository.create_user(
            {
                "email": request.email,
                "password": hash_password(password),
                "is_active": True,
                "role": request.role,
                "is_profile_verified": True,
                "status": UserStatus.PENDING,
            }
        )
        await self.email_provider.send_templated_email(
            to_email=request.email,
            subject="Welcome! Your Account Has Been Created",
            template_name="user_invite.html",
            template_data={
                "user_email": request.email,
                "password": password,
                "login_url": f"{self.settings.frontend_url}/login",
                "current_year": current_year,
            },
        )

    def _validate_permission(
        self,
        actor: User,
        action: str,
        target: User | None = None,
    ) -> None:
        """ """
        min_role = ACTION_MIN_ROLE.get(action)
        if min_role is None:
            raise InsufficientPermissionsError(f"Unknown action: '{action}'")
        actor_rank = (
            RolesClass.rank("superadmin")
            if actor.is_superuser
            else RolesClass.rank(actor.role)
        )
        required_rank = RolesClass.rank(min_role)

        if actor_rank < required_rank:
            raise InsufficientPermissionsError

        if target is not None and action in REQUIRES_HIGHER_RANK:
            target_rank = (
                RolesClass.rank("superadmin")
                if target.is_superuser
                else RolesClass.rank(target.role)
            )
            if actor_rank <= target_rank:
                raise InsufficientPermissionsError

    def _validate_not_self_operation(
        self, current_user_id: int, target_user_id: int, action: str
    ) -> None:
        if current_user_id == target_user_id:
            raise BadRequestException(f"Cannot {action} your own account.")

    async def _get_user_or_raise(self, user_id: int) -> User:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_stats(self) -> UserStatsResponse:
        """Get task statistics."""
        stats = await self.repository.get_stats()
        return UserStatsResponse(**stats)
