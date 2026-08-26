import { useState, useEffect } from 'react';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { dashboardService, DashboardData } from '../../services/api/dashboardService';
import { KPICards } from './components/KPICards';
import { AnalyticsOverview } from './components/AnalyticsOverview';
import { RecentPosts } from './components/RecentPosts';
import { UpcomingSchedule } from './components/UpcomingSchedule';
import { SocialAccountsSummary } from './components/SocialAccountsSummary';
import { QuickActions } from './components/QuickActions';

import { Loader2, AlertCircle } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import styles from './Dashboard.module.css';

export function Dashboard() {
  const { activeWorkspace, isLoading: isWorkspaceLoading } = useWorkspaceStore();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    if (!activeWorkspace) return;
    
    setIsLoading(true);
    setError(null);
    setData(null); // Clear stale data
    
    try {
      const dashboardData = await dashboardService.fetchDashboardData(activeWorkspace.id);
      setData(dashboardData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [activeWorkspace?.id]);

  if (isWorkspaceLoading) {
    return (
      <div className={styles.loadingContainer}>
        <Loader2 className="spinner" size={32} style={{ marginBottom: '1rem' }} />
        <p>Loading workspaces...</p>
      </div>
    );
  }

  if (!activeWorkspace) {
    return (
      <div className={styles.emptyContainer}>
        <p style={{ marginBottom: '1rem' }}>No workspace selected or available.</p>
        <Button onClick={() => window.location.href = '/workspaces'}>
          Go to Workspaces
        </Button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Command Center</h1>
        <p className={styles.subtitle}>Your content engine is running optimally.</p>
      </div>

      {isLoading ? (
        <div className={styles.loadingContainer}>
          <Loader2 className="spinner" size={32} style={{ marginBottom: '1rem' }} />
          <p>Loading your command center...</p>
        </div>
      ) : error ? (
        <div className={styles.errorContainer}>
          <AlertCircle size={32} style={{ marginBottom: '1rem' }} />
          <p style={{ marginBottom: '1rem' }}>{error}</p>
          <Button variant="outline" onClick={fetchDashboardData}>Retry</Button>
        </div>
      ) : data ? (
        <div className="flex flex-col gap-6">
          {/* 1. Quick Create (The new primary entry point) */}
          <QuickActions />
          
          {/* 2. Today / Content Engine Summary */}
          <KPICards data={data} />
          
          <div className={styles.contentGrid}>
            <div className="flex flex-col gap-6">
              <RecentPosts posts={data.recentPosts} />
              <UpcomingSchedule posts={data.upcomingScheduledPosts} />
            </div>
            <div className="flex flex-col gap-6">
              <AnalyticsOverview data={data} />
              <SocialAccountsSummary accounts={data.accounts} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
