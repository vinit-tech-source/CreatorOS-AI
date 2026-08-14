import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Dashboard } from '../src/pages/dashboard/Dashboard';
import { useWorkspaceStore } from '../src/stores/workspaceStore';
import { dashboardService } from '../src/services/api/dashboardService';

vi.mock('../src/services/api/dashboardService', () => ({
  dashboardService: {
    fetchDashboardData: vi.fn()
  }
}));

const renderDashboard = () => {
  return render(
    <BrowserRouter>
      <Dashboard />
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWorkspaceStore.setState({
      workspaces: [],
      activeWorkspace: null,
      isLoading: false,
    });
  });

  it('shows loading state when workspace is loading', () => {
    useWorkspaceStore.setState({ isLoading: true });
    renderDashboard();
    expect(screen.getByText('Loading workspaces...')).toBeInTheDocument();
  });

  it('shows empty state when no workspace is selected', () => {
    renderDashboard();
    expect(screen.getByText('No workspace selected or available.')).toBeInTheDocument();
  });

  it('renders dashboard data when workspace is active', async () => {
    useWorkspaceStore.setState({
      activeWorkspace: { id: 'ws-1', name: 'Test Workspace', slug: 'test', owner_id: '1', created_at: '', updated_at: '' }
    });

    const mockData = {
      totalProjects: 5,
      totalPosts: 10,
      publishedPosts: 2,
      scheduledPostsCount: 1,
      connectedAccounts: 3,
      analyticsSummary: { total_impressions: 1000 },
      recentPosts: [],
      upcomingScheduledPosts: [],
      accounts: []
    };

    (dashboardService.fetchDashboardData as any).mockResolvedValue(mockData);

    renderDashboard();

    // First it shows loading data
    expect(screen.getByText('Loading dashboard data...')).toBeInTheDocument();

    // Then it renders the data
    await waitFor(() => {
      expect(screen.getByText('Test Workspace', { exact: false })).toBeInTheDocument();
      expect(screen.getByText('Total Projects')).toBeInTheDocument();
      // Values are hard to test perfectly by text due to DOM nesting, but we can check if they exist
      expect(screen.getByText('5')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
    });
  });

  it('shows error state when fetching fails', async () => {
    useWorkspaceStore.setState({
      activeWorkspace: { id: 'ws-1', name: 'Test Workspace', slug: 'test', owner_id: '1', created_at: '', updated_at: '' }
    });

    (dashboardService.fetchDashboardData as any).mockRejectedValue(new Error('API failed'));

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText('API failed')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });
});
