import { apiClient } from '@/lib/client';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UpdateProfileRequest {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  confirm_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  confirm_password: string;
}

export interface UserResponse {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  is_profile_verified: boolean;
  role: string | null;
  status: string;
}

export interface LoginResponse {
  access_token?: string;
  token_type?: string;
  message?: string;
  data?: { csrf_token?: string };
}

export interface GenericResponse<T> {
  data: T;
  message?: string;
}

class AuthService {
  /**
   * Login user with email and password
   * Stores the session-bound CSRF token returned by the server.
   */
  async login(credentials: LoginRequest): Promise<GenericResponse<string>> {
    const response = await apiClient.post<GenericResponse<{ message: string; csrf_token: string }>>(
      '/auth/login',
      credentials
    );
    const csrfToken = response.data?.data?.csrf_token;
    if (csrfToken) {
      localStorage.setItem('csrf_token', csrfToken);
    }
    return {
      data: 'Login successful',
    };
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<UserResponse> {
    const response = await apiClient.get<GenericResponse<UserResponse>>('/auth/me');
    return response.data.data;
  }

  /**
   * Refresh access token
   * Refresh token is automatically sent via cookies
   */
  async refreshToken(): Promise<GenericResponse<string>> {
    const response =
      await apiClient.post<GenericResponse<{ message: string; csrf_token: string }>>(
        '/auth/refresh'
      );

    const csrfToken = response.data?.data?.csrf_token;
    if (csrfToken) {
      localStorage.setItem('csrf_token', csrfToken);
    }

    return {
      data: response.data.data?.message || 'Token refreshed',
    };
  }

  /**
   * Logout user
   * Clears HTTP-only cookies on the server and removes local token
   */
  async logout(): Promise<GenericResponse<string>> {
    const response = await apiClient.post<GenericResponse<string>>('/auth/logout');

    // Remove tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('csrf_token');

    return response.data;
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: UpdateProfileRequest): Promise<GenericResponse<string>> {
    const response = await apiClient.put<GenericResponse<string>>('/auth/profile', profileData);
    return response.data;
  }

  /**
   * Verify user profile with token
   */
  async verifyProfile(token: string): Promise<GenericResponse<string>> {
    const response = await apiClient.patch<GenericResponse<string>>(
      `/auth/verify-profile?token=${token}`
    );
    return response.data;
  }

  /**
   * Request password reset
   */
  async forgotPassword(request: ForgotPasswordRequest): Promise<GenericResponse<string>> {
    const response = await apiClient.post<GenericResponse<string>>(
      '/auth/forgot-password',
      request
    );
    return response.data;
  }

  /**
   * Reset password with token
   */
  async resetPassword(request: ResetPasswordRequest): Promise<GenericResponse<string>> {
    const response = await apiClient.post<GenericResponse<string>>('/auth/reset-password', request);
    return response.data;
  }
}

export const authService = new AuthService();
