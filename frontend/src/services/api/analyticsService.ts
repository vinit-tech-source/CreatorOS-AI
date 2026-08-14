/**
 * analyticsService.ts
 *
 * Typed API wrapper for Analytics endpoints.
 */
import { apiClient } from './client';
import { AnalyticsSummary, PostAnalyticsResponse, ApiResponse } from '../../types';

export const analyticsService = {
  /**
   * Fetch aggregated metrics for a workspace.
   */
  getWorkspaceSummary: async (workspaceId: string): Promise<AnalyticsSummary> => {
    const response = await apiClient.get<ApiResponse<AnalyticsSummary>>(
      `/workspaces/${workspaceId}/analytics/summary`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to fetch analytics summary.');
  },

  /**
   * Fetch analytics for all posts in a workspace.
   */
  listWorkspacePostsAnalytics: async (workspaceId: string): Promise<PostAnalyticsResponse[]> => {
    const response = await apiClient.get<ApiResponse<PostAnalyticsResponse[]>>(
      `/workspaces/${workspaceId}/analytics/posts`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to load post analytics.');
  },

  /**
   * Fetch analytics history for a specific post.
   */
  getPostAnalytics: async (projectId: string, postId: string): Promise<PostAnalyticsResponse[]> => {
    const response = await apiClient.get<ApiResponse<PostAnalyticsResponse[]>>(
      `/projects/${projectId}/posts/${postId}/analytics`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to load post analytics history.');
  },
};
