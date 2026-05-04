"""User API routes."""

from fastapi import APIRouter, Depends, Path

from app.api.dependencies.auth import require_roles
from app.api.routes.users.dependencies import UserServiceDep
from app.core.common.schema import (
    GenericListResponse,
    GenericResponse,
    PaginationParams,
)
from app.core.users.schemas import (
    UserInviteRequest,
    UserListResponse,
    UserStatsResponse,
)
from app.db.models import User, UserStatus
from app.shared.constants.app_constants import Roles

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=GenericListResponse[UserListResponse])
async def get_users(
    user_service: UserServiceDep,
    query_params: PaginationParams = Depends(),
    user: User = Depends(require_roles(Roles.ADMIN)),
):
    users, metadata = await user_service.get_all_users(user, query_params)
    return GenericListResponse[UserListResponse](data=users, metadata=metadata)


@router.get("/stats", response_model=GenericResponse[UserStatsResponse])
async def get_user_stats(
    user_service: UserServiceDep,
    _: User = Depends(require_roles(Roles.ADMIN)),
):
    """
    Get task statistics.

    Returns statistics for all users including:
    - Total number of users
    - Number of users in active status
    - Number of users in pending status
    - Number of users in blocked status
    - Number of users in unblocked status
    - Number of users in admins status
    """
    stats = await user_service.get_user_stats()
    return GenericResponse[UserStatsResponse](data=stats)


@router.get("/{user_id}", response_model=GenericResponse[UserListResponse])
async def get_user(
    user_service: UserServiceDep,
    user_id: int = Path(..., description="ID of the user to retrieve"),
    user: User = Depends(require_roles(Roles.ADMIN)),
):
    user_data = await user_service.get_user(user_id, user)
    return GenericResponse[UserListResponse](data=user_data)


@router.post("/invite", response_model=GenericResponse[str])
async def invite_user(
    request: UserInviteRequest,
    user_service: UserServiceDep,
    user: User = Depends(require_roles(Roles.ADMIN)),
):
    await user_service.invite_user(request, user)
    return GenericResponse[str](data="User invited successfully")


@router.post("/{user_id}/resend-verification", response_model=GenericResponse[str])
async def resend_invite(
    user_service: UserServiceDep,
    user_id: int = Path(..., description="User id"),
    user: User = Depends(require_roles(Roles.ADMIN)),
):
    await user_service.resend_invite(user_id, user)
    return GenericResponse[str](data="User invited successfully")


@router.delete("/{user_id}", response_model=GenericResponse[str])
async def delete_user(
    user_service: UserServiceDep,
    user_id: int = Path(..., description="ID of the user to delete"),
    current_user: User = Depends(require_roles(Roles.ADMIN)),
):
    await user_service.delete_user(user_id, current_user)
    return GenericResponse[str](data="User deleted successfully")


@router.post("/{user_id}/block", response_model=GenericResponse[str])
async def block_user(
    user_service: UserServiceDep,
    user_id: int = Path(..., description="ID of the user to block"),
    current_user: User = Depends(require_roles(Roles.ADMIN)),
):
    await user_service.change_status(user_id, current_user, status=UserStatus.BLOCKED)
    return GenericResponse[str](data="User Blocked successfully")


@router.post("/{user_id}/unblock", response_model=GenericResponse[str])
async def unblock_user(
    user_service: UserServiceDep,
    user_id: int = Path(..., description="ID of the user to delete"),
    current_user: User = Depends(require_roles(Roles.ADMIN)),
):
    await user_service.change_status(user_id, current_user, status=UserStatus.ACTIVE)
    return GenericResponse[str](data="User Unblocked successfully")


@router.patch("/{user_id}/toggle-status", response_model=GenericResponse[str])
async def toggle_user_status(
    user_service: UserServiceDep,
    user_id: int = Path(..., description="ID of the user to toggle status"),
    current_user: User = Depends(require_roles(Roles.ADMIN)),
):
    await user_service.toggle_user_status(user_id, current_user)
    return GenericResponse[str](data="User status toggled successfully")
