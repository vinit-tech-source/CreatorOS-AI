import { apiClient } from './client';
import { Project, SocialAccount, AnalyticsSummary, Post } from '../../types';

export interface DashboardData {
  totalProjects: number | null;
  totalPosts: number | null;
  publishedPosts: number | null;
  scheduledPostsCount: number | null;
  connectedAccounts: number | null;
  analyticsSummary: AnalyticsSummary | null;
  recentPosts: Post[];
  upcomingScheduledPosts: Post[];
  accounts: SocialAccount[];
}

export const dashboardService = {
  fetchDashboardData: async (workspaceId: string): Promise<DashboardData> => {
    try {
      // 1. Fetch projects, social accounts, and analytics summary concurrently
      const [projectsRes, accountsRes, analyticsRes] = await Promise.all([
        apiClient.get(`/workspaces/${workspaceId}/projects`),
        apiClient.get(`/workspaces/${workspaceId}/social-accounts`),
        apiClient.get(`/workspaces/${workspaceId}/analytics/summary`).catch(() => ({ data: { success: false, data: null } })) // allow failure if no analytics
      ]);

      const projects: Project[] = projectsRes.data.success ? projectsRes.data.data : [];
      const accounts: SocialAccount[] = accountsRes.data.success ? accountsRes.data.data : [];
      const analyticsSummary: AnalyticsSummary | null = analyticsRes.data.success ? analyticsRes.data.data : null;

      // 2. Fetch all posts for all projects concurrently
      const postPromises = projects.map(project => 
        apiClient.get(`/projects/${project.id}/posts`)
          .then(res => res.data.success ? res.data.data as Post[] : [])
          .catch(() => [] as Post[])
      );

      const projectPostsArrays = await Promise.all(postPromises);
      
      // Flatten arrays
      const allPosts: Post[] = projectPostsArrays.flat();

      // 3. Aggregate data
      const totalProjects = projects.length;
      const totalPosts = allPosts.length;
      const publishedPosts = allPosts.filter(p => p.status === 'PUBLISHED').length;
      const scheduledPostsCount = allPosts.filter(p => p.status === 'SCHEDULED').length;
      const connectedAccounts = accounts.filter(a => a.is_active).length;

      // Sort recent posts by updated_at desc
      const recentPosts = [...allPosts]
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, 5);

      // Sort upcoming scheduled posts by scheduled_for asc
      const upcomingScheduledPosts = [...allPosts]
        .filter(p => p.status === 'SCHEDULED' && p.scheduled_for)
        .sort((a, b) => new Date(a.scheduled_for!).getTime() - new Date(b.scheduled_for!).getTime())
        .slice(0, 5);

      return {
        totalProjects,
        totalPosts,
        publishedPosts,
        scheduledPostsCount,
        connectedAccounts,
        analyticsSummary,
        recentPosts,
        upcomingScheduledPosts,
        accounts
      };
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      throw new Error("Failed to fetch dashboard data");
    }
  }
};
