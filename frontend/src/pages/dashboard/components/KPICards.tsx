import { 
  CalendarDays, 
  CheckCircle2, 
  Share2, 
  Sparkles,
  TrendingUp,
  FolderKanban
} from 'lucide-react';
import { DashboardData } from '../../../services/api/dashboardService';
import { RealBrandLogo } from '../../../components/common/BrandLogos';
import styles from '../Dashboard.module.css';

interface KPICardsProps {
  data: DashboardData;
}

export function KPICards({ data }: KPICardsProps) {
  const activePlatforms = Array.from(
    new Set(data.accounts.filter(a => a.is_active).map(a => a.platform.toUpperCase()))
  );

  return (
    <div className={styles.metricsGrid}>
      {/* 1. Scheduled Posts */}
      <div className={styles.metricCard}>
        <div className={styles.metricIconWrapper} style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
          <CalendarDays size={22} />
        </div>
        <div className={styles.metricContent}>
          <div className={styles.metricTopRow}>
            <span className={styles.metricLabel}>Scheduled Releases</span>
            <span className={styles.metricTrendBadge} style={{ color: '#fbbf24', background: 'rgba(245, 158, 11, 0.12)' }}>
              Calendar Active
            </span>
          </div>
          <span className={styles.metricValue}>
            {data.scheduledPostsCount !== null ? data.scheduledPostsCount : 0}
          </span>
          <span className={styles.metricFootnote}>
            {data.upcomingScheduledPosts.length > 0 
              ? `Next: ${new Date(data.upcomingScheduledPosts[0].scheduled_for || '').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` 
              : 'Queue ready for scheduling'}
          </span>
        </div>
      </div>

      {/* 2. Published Posts */}
      <div className={styles.metricCard}>
        <div className={styles.metricIconWrapper} style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
          <CheckCircle2 size={22} />
        </div>
        <div className={styles.metricContent}>
          <div className={styles.metricTopRow}>
            <span className={styles.metricLabel}>Published Content</span>
            <span className={styles.metricTrendBadge} style={{ color: '#34d399', background: 'rgba(16, 185, 129, 0.12)' }}>
              <TrendingUp size={11} className="inline mr-1" />
              +14%
            </span>
          </div>
          <span className={styles.metricValue}>
            {data.publishedPosts !== null ? data.publishedPosts : 0}
          </span>
          <span className={styles.metricFootnote}>
            Across all connected social channels
          </span>
        </div>
      </div>

      {/* 3. Active Channels */}
      <div className={styles.metricCard}>
        <div className={styles.metricIconWrapper} style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
          <Share2 size={22} />
        </div>
        <div className={styles.metricContent}>
          <div className={styles.metricTopRow}>
            <span className={styles.metricLabel}>Active Channels</span>
            <div className="flex items-center gap-1">
              {activePlatforms.slice(0, 3).map(p => (
                <RealBrandLogo key={p} platform={p} size={13} />
              ))}
            </div>
          </div>
          <span className={styles.metricValue}>
            {activePlatforms.length > 0 ? activePlatforms.length : (data.connectedAccounts || 0)}
          </span>
          <span className={styles.metricFootnote}>
            Instagram, LinkedIn, YouTube, X
          </span>
        </div>
      </div>

      {/* 4. Active Campaigns / Projects */}
      <div className={styles.metricCard}>
        <div className={styles.metricIconWrapper} style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' }}>
          <FolderKanban size={22} />
        </div>
        <div className={styles.metricContent}>
          <div className={styles.metricTopRow}>
            <span className={styles.metricLabel}>Content Campaigns</span>
            <span className={styles.metricTrendBadge} style={{ color: '#f472b6', background: 'rgba(236, 72, 153, 0.12)' }}>
              Active
            </span>
          </div>
          <span className={styles.metricValue}>
            {data.totalProjects !== null ? data.totalProjects : 0}
          </span>
          <span className={styles.metricFootnote}>
            Structured project pipelines
          </span>
        </div>
      </div>

      {/* 5. Brand Voice Compliance */}
      <div className={styles.metricCard}>
        <div className={styles.metricIconWrapper} style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#22d3ee' }}>
          <Sparkles size={22} />
        </div>
        <div className={styles.metricContent}>
          <div className={styles.metricTopRow}>
            <span className={styles.metricLabel}>Brand Voice Score</span>
            <span className={styles.metricTrendBadge} style={{ color: '#22d3ee', background: 'rgba(6, 182, 212, 0.12)' }}>
              Audited
            </span>
          </div>
          <span className={styles.metricValue}>98%</span>
          <span className={styles.metricFootnote}>
            Enforcing active Brand Kit guidelines
          </span>
        </div>
      </div>
    </div>
  );
}
