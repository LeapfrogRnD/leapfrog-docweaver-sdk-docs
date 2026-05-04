import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/authStore';

// Get API base URL from environment variable (Vite). Normalize to avoid double '/api'.
const RAW_API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';
const API_BASE_HOST = RAW_API_BASE.replace(/\/$/, '');
export const API_BASE_URL = API_BASE_HOST.endsWith('/api') ? API_BASE_HOST : API_BASE_HOST + '/api';

const STATE_CHANGING_METHODS = new Set(['post', 'put', 'patch', 'delete']);

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important: This enables sending cookies with requests
});

// Request interceptor - Add Bearer token and CSRF token if present
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Try to get token from localStorage (for Bearer token auth)
    const token = localStorage.getItem('access_token');
    const _csrfToken = getCsrfToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Attach CSRF token for every state-changing request
    if (
      config.method &&
      STATE_CHANGING_METHODS.has(config.method.toLowerCase()) &&
      _csrfToken &&
      config.headers
    ) {
      config.headers['X-CSRF-Token'] = _csrfToken;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle token refresh and errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },

  async (error: AxiosError<{ error_code?: string }>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const refresh_error_codes: string[] = [
      'ERR_INVALID_TOKEN',
      'ERR_TOKEN_EXPIRED',
      'ERR_TOKEN_NOT_FOUND',
    ];

    // Check if the failing request is the refresh endpoint itself
    const isRefreshEndpoint = originalRequest.url?.includes('/auth/refresh');

    const shouldRefresh =
      !originalRequest._retry &&
      !isRefreshEndpoint &&
      ((error.response?.status === 401 &&
        error.response?.data?.error_code &&
        refresh_error_codes.includes(error.response.data.error_code)) ||
        (error.response?.status === 403 &&
          error.response?.data?.error_code === 'ERR_CSRF_TOKEN_INVALID')); // CSRF cookie expired — refresh rotates a new one

    if (shouldRefresh) {
      originalRequest._retry = true;
      try {
        // Attempt to refresh the token via HTTP-only cookie.
        // /auth/refresh is CSRF-exempt so this works even when the CSRF cookie has expired.
        const refreshResponse = await axios.post<{ data?: { csrf_token?: string } }>(
          `${API_BASE_URL}/auth/refresh`,
          {},
          {
            withCredentials: true,
          }
        );

        const newCsrfToken = refreshResponse.data?.data?.csrf_token;
        if (newCsrfToken) {
          localStorage.setItem('csrf_token', newCsrfToken);
          // Also propagate to the retry request header
          if (originalRequest.headers) {
            originalRequest.headers['X-CSRF-Token'] = newCsrfToken;
          }
        }

        // Retry the original request
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Clear auth state and token before redirecting
        useAuthStore.getState().setUser(null);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // If refresh endpoint fails, redirect to login
    if (isRefreshEndpoint && (error.response?.status === 401 || error.response?.status === 403)) {
      // Clear auth state and token before redirecting
      useAuthStore.getState().setUser(null);
      window.location.href = '/login';
    }

    // Handle other errors
    return Promise.reject(error);
  }
);

// Helper function to extract error messages
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.message || error.response?.data?.detail || error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

const getCsrfToken = () => {
  return localStorage.getItem('csrf_token');
};
