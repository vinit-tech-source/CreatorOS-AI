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
      <div className="flex flex-col items-center justify-center h-full text-secondary">
        <Loader2 className="animate-spin mb-4" size={32} />
        <p>Loading workspaces...</p>
      </div>
    );
  }

  if (!activeWorkspace) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-secondary">
        <p>No workspace selected or available.</p>
      </div>
    );
  }

  return (
    <div className="flex-col gap-6 w-full">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-secondary">Welcome to {activeWorkspace.name}</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-64 text-secondary">
          <Loader2 className="animate-spin mb-4" size={32} />
          <p>Loading dashboard data...</p>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center h-64 text-danger bg-danger/10 border border-danger/20 rounded-xl">
          <AlertCircle size={32} className="mb-4" />
          <p className="mb-4">{error}</p>
          <Button variant="outline" onClick={fetchDashboardData}>Retry</Button>
        </div>
      ) : data ? (
        <>
          <KPICards data={data} />
          
          <div className="mb-6">
            <AnalyticsOverview data={data} />
          </div>

          <div className={styles.contentGrid}>
            <div className="flex flex-col gap-6">
              <RecentPosts posts={data.recentPosts} />
              <UpcomingSchedule posts={data.upcomingScheduledPosts} />
            </div>
            <div className="flex flex-col gap-6">
              <QuickActions />
              <SocialAccountsSummary accounts={data.accounts} />
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
