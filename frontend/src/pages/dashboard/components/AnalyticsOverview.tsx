import { Card, CardContent, CardHeader } from '../../../components/ui/Card';
import { DashboardData } from '../../../services/api/dashboardService';

interface AnalyticsOverviewProps {
  data: DashboardData;
}

export function AnalyticsOverview({ data }: AnalyticsOverviewProps) {
  const summary = data.analyticsSummary;
  
  const safeNumber = (val: number | undefined | null) => {
    if (val === null || val === undefined) return 'N/A';
    return val.toLocaleString();
  };

  return (
    <Card glass>
      <CardHeader title="Analytics Summary" subtitle="Aggregated metrics for this workspace" />
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Impressions</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_impressions)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Views</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_views)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Likes</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_likes)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Comments</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_comments)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Shares</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_shares)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Saves</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_saves)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Clicks</span>
            <span className="text-xl font-bold">{safeNumber(summary?.total_clicks)}</span>
          </div>
          <div className="flex flex-col p-4 bg-surface rounded-lg border border-border">
            <span className="text-sm text-secondary">Engagement</span>
            <span className="text-xl font-bold">
              {summary?.average_engagement_rate !== undefined && summary?.average_engagement_rate !== null
                ? `${summary.average_engagement_rate.toFixed(2)}%` 
                : 'N/A'}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
