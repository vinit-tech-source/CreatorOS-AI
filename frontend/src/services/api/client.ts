import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../../stores/authStore';

// Assuming backend runs on 8000 by default in development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request Interceptor: Attach token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401s
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // Skip retry for auth endpoints — they legitimately return 401 on bad
    // credentials; retrying with a refresh token would be wrong and leaks
    // "No refresh token" into the login form's error state.
    const isAuthEndpoint = originalRequest?.url?.includes('/auth/');

    // If error is 401 and we haven't already retried
    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry && !isAuthEndpoint) {
      (originalRequest as any)._retry = true;

      // ── Dev bypass: re-fetch the dev token instead of a normal refresh ──
      // Import lazily to keep the production bundle unaffected.
      if (import.meta.env.DEV && import.meta.env.VITE_DEV_AUTH_BYPASS === 'true') {
        try {
          const { initDevAuth } = await import('../../lib/devAuth');
          await initDevAuth();
          const newToken = useAuthStore.getState().accessToken;
          if (newToken && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
          }
          return apiClient(originalRequest);
        } catch {
          useAuthStore.getState().logout();
          return Promise.reject(error);
        }
      }

      // ── Normal refresh flow ──
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        useAuthStore.getState().setAuth(
          useAuthStore.getState().user!,
          data.data.access_token
        );

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${data.data.access_token}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
