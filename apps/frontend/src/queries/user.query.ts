import { useMutation, useQuery, useQueryClient, QueryClient } from '@tanstack/react-query';
import {
  getUsers,
  deleteUser,
  blockUser,
  unblockUser,
  inviteUser,
  resendVerificationEmail,
  getUserProfile,
  updateUserProfile,
  getUserStats,
} from '@/services/user.service';
import type { InviteUserRequest } from '@/services/user.service';

// Query keys for users
export const userKeys = {
  all: ['users'] as const,

  lists: () => [...userKeys.all, 'list'] as const,

  list: (page: number, pageSize: number, filters: Record<string, any> = {}) =>
    [...userKeys.lists(), page, pageSize, JSON.stringify(filters)] as const,

  details: () => [...userKeys.all, 'detail'] as const,

  detail: (id: string) => [...userKeys.details(), id] as const,

  stats: () => [...userKeys.all, 'stats'] as const,
};

export const useGetUsers = (page = 1, pageSize = 25, filters: Record<string, any> = {}) => {
  return useQuery({
    queryKey: userKeys.list(page, pageSize, filters),
    queryFn: () => getUsers(page, pageSize, filters),
    staleTime: 30 * 1000,
  });
};

/**
 * User Statistics
 */
export const useGetUserStats = () => {
  return useQuery({
    queryKey: userKeys.stats(),
    queryFn: getUserStats,
  });
};

const invalidateUserCaches = async (queryClient: QueryClient) => {
  await queryClient.invalidateQueries({
    queryKey: userKeys.lists(),
  });

  await queryClient.invalidateQueries({
    queryKey: userKeys.stats(),
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => deleteUser(userId),

    onSuccess: async () => {
      await invalidateUserCaches(queryClient);
    },
  });
};

export const useBlockUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => blockUser(userId),

    onSuccess: async () => {
      await invalidateUserCaches(queryClient);
    },
  });
};

export const useUnblockUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => unblockUser(userId),

    onSuccess: async () => {
      await invalidateUserCaches(queryClient);
    },
  });
};

export const useInviteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: InviteUserRequest) => inviteUser(request),

    onSuccess: async () => {
      await invalidateUserCaches(queryClient);
    },
  });
};

/**
 * Resend verification email (no cache invalidation needed)
 */
export const useResendVerificationEmail = () => {
  return useMutation({
    mutationFn: (userId: string) => resendVerificationEmail(userId),
  });
};

export const useUserProfile = () => {
  return {
    get: getUserProfile,
    update: updateUserProfile,
  };
};
