/**
 * analyticsStore.ts
 *
 * Zustand store for Analytics state management.
 * Guarantees workspace isolation.
 */
import { create } from 'zustand';
import { AnalyticsSummary, PostAnalyticsResponse } from '../types';
import { analyticsService } from '../services/api/analyticsService';

interface AnalyticsState {
  workspaceSummary: AnalyticsSummary | null;
  workspacePostsAnalytics: PostAnalyticsResponse[];
  
  isLoading: boolean;
  error: string | null;
  loadedWorkspaceId: string | null;

  /** Fetch all analytics for a workspace */
  fetchWorkspaceAnalytics: (workspaceId: string) => Promise<void>;
  
  /** Clear all analytics state (call on workspace change) */
  clearAnalytics: () => void;
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
  workspaceSummary: null,
  workspacePostsAnalytics: [],
  isLoading: false,
  error: null,
  loadedWorkspaceId: null,

  fetchWorkspaceAnalytics: async (workspaceId: string) => {
    // Clear stale data immediately
    set({
      workspaceSummary: null,
      workspacePostsAnalytics: [],
      isLoading: true,
      error: null,
      loadedWorkspaceId: null,
    });

    try {
      const [summary, posts] = await Promise.all([
        analyticsService.getWorkspaceSummary(workspaceId),
        analyticsService.listWorkspacePostsAnalytics(workspaceId),
      ]);

      set({
        workspaceSummary: summary,
        workspacePostsAnalytics: posts,
        isLoading: false,
        loadedWorkspaceId: workspaceId,
      });
    } catch (err: any) {
      const message =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to load analytics. Please try again.';
      set({ error: message, isLoading: false });
    }
  },

  clearAnalytics: () =>
    set({
      workspaceSummary: null,
      workspacePostsAnalytics: [],
      isLoading: false,
      error: null,
      loadedWorkspaceId: null,
    }),
}));
