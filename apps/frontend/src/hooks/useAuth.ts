import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  authService,
  LoginRequest,
  UpdateProfileRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '../services/auth.service.ts';
import { useAuthStore } from '../store/authStore';

/**
 * Custom hook for authentication operations with React Query
 */
export const useAuthOperations = () => {
  const queryClient = useQueryClient();
  const { setUser, logout: logoutStore } = useAuthStore();

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authService.login(credentials),
    onSuccess: async () => {
      // Fetch user data after successful login
      const user = await authService.getCurrentUser();
      setUser(user);
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      logoutStore();
      queryClient.clear();
    },
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (profileData: UpdateProfileRequest) => authService.updateProfile(profileData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  // Verify profile mutation
  const verifyProfileMutation = useMutation({
    mutationFn: (token: string) => authService.verifyProfile(token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });

  // Forgot password mutation
  const forgotPasswordMutation = useMutation({
    mutationFn: (request: ForgotPasswordRequest) => authService.forgotPassword(request),
  });

  // Reset password mutation
  const resetPasswordMutation = useMutation({
    mutationFn: (request: ResetPasswordRequest) => authService.resetPassword(request),
  });

  return {
    login: loginMutation,
    logout: logoutMutation,
    updateProfile: updateProfileMutation,
    verifyProfile: verifyProfileMutation,
    forgotPassword: forgotPasswordMutation,
    resetPassword: resetPasswordMutation,
  };
};

/**
 * Hook to fetch current user
 */
export const useCurrentUser = (enabled = true) => {
  const { setUser } = useAuthStore();

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const user = await authService.getCurrentUser();
      setUser(user);
      return user;
    },
    enabled,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
