import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { 
  BarChart3, 
  CalendarDays, 
  CheckCircle2, 
  FolderKanban,
  Users
} from 'lucide-react';
import styles from './Dashboard.module.css';

export function Dashboard() {
  return (
    <div className="flex-col gap-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-secondary">Welcome back to CreatorOS AI.</p>
        </div>
      </div>

      <div className={styles.metricsGrid}>
        <Card glass>
          <CardContent className="pt-6">
            <div className={styles.metricCard}>
              <div className={styles.metricIconWrapper} style={{ backgroundColor: 'rgba(99, 102, 241, 0.1)', color: '#6366f1' }}>
                <FolderKanban size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricLabel}>Active Projects</span>
                <span className={styles.metricValue}>12</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardContent className="pt-6">
            <div className={styles.metricCard}>
              <div className={styles.metricIconWrapper} style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>
                <CheckCircle2 size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricLabel}>Published Posts</span>
                <span className={styles.metricValue}>48</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardContent className="pt-6">
            <div className={styles.metricCard}>
              <div className={styles.metricIconWrapper} style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}>
                <CalendarDays size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricLabel}>Scheduled</span>
                <span className={styles.metricValue}>5</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardContent className="pt-6">
            <div className={styles.metricCard}>
              <div className={styles.metricIconWrapper} style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9' }}>
                <Users size={24} />
              </div>
              <div className={styles.metricInfo}>
                <span className={styles.metricLabel}>Total Engagement</span>
                <span className={styles.metricValue}>12.4k</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className={styles.contentGrid}>
        <Card className={styles.recentActivity}>
          <CardHeader title="Recent Activity" subtitle="Your latest content actions" />
          <CardContent>
            <div className="flex items-center justify-center h-48 text-secondary">
              No recent activity to show.
            </div>
          </CardContent>
        </Card>
        
        <Card className={styles.engagementOverview}>
          <CardHeader title="Engagement Overview" subtitle="Last 30 days" />
          <CardContent>
            <div className="flex items-center justify-center h-48 text-secondary">
              <BarChart3 size={48} className="opacity-20 mb-2" />
              <p>Analytics will appear here once posts are published.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
