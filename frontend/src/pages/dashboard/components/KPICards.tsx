import { Card, CardContent } from '../../../components/ui/Card';
import { 
  FolderKanban, 
  PenTool, 
  CalendarDays, 
  CheckCircle2,
  Share2,
  Activity
} from 'lucide-react';
import styles from '../Dashboard.module.css';
import { DashboardData } from '../../../services/api/dashboardService';

interface KPICardsProps {
  data: DashboardData;
}

export function KPICards({ data }: KPICardsProps) {
  const metrics = [
    {
      label: 'Total Projects',
      value: data.totalProjects !== null ? data.totalProjects : '--',
      icon: FolderKanban,
      color: '#6366f1',
      bg: 'rgba(99, 102, 241, 0.1)',
    },
    {
      label: 'Total Posts',
      value: data.totalPosts !== null ? data.totalPosts : '--',
      icon: PenTool,
      color: '#3b82f6',
      bg: 'rgba(59, 130, 246, 0.1)',
    },
    {
      label: 'Scheduled Posts',
      value: data.scheduledPostsCount !== null ? data.scheduledPostsCount : '--',
      icon: CalendarDays,
      color: '#f59e0b',
      bg: 'rgba(245, 158, 11, 0.1)',
    },
    {
      label: 'Published Posts',
      value: data.publishedPosts !== null ? data.publishedPosts : '--',
      icon: CheckCircle2,
      color: '#10b981',
      bg: 'rgba(16, 185, 129, 0.1)',
    },
    {
      label: 'Connected Accounts',
      value: data.connectedAccounts !== null ? data.connectedAccounts : '--',
      icon: Share2,
      color: '#8b5cf6',
      bg: 'rgba(139, 92, 246, 0.1)',
    },
    {
      label: 'Avg Engagement Rate',
      value: data.analyticsSummary?.average_engagement_rate !== undefined 
        ? `${data.analyticsSummary.average_engagement_rate.toFixed(2)}%` 
        : '--',
      icon: Activity,
      color: '#0ea5e9',
      bg: 'rgba(14, 165, 233, 0.1)',
    }
  ];

  return (
    <div className={styles.metricsGrid}>
      {metrics.map((metric, i) => {
        const Icon = metric.icon;
        return (
          <Card key={i} glass>
            <CardContent className="pt-6">
              <div className={styles.metricCard}>
                <div className={styles.metricIconWrapper} style={{ backgroundColor: metric.bg, color: metric.color }}>
                  <Icon size={24} />
                </div>
                <div className={styles.metricInfo}>
                  <span className={styles.metricLabel}>{metric.label}</span>
                  <span className={styles.metricValue}>{metric.value}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
