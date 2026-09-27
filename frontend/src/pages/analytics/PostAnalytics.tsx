/**
 * PostAnalytics.tsx
 *
 * Post Analytics detail page for CreatorOS AI.
 * Displays metrics for a specific post.
 */
import { useEffect, useState, useMemo, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  Eye,
  Heart,
  MessageSquare,
  Share2,
  TrendingUp,
  AlertCircle,
  Calendar,
  Globe
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { analyticsService } from '../../services/api/analyticsService';
import { PostAnalyticsResponse } from '../../types';
import styles from './PostAnalytics.module.css';

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
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return 'Unknown';
  }
}

export function PostAnalytics() {
  const { workspaceId, projectId, postId } = useParams<{ workspaceId: string, projectId: string, postId: string }>();

  const [snapshots, setSnapshots] = useState<PostAnalyticsResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!projectId || !postId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await analyticsService.getPostAnalytics(projectId, postId);
      setSnapshots(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to load post analytics.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, postId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Latest snapshot is the first one in the array (assuming API returns desc, or we find max collected_at)
  const latestSnapshot = useMemo(() => {
    if (snapshots.length === 0) return null;
    return snapshots.reduce((latest, current) => {
      return new Date(current.collected_at) > new Date(latest.collected_at) ? current : latest;
    });
  }, [snapshots]);

  const chartData = useMemo(() => {
    // Sort snapshots chronologically for the chart
    return [...snapshots]
      .sort((a, b) => new Date(a.collected_at).getTime() - new Date(b.collected_at).getTime())
      .map(snap => ({
        date: formatDate(snap.collected_at),
        likes: snap.likes || 0,
        comments: snap.comments || 0,
        shares: snap.shares || 0,
        views: snap.views || 0,
      }));
  }, [snapshots]);

  return (
    <div className={styles.page}>
      <Link to={`/workspaces/${workspaceId}/analytics`} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '0.875rem' }}>
        <ArrowLeft size={16} /> Back to Analytics
      </Link>

      <PageHeader
        title="Post Analytics"
        subtitle={
          <span className={styles.metaList}>
            {latestSnapshot && (
              <>
                <span className={styles.metaItem}>
                  <Globe size={14} /> <Badge variant="secondary">{latestSnapshot.platform}</Badge>
                </span>
                <span className={styles.metaItem}>
                  <Calendar size={14} /> Published: {formatDate(latestSnapshot.created_at)}
                </span>
                {latestSnapshot.external_post_id && (
                  <span className={styles.metaItem}>
                    External ID: {latestSnapshot.external_post_id}
                  </span>
                )}
              </>
            )}
          </span>
        }
        action={
          <Button
            variant="outline"
            size="sm"
            onClick={loadData}
            disabled={isLoading}
            isLoading={isLoading}
          >
            <RefreshCw size={16} aria-hidden />
            Refresh
          </Button>
        }
      />

      {error && !isLoading && (
        <Card glass>
          <CardContent>
            <div className={styles.errorState} role="alert">
              <AlertCircle size={40} aria-hidden />
              <p style={{ fontSize: '1rem', fontWeight: 600 }}>Unable to load post analytics</p>
              <p style={{ fontSize: '0.875rem' }}>{error}</p>
              <Button variant="outline" size="sm" onClick={loadData}>
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {!error && (
        <>
          <div className={styles.kpiGrid} role="region" aria-label="KPI Summary">
            <div className={styles.kpiCard}>
              <div className={styles.kpiHeader}>
                <Eye size={16} /> Views
              </div>
              <div className={styles.kpiValue}>
                {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(latestSnapshot?.views)}
              </div>
            </div>
            <div className={styles.kpiCard}>
              <div className={styles.kpiHeader}>
                <Heart size={16} /> Likes
              </div>
              <div className={styles.kpiValue}>
                {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(latestSnapshot?.likes)}
              </div>
            </div>
            <div className={styles.kpiCard}>
              <div className={styles.kpiHeader}>
                <MessageSquare size={16} /> Comments
              </div>
              <div className={styles.kpiValue}>
                {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(latestSnapshot?.comments)}
              </div>
            </div>
            <div className={styles.kpiCard}>
              <div className={styles.kpiHeader}>
                <Share2 size={16} /> Shares
              </div>
              <div className={styles.kpiValue}>
                {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatNumber(latestSnapshot?.shares)}
              </div>
            </div>
            <div className={styles.kpiCard}>
              <div className={styles.kpiHeader}>
                <TrendingUp size={16} /> Engagement Rate
              </div>
              <div className={styles.kpiValue}>
                {isLoading ? <div className={styles.skeletonLine} style={{ width: '60%', height: '32px' }} /> : formatPercent(latestSnapshot?.engagement_rate)}
              </div>
            </div>
          </div>

          <Card glass className={styles.chartCard}>
            <div className={styles.chartHeader}>
              <h2 className={styles.chartTitle}>Performance Over Time</h2>
            </div>
            
            {isLoading ? (
              <div className={styles.chartContainer} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                 <div className={styles.skeletonLine} style={{ height: '100%' }} />
              </div>
            ) : chartData.length > 1 ? (
              <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-strong)" />
                    <XAxis dataKey="date" stroke="var(--muted)" fontSize={12} tickMargin={10} />
                    <YAxis stroke="var(--muted)" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--bg-surface-solid)', borderColor: 'var(--border-color)', borderRadius: 8 }}
                      itemStyle={{ color: 'var(--text-primary)' }}
                    />
                    <Line type="monotone" dataKey="likes" stroke="var(--color-primary)" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Likes" />
                    <Line type="monotone" dataKey="comments" stroke="var(--panel-2)" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Comments" />
                    <Line type="monotone" dataKey="shares" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Shares" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className={styles.chartContainer} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                 <p style={{ color: 'var(--text-muted)' }}>Not enough historical data to display trends.</p>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
