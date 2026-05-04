import { UserListItem, UserListResponse, UserRole, UserStatus } from '@/types/user.type';
import { formatDate } from '@/utils';

export const mapUserListResponse = (user: UserListResponse): UserListItem => {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    status: user.status as UserStatus,
    is_active: user.is_active,
    full_name: user.full_name,
    role: user.role as UserRole,
    setup: user.setup,
    created_by: user.created_by,
    created_by_fullname: user.created_by_fullname,
    created_at: formatDate(user.created_at),
  };
};
