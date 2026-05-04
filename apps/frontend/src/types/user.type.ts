export enum UserStatus {
  BLOCKED = 'blocked',
  PENDING = 'pending',
  ACTIVE = 'active',
  INACTIVE = 'inactive',
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
}
export interface UserListItem {
  id: number;
  name: string;
  email: string;
  status: UserStatus;
  is_active: boolean;
  full_name: string;
  role: UserRole;
  setup: boolean;
  created_by: number | null;
  created_by_fullname: string | null;
  created_at: string;
}

export interface UserListFilterParams {
  status?: UserStatus | null;
  search?: string;
}

export interface UserListResponse {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  role: UserRole;
  setup: boolean;
  status: UserStatus;
  full_name: string;
  created_by: number | null;
  created_by_fullname: string | null;
  created_at: string;
}

export interface UserStatsResponse {
  total: number;
  active: number;
  blocked: number;
  pending: number;
  admin: number;
}
