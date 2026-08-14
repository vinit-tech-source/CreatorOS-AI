import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { BarChart3, TrendingUp, Users, Heart, MessageCircle } from 'lucide-react';
import { AnalyticsSummary } from '../../types';

export function Analytics() {
  const [summary, _setSummary] = useState<AnalyticsSummary | null>(null);
  const [_isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        // Need a workspace ID in a real app, assuming one is provided by state/URL
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch analytics', error);
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  return (
    <div className="flex-col gap-6">
      <PageHeader 
        title="Analytics" 
        subtitle="Measure the performance of your social media content"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card glass>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(99, 102, 241, 0.1)', color: '#6366f1' }}>
                <TrendingUp size={24} />
              </div>
              <div>
                <span className="text-sm text-secondary font-medium block">Total Impressions</span>
                <span className="text-2xl font-bold text-primary-text block">{summary?.total_impressions || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>
                <Heart size={24} />
              </div>
              <div>
                <span className="text-sm text-secondary font-medium block">Total Likes</span>
                <span className="text-2xl font-bold text-primary-text block">{summary?.total_likes || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}>
                <MessageCircle size={24} />
              </div>
              <div>
                <span className="text-sm text-secondary font-medium block">Total Comments</span>
                <span className="text-2xl font-bold text-primary-text block">{summary?.total_comments || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(14, 165, 233, 0.1)', color: '#0ea5e9' }}>
                <Users size={24} />
              </div>
              <div>
                <span className="text-sm text-secondary font-medium block">Avg. Engagement Rate</span>
                <span className="text-2xl font-bold text-primary-text block">{summary?.average_engagement_rate ? `${summary.average_engagement_rate.toFixed(2)}%` : '0%'}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="min-h-[300px]">
        <CardHeader title="Performance Over Time" />
        <CardContent>
          <div className="flex flex-col items-center justify-center h-48 text-secondary">
            <BarChart3 size={48} className="opacity-20 mb-4" />
            <p>Not enough data to generate charts yet.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
