import type {
  GenericResponse,
  PaginatedResponse,
  PaginationMetadata,
  UserProfile,
} from '../types/types';
import { apiClient, getErrorMessage } from '@/lib/client';
import { SETUP_ROUTES } from '@/constants/routes.constants';
import { DEFAULT_PAGE_SIZE } from '@/constants/pagination.constants';
import {
  UserListFilterParams,
  UserListItem,
  UserListResponse,
  UserStatsResponse,
} from '@/types/user.type';
import { mapPaginatedResponse } from '@/mappers/common.mapper';
import { mapUserListResponse } from '@/mappers/user.mapper';

const STORAGE_KEY = 'ocr_user_profile';

const defaultProfile: UserProfile = {
  id: '1',
  fullName: 'Demo',
  email: 'demo@gmail.com',
  company: 'Acme Inc.',
  phoneNumber: '+1 (555) 000-0000',
  accountStatus: 'Active',
  memberSince: new Date('2026-02-06'),
  plan: 'Professional',
  passwordLastChanged: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
  twoFactorEnabled: false,
};

export const getUserProfile = (): UserProfile => {
  const stored = sessionStorage.getItem(STORAGE_KEY);
  if (stored) {
    const parsed = JSON.parse(stored);
    return {
      ...parsed,
      memberSince: new Date(parsed.memberSince),
      passwordLastChanged: parsed.passwordLastChanged ? new Date(parsed.passwordLastChanged) : null,
    };
  }

  // Initialize with default profile
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(defaultProfile));
  return defaultProfile;
};

export const updateUserProfile = (profile: UserProfile): UserProfile => {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  return profile;
};

export const changePassword = (_currentPassword: string, _newPassword: string): boolean => {
  // In a real application, this would validate against a backend
  // For now, we just update the passwordLastChanged timestamp
  const profile = getUserProfile();
  profile.passwordLastChanged = new Date();
  updateUserProfile(profile);
  return true;
};

// Send verification email via API
export const sendVerificationEmail = async (email: string): Promise<boolean> => {
  try {
    const response = await apiClient.post(SETUP_ROUTES.SEND_VERIFICATION_EMAIL, { email });
    return response.status === 200;
  } catch (error) {
    console.error('Failed to send verification email:', error);
    throw error;
  }
};

// Verify user's new password and update profile via API
export const verifyAndChangePassword = async (
  email: string,
  currentPassword: string,
  newPassword: string,
  firstName: string,
  lastName: string,
  token: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.put(SETUP_ROUTES.VERIFY_AND_CHANGE_PASSWORD, {
      email,
      current_password: currentPassword,
      password: newPassword,
      token: token,
      first_name: firstName,
      last_name: lastName,
    });

    if (response.status === 200) {
      // Update local password timestamp
      const profile = getUserProfile();
      profile.passwordLastChanged = new Date();
      updateUserProfile(profile);

      return {
        success: true,
        message: response.data.message || 'Password changed successfully',
      };
    }

    return {
      success: false,
      message: 'Failed to change password',
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      'Failed to change password. Please try again.';

    return {
      success: false,
      message: errorMessage,
    };
  }
};

export const enableTwoFactor = (): UserProfile => {
  const profile = getUserProfile();
  profile.twoFactorEnabled = true;
  return updateUserProfile(profile);
};

export const disableTwoFactor = (): UserProfile => {
  const profile = getUserProfile();
  profile.twoFactorEnabled = false;
  return updateUserProfile(profile);
};

export interface InviteUserRequest {
  email: string;
  role?: string;
}

export const inviteUser = async (
  userData: InviteUserRequest
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.post('/users/invite', userData);

    return {
      success: true,
      message: response.data.message || 'User Invited Successfully',
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      'Failed to send invite. Please try again.';

    return {
      success: false,
      message: errorMessage,
    };
  }
};

export interface User {
  id: string;
  full_name: string;
  email: string;
  role: 'admin' | 'user' | 'superadmin';
  status: 'active' | 'blocked' | 'pending';
  company?: string;
  created_at?: string;
}

export interface BackendResponse<T = any> {
  data: T;
  metadata: any;
}

export const getUsers = async (
  page: number = 1,
  pageSize: number = DEFAULT_PAGE_SIZE,
  filters?: UserListFilterParams
): Promise<{ data: UserListItem[]; metadata: PaginationMetadata }> => {
  try {
    const response = await apiClient.get<PaginatedResponse<UserListResponse>>('/users/', {
      params: {
        page,
        page_size: pageSize,
        ...(filters?.status ? { status: filters.status } : {}),
        ...(filters?.search ? { search: filters.search } : {}),
      },
    });
    return mapPaginatedResponse(mapUserListResponse)(response.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get user statistics
export const getUserStats = async (): Promise<UserStatsResponse> => {
  try {
    const response = await apiClient.get<GenericResponse<UserStatsResponse>>('/users/stats');
    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

export const deleteUser = async (
  userId: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.delete(`/users/${userId}`);
    return {
      success: true,
      message: response.data.message || 'User deleted successfully',
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      'Failed to delete user. Please try again.';
    return {
      success: false,
      message: errorMessage,
    };
  }
};

export const blockUser = async (userId: string): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.post(`/users/${userId}/block`);
    return {
      success: true,
      message: response.data.message || 'User blocked successfully',
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      'Failed to block user. Please try again.';
    return {
      success: false,
      message: errorMessage,
    };
  }
};

export const unblockUser = async (
  userId: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.post(`/users/${userId}/unblock`);
    return {
      success: true,
      message: response.data.message || 'User unblocked successfully',
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      'Failed to unblock user. Please try again.';
    return {
      success: false,
      message: errorMessage,
    };
  }
};

export const resendVerificationEmail = async (
  userId: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await apiClient.post(`/users/${userId}/resend-verification`);
    return {
      success: true,
      message: response.data.message || 'Verification email sent successfully',
    };
  } catch (error: any) {
    const errorMessage =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      'Failed to send verification email. Please try again.';
    return {
      success: false,
      message: errorMessage,
    };
  }
};
