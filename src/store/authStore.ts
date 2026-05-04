import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService, UserResponse, LoginRequest } from '@/services/auth.service.ts';

interface AuthState {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isProfileSetup: boolean;
  isProfileVerified: boolean;
  isLoading: boolean;
  error: string | null;
  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  clearError: () => void;
  setUser: (user: UserResponse | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      isProfileSetup: false,
      isProfileVerified: false,
      error: null,

      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          await authService.login(credentials);
          // After successful login, fetch user data
          const user = await authService.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isProfileSetup: user.status != 'pending',
            isProfileVerified: user.is_profile_verified,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          // Extract error message from backend response
          const errorMessage =
            error.response?.data?.message ||
            error.response?.data?.detail ||
            error.message ||
            'Login failed';
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true, error: null });
        try {
          await authService.logout();
          localStorage.removeItem('access_token');
          set({
            user: null,
            isAuthenticated: false,
            isProfileVerified: false,
            isProfileSetup: false,
            isLoading: false,
            error: null,
          });
        } catch (_: any) {
          localStorage.removeItem('access_token');
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      fetchUser: async () => {
        set({ isLoading: true, error: null });
        try {
          const user = await authService.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isProfileSetup: user.status !== 'pending',
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const errorMessage =
            error.response?.data?.detail || error.message || 'Failed to fetch user';
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
            user: null,
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),

      setUser: (user: UserResponse | null) =>
        set({ user, isAuthenticated: !!user, isProfileSetup: user?.status !== 'pending' }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        isProfileVerified: state.isProfileVerified,
        isProfileSetup: state.isProfileSetup,
      }),
    }
  )
);
