import { createContext, useContext, ReactNode, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { LoginRequest } from '@/services/auth.service.ts';

export interface User {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  is_profile_verified: boolean;
  role: string | null;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isProfileSetup: boolean;
  isProfileVerified: boolean;
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const {
    user,
    isAuthenticated,
    isProfileSetup,
    isProfileVerified,
    isLoading,
    error,
    login: loginStore,
    logout: logoutStore,
    fetchUser,
    clearError,
  } = useAuthStore();

  // Fetch user on mount if authenticated
  useEffect(() => {
    if (isAuthenticated && !user) {
      fetchUser().catch(() => {
        // If fetch fails, user will be logged out automatically
      });
    }
  }, [isAuthenticated, user, fetchUser]);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const credentials: LoginRequest = { email, password };
      await loginStore(credentials);
      return true;
    } catch (_) {
      // Error is already set in the store, just return false
      // Don't clear the error here so it can be displayed
      return false;
    }
  };

  const logout = async () => {
    await logoutStore();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated,
        isProfileVerified,
        isProfileSetup,
        isLoading,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
