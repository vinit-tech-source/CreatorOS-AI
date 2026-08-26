/**
 * Analytics.tsx
 *
 * Workspace Analytics Dashboard for CreatorOS AI.
 *
 * Provides:
 * - KPI Summary cards
 * - Performance trends (Line chart)
 * - Post performance table with UI-level sorting and filtering
 */
import { useEffect, useState, useMemo, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  BarChart3,
  RefreshCw,
  Eye,
  Heart,
  MessageSquare,
  Share2,
  TrendingUp,
  AlertCircle,
  FileText,
  Filter,
  ArrowUp,
  ArrowDown
} from 'lucide-react';
import { AnalyticsChart3D } from './components/3d/AnalyticsChart3D';

import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { useAnalyticsStore } from '../../stores/analyticsStore';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import styles from './Analytics.module.css';

type SortField = 'created_at' | 'engagement_rate' | 'likes' | 'comments' | 'shares' | 'views';
type SortOrder = 'asc' | 'desc';

function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return 'N/A';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

function formatPercent(num: number | null | undefined): string {
  if (num === null || num === undefined) return 'N/A';
  return (num * 100).toFixed(1) + '%';
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  } catch {
    return 'Unknown';
  }
}

export function Analytics() {
  const { workspaceId: routeWorkspaceId } = useParams<{ workspaceId: string }>();
  const { activeWorkspace } = useWorkspaceStore();
  const workspaceId = routeWorkspaceId || activeWorkspace?.id || null;

  const {
    workspaceSummary,
    workspacePostsAnalytics,
    isLoading,
    error,
    fetchWorkspaceAnalytics,
    clearAnalytics
  } = useAnalyticsStore();

  const [platformFilter, setPlatformFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const loadAnalytics = useCallback(() => {
    if (workspaceId) {
      fetchWorkspaceAnalytics(workspaceId);
    }
  }, [workspaceId, fetchWorkspaceAnalytics]);

  useEffect(() => {
    loadAnalytics();
    return () => {
      clearAnalytics();
    };
  }, [loadAnalytics, clearAnalytics]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc'); // Default to descending when changing fields
    }
  };

  const filteredAndSortedPosts = useMemo(() => {
    let result = [...workspacePostsAnalytics];

    // Filter
    if (platformFilter !== 'all') {
      result = result.filter(p => p.platform.toLowerCase() === platformFilter.toLowerCase());
    }

    // Sort
    result.sort((a, b) => {
      let valA: any = a[sortField];
      let valB: any = b[sortField];

      // Handle nulls safely (treat nulls as lowest value)
      if (valA === null || valA === undefined) valA = -1;
      if (valB === null || valB === undefined) valB = -1;

      if (sortField === 'created_at') {
        valA = new Date(a.created_at).getTime();
        valB = new Date(b.created_at).getTime();
      }

      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [workspacePostsAnalytics, platformFilter, sortField, sortOrder]);

  const chartData = useMemo(() => {
    // Group by date, calculating average engagement rate
    const dateMap = new Map<string, { date: string, totalEngagement: number, count: number }>();

    filteredAndSortedPosts.forEach(post => {
      if (post.engagement_rate === null || post.engagement_rate === undefined) return;
      
      const dateStr = formatDate(post.created_at);
      const existing = dateMap.get(dateStr) || { date: dateStr, totalEngagement: 0, count: 0 };
      
      existing.totalEngagement += post.engagement_rate;
      existing.count += 1;
      dateMap.set(dateStr, existing);
    });

    return Array.from(dateMap.values())
      .map(item => ({
        date: item.date,
        engagement: Number(((item.totalEngagement / item.count) * 100).toFixed(2))
      }))
      .reverse(); // Time series should usually read left-to-right (oldest to newest)
  }, [filteredAndSortedPosts]);

  const noWorkspace = !workspaceId;

  return (
    <div className={styles.page}>
      <PageHeader
        title="Workspace Analytics"
        subtitle="Track your overall performance and engagement metrics across platforms."
        action={
          !noWorkspace && (
            <Button
              variant="outline"
              size="sm"
              onClick={loadAnalytics}
              disabled={isLoading}
              isLoading={isLoading}
              id="refresh-analytics-btn"
            >
              <RefreshCw size={16} aria-hidden />
              Refresh
            </Button>
          )
        }
      />

      {noWorkspace && (
        <Card glass>
          <CardContent>
            <div className={styles.emptyState}>
              <AlertCircle size={40} className={styles.emptyIcon} aria-hidden />
              <p style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-primary)' }}>No workspace selected</p>
              <p className="mb-4">Select a workspace from the sidebar to view its analytics.</p>
              <Button onClick={() => window.location.href = '/workspaces'}>
                Go to Workspaces
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {!noWorkspace && error && !isLoading && (
        <Card glass>
          <CardContent>
            <div className={styles.errorState} role="alert">
              <AlertCircle size={40} aria-hidden />
              <p style={{ fontSize: '1rem', fontWeight: 600 }}>Unable to load analytics</p>
              <p style={{ fontSize: '0.875rem' }}>{error}</p>
              <Button variant="outline" size="sm" onClick={loadAnalytics}>
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── KPI Summary ── */}
      {!noWorkspace && !error && (
        <div className={styles.kpiGrid} role="region" aria-label="KPI Summary">
          <div className={styles.kpiCard}>
            <div className={styles.kpiHeader}>
              <Eye size={16} /> Total Views
            </div>
            <div className={styles.kpiValue}>
              {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(workspaceSummary?.total_views)}
            </div>
          </div>
          <div className={styles.kpiCard}>
            <div className={styles.kpiHeader}>
              <Heart size={16} /> Total Likes
            </div>
            <div className={styles.kpiValue}>
              {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(workspaceSummary?.total_likes)}
            </div>
          </div>
          <div className={styles.kpiCard}>
            <div className={styles.kpiHeader}>
              <MessageSquare size={16} /> Comments
            </div>
            <div className={styles.kpiValue}>
              {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(workspaceSummary?.total_comments)}
            </div>
          </div>
          <div className={styles.kpiCard}>
            <div className={styles.kpiHeader}>
              <Share2 size={16} /> Shares
            </div>
            <div className={styles.kpiValue}>
              {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(workspaceSummary?.total_shares)}
            </div>
          </div>
          <div className={styles.kpiCard}>
            <div className={styles.kpiHeader}>
              <TrendingUp size={16} /> Avg Engagement
            </div>
            <div className={styles.kpiValue}>
              {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatPercent(workspaceSummary?.average_engagement_rate)}
            </div>
          </div>
        </div>
      )}

      {/* ── Performance Trends Chart ── */}
      {!noWorkspace && !error && (
        <Card glass className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <h2 className={styles.chartTitle}>Engagement Trends</h2>
          </div>
          
          {isLoading ? (
            <div className={styles.chartContainer} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
               <div className={styles.skeletonLine} style={{ height: '100%' }} />
            </div>
          ) : (
            <AnalyticsChart3D data={chartData} />
          )}
        </Card>
      )}

      {/* ── Post Performance Table ── */}
      {!noWorkspace && !error && (
        <Card glass>
          <CardContent>
            <div className={styles.tableControls}>
              <h2 className={styles.chartTitle}>Post Performance</h2>
              <div className={styles.filters}>
                <Filter size={16} color="var(--text-secondary)" />
                <select 
                  className={styles.filterSelect}
                  value={platformFilter}
                  onChange={(e) => setPlatformFilter(e.target.value)}
                  aria-label="Filter by platform"
                  disabled={isLoading}
                >
                  <option value="all">All Platforms</option>
                  <option value="bluesky">Bluesky</option>
                  <option value="x">X (Twitter)</option>
                  <option value="linkedin">LinkedIn</option>
                </select>
              </div>
            </div>

            {isLoading ? (
              <div className={styles.tableContainer}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th>Post</th><th>Platform</th><th>Date</th><th>Views</th><th>Likes</th><th>Comments</th><th>Shares</th><th>Engagement</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i}>
                        <td colSpan={8}><div className={styles.skeletonLine} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : filteredAndSortedPosts.length === 0 ? (
              <div className={styles.emptyState}>
                <FileText size={48} className={styles.emptyIcon} aria-hidden />
                <p style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 0 }}>No posts found</p>
                <p>Publish a post to start collecting performance data.</p>
              </div>
            ) : (
              <div className={styles.tableContainer}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th onClick={() => handleSort('created_at')}>
                        Published Date
                        {sortField === 'created_at' && (sortOrder === 'asc' ? <ArrowUp size={12} className={`${styles.sortIcon} ${styles.active}`} /> : <ArrowDown size={12} className={`${styles.sortIcon} ${styles.active}`} />)}
                      </th>
                      <th>Platform</th>
                      <th className={styles.metricCell} onClick={() => handleSort('views')}>
                        Views
                        {sortField === 'views' && (sortOrder === 'asc' ? <ArrowUp size={12} className={`${styles.sortIcon} ${styles.active}`} /> : <ArrowDown size={12} className={`${styles.sortIcon} ${styles.active}`} />)}
                      </th>
                      <th className={styles.metricCell} onClick={() => handleSort('likes')}>
                        Likes
                        {sortField === 'likes' && (sortOrder === 'asc' ? <ArrowUp size={12} className={`${styles.sortIcon} ${styles.active}`} /> : <ArrowDown size={12} className={`${styles.sortIcon} ${styles.active}`} />)}
                      </th>
                      <th className={styles.metricCell} onClick={() => handleSort('comments')}>
                        Comments
                        {sortField === 'comments' && (sortOrder === 'asc' ? <ArrowUp size={12} className={`${styles.sortIcon} ${styles.active}`} /> : <ArrowDown size={12} className={`${styles.sortIcon} ${styles.active}`} />)}
                      </th>
                      <th className={styles.metricCell} onClick={() => handleSort('shares')}>
                        Shares
                        {sortField === 'shares' && (sortOrder === 'asc' ? <ArrowUp size={12} className={`${styles.sortIcon} ${styles.active}`} /> : <ArrowDown size={12} className={`${styles.sortIcon} ${styles.active}`} />)}
                      </th>
                      <th className={styles.metricCell} onClick={() => handleSort('engagement_rate')}>
                        Engagement
                        {sortField === 'engagement_rate' && (sortOrder === 'asc' ? <ArrowUp size={12} className={`${styles.sortIcon} ${styles.active}`} /> : <ArrowDown size={12} className={`${styles.sortIcon} ${styles.active}`} />)}
                      </th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAndSortedPosts.map((post) => (
                      <tr key={post.id}>
                        <td>{formatDate(post.created_at)}</td>
                        <td>
                          <Badge variant="secondary">{post.platform}</Badge>
                        </td>
                        <td className={styles.metricCell}>{formatNumber(post.views)}</td>
                        <td className={styles.metricCell}>{formatNumber(post.likes)}</td>
                        <td className={styles.metricCell}>{formatNumber(post.comments)}</td>
                        <td className={styles.metricCell}>{formatNumber(post.shares)}</td>
                        <td className={styles.metricCell}>{formatPercent(post.engagement_rate)}</td>
                        <td>
                          <Link 
                            to={`/workspaces/${workspaceId}/projects/${post.workspace_id}/posts/${post.post_id}/analytics`}
                            style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--color-primary)', fontSize: '0.75rem', fontWeight: 500 }}
                          >
                            Details <BarChart3 size={12} />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
