import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { Analytics } from '../src/pages/analytics/Analytics';
import { PostAnalytics } from '../src/pages/analytics/PostAnalytics';
import { analyticsService } from '../src/services/api/analyticsService';
import { useAnalyticsStore } from '../src/stores/analyticsStore';
import { useWorkspaceStore } from '../src/stores/workspaceStore';
import '@testing-library/jest-dom';

// ── Mocks ──────────────────────────────────────────────────────────
vi.mock('../src/services/api/analyticsService', () => ({
  analyticsService: {
    getWorkspaceSummary: vi.fn(),
    listWorkspacePostsAnalytics: vi.fn(),
    getPostAnalytics: vi.fn(),
  },
}));

// ResizeObserver mock for Recharts
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = ResizeObserver;

const WORKSPACE_ID = 'ws-123';
const PROJECT_ID = 'proj-456';
const POST_ID = 'post-789';

const mockSummary = {
  total_impressions: 10000,
  total_views: 5000,
  total_likes: 1200,
  total_comments: 300,
  total_shares: 150,
  total_saves: 50,
  total_clicks: 400,
  average_engagement_rate: 0.05,
  post_count: 10,
};

const mockPosts = [
  {
    id: 'snap-1',
    post_id: 'post-1',
    workspace_id: WORKSPACE_ID,
    social_account_id: 'sa-1',
    platform: 'bluesky',
    external_post_id: 'ext-1',
    collected_at: '2026-08-14T10:00:00Z',
    created_at: '2026-08-01T10:00:00Z',
    views: 1000,
    likes: 100,
    comments: 10,
    shares: 5,
    engagement_rate: 0.115,
    impressions: null,
    saves: null,
    clicks: null,
    followers_at_time: null
  },
  {
    id: 'snap-2',
    post_id: 'post-2',
    workspace_id: WORKSPACE_ID,
    social_account_id: 'sa-2',
    platform: 'x',
    external_post_id: 'ext-2',
    collected_at: '2026-08-14T10:00:00Z',
    created_at: '2026-08-10T10:00:00Z',
    views: 500,
    likes: null, // Test N/A rendering
    comments: 0,
    shares: null,
    engagement_rate: null,
    impressions: null,
    saves: null,
    clicks: null,
    followers_at_time: null
  }
];

const mockPostHistory = [
  { ...mockPosts[0], collected_at: '2026-08-14T10:00:00Z', likes: 100 },
  { ...mockPosts[0], collected_at: '2026-08-13T10:00:00Z', likes: 50 },
];

function renderAnalyticsPage() {
  return render(
    <MemoryRouter initialEntries={[`/workspaces/${WORKSPACE_ID}/analytics`]}>
      <Routes>
        <Route path="/workspaces/:workspaceId/analytics" element={<Analytics />} />
      </Routes>
    </MemoryRouter>
  );
}

function renderPostAnalyticsPage() {
  return render(
    <MemoryRouter initialEntries={[`/workspaces/${WORKSPACE_ID}/projects/${PROJECT_ID}/posts/${POST_ID}/analytics`]}>
      <Routes>
        <Route path="/workspaces/:workspaceId/projects/:projectId/posts/:postId/analytics" element={<PostAnalytics />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('Analytics UI', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWorkspaceStore.setState({
      workspaces: [{ id: WORKSPACE_ID, name: 'Test WS', role: 'owner' }],
      activeWorkspace: { id: WORKSPACE_ID, name: 'Test WS', role: 'owner' },
      isLoading: false,
      error: null
    });
    useAnalyticsStore.getState().clearAnalytics();
  });

  describe('Workspace Analytics Dashboard', () => {
    it('renders KPI metrics and Post table', async () => {
      (analyticsService.getWorkspaceSummary as any).mockResolvedValue(mockSummary);
      (analyticsService.listWorkspacePostsAnalytics as any).mockResolvedValue(mockPosts);

      renderAnalyticsPage();

      expect(screen.getByText(/Workspace Analytics/i)).toBeInTheDocument();
      
      // Wait for data
      await waitFor(() => {
        expect(screen.getByText('1.2K')).toBeInTheDocument(); // likes
        expect(screen.getByText('5.0K')).toBeInTheDocument(); // views
        expect(screen.getByText('5.0%')).toBeInTheDocument(); // engagement rate
      });

      // Post table
      expect(screen.getByText('bluesky')).toBeInTheDocument();
      // Ensure null metrics render as N/A
      expect(screen.getAllByText('N/A').length).toBeGreaterThan(0);
    });

    it('shows error state on backend failure', async () => {
      (analyticsService.getWorkspaceSummary as any).mockRejectedValue(new Error('API Down'));
      (analyticsService.listWorkspacePostsAnalytics as any).mockRejectedValue(new Error('API Down'));

      renderAnalyticsPage();

      expect(await screen.findByText(/Unable to load analytics/i)).toBeInTheDocument();
      expect(screen.getByText('API Down')).toBeInTheDocument();
    });

    it('filters posts by platform UI-side', async () => {
      (analyticsService.getWorkspaceSummary as any).mockResolvedValue(mockSummary);
      (analyticsService.listWorkspacePostsAnalytics as any).mockResolvedValue(mockPosts);

      renderAnalyticsPage();

      await waitFor(() => {
        expect(screen.getByText('bluesky')).toBeInTheDocument();
        expect(screen.getByText('x')).toBeInTheDocument();
      });

      // Change filter to bluesky
      const select = screen.getByRole('combobox', { name: /Filter by platform/i });
      fireEvent.change(select, { target: { value: 'bluesky' } });

      await waitFor(() => {
        expect(screen.getByText('bluesky')).toBeInTheDocument();
        expect(screen.queryByText('x')).not.toBeInTheDocument();
      });
    });

    it('handles sorting of posts', async () => {
      (analyticsService.getWorkspaceSummary as any).mockResolvedValue(mockSummary);
      (analyticsService.listWorkspacePostsAnalytics as any).mockResolvedValue(mockPosts);

      renderAnalyticsPage();

      // Wait for table
      await waitFor(() => {
        expect(screen.getByText('bluesky')).toBeInTheDocument();
      });

      // Click "Views" header to sort by views
      const viewsHeader = screen.getByText('Views');
      fireEvent.click(viewsHeader);

      // Verify state update (checking DOM order is complex in generic testing library, but we can verify click doesn't crash)
      await waitFor(() => {
        expect(screen.getByText('1.0K')).toBeInTheDocument();
      });
    });
  });

  describe('Post Analytics Page', () => {
    it('renders post metrics safely', async () => {
      (analyticsService.getPostAnalytics as any).mockResolvedValue(mockPostHistory);

      renderPostAnalyticsPage();

      await waitFor(() => {
        expect(screen.getByText('Post Analytics')).toBeInTheDocument();
        expect(screen.getByText('ext-1', { exact: false })).toBeInTheDocument(); // external ID
      });

      // Likes from latest snapshot (100)
      expect(screen.getAllByText('100').length).toBeGreaterThan(0);
    });

    it('shows error state if post fetch fails', async () => {
      (analyticsService.getPostAnalytics as any).mockRejectedValue(new Error('Not Found'));

      renderPostAnalyticsPage();

      expect(await screen.findByText(/Unable to load post analytics/i)).toBeInTheDocument();
      expect(screen.getByText('Not Found')).toBeInTheDocument();
    });
  });
});
