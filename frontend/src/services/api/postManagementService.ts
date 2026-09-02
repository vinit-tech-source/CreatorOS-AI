import { apiClient } from './client';
import { Post } from '../../types';

export const postManagementService = {
  createPost: async (projectId: string, data: any): Promise<Post> => {
    const response = await apiClient.post(`/projects/${projectId}/posts`, data);
    return response.data.data;
  },

  getPosts: async (projectId: string): Promise<Post[]> => {
    const response = await apiClient.get(`/projects/${projectId}/posts`);
    return response.data.data;
  },

  getPost: async (projectId: string, postId: string): Promise<Post> => {
    const response = await apiClient.get(`/projects/${projectId}/posts/${postId}`);
    return response.data.data;
  },

  updatePost: async (projectId: string, postId: string, data: Partial<Post>): Promise<Post> => {
    const response = await apiClient.patch(`/projects/${projectId}/posts/${postId}`, data);
    return response.data.data;
  },

  submitForReview: async (projectId: string, postId: string): Promise<Post> => {
    const response = await apiClient.post(`/projects/${projectId}/posts/${postId}/submit-review`);
    return response.data.data;
  },

  approvePost: async (projectId: string, postId: string): Promise<Post> => {
    const response = await apiClient.post(`/projects/${projectId}/posts/${postId}/approve`);
    return response.data.data;
  },

  rejectPost: async (projectId: string, postId: string, reason: string): Promise<Post> => {
    const response = await apiClient.post(`/projects/${projectId}/posts/${postId}/reject`, {
      rejection_reason: reason
    });
    return response.data.data;
  },

  schedulePost: async (projectId: string, postId: string, date: string, timezone: string): Promise<Post> => {
    const response = await apiClient.post(`/projects/${projectId}/posts/${postId}/schedule`, {
      scheduled_at: date,
      timezone: timezone
    });
    return response.data.data;
  },

  reschedulePost: async (projectId: string, postId: string, date: string, timezone: string): Promise<Post> => {
    const response = await apiClient.patch(`/projects/${projectId}/posts/${postId}/schedule`, {
      scheduled_at: date,
      timezone: timezone
    });
    return response.data.data;
  },

  cancelSchedule: async (projectId: string, postId: string): Promise<Post> => {
    const response = await apiClient.delete(`/projects/${projectId}/posts/${postId}/schedule`);
    return response.data.data;
  },

  deletePost: async (projectId: string, postId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/posts/${postId}`);
  }
};
