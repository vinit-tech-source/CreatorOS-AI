import { apiClient } from './client';
import { User, ApiResponse } from '../../types';

export interface UserUpdatePayload {
  full_name?: string;
  username?: string;
  region?: string | null;
  country?: string | null;
}

export const userService = {
  /**
   * Get current authenticated user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<ApiResponse<User>>('/auth/me');
    return response.data.data!;
  },

  /**
   * Update current user profile / region / country preferences
   */
  async updateCurrentUser(payload: UserUpdatePayload): Promise<User> {
    const response = await apiClient.patch<ApiResponse<User>>('/auth/me', payload);
    return response.data.data!;
  },
};
