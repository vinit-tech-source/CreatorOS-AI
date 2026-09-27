import { useEffect, useState } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';
import { Activity, Users, Eye, MousePointerClick, TrendingUp } from 'lucide-react';
import { Skeleton } from '../../components/ui/Skeleton';
import './AnalyticsDashboard.css';

interface DashboardStats {
  totalImpressions: number;
  totalEngagements: number;
  avgEngagementRate: number;
  followerGrowth: number;
}

const mockChartData = [
  { name: 'Mon', impressions: 4000, engagements: 240 },
  { name: 'Tue', impressions: 3000, engagements: 139 },
  { name: 'Wed', impressions: 2000, engagements: 980 },
  { name: 'Thu', impressions: 2780, engagements: 390 },
  { name: 'Fri', impressions: 1890, engagements: 480 },
  { name: 'Sat', impressions: 2390, engagements: 380 },
  { name: 'Sun', impressions: 3490, engagements: 430 },
];

export function AnalyticsDashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    // Simulate API fetch
    const timer = setTimeout(() => {
      setStats({
        totalImpressions: 124500,
        totalEngagements: 4200,
        avgEngagementRate: 3.4,
        followerGrowth: +120
      });
      setLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="analytics-container">
      <header className="analytics-header">
        <div>
          <h1 className="analytics-title">Workspace Analytics</h1>
          <p className="analytics-subtitle">Track your performance and audience growth across all social channels.</p>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="analytics-grid">
        <div className="kpi-card extruded-panel">
          <div className="kpi-header">
            <h3 className="kpi-title">Impressions</h3>
            <Eye className="kpi-icon text-cyan" size={20} />
          </div>
          {loading ? (
            <Skeleton width="120px" height="36px" style={{ marginTop: '0.5rem' }} />
          ) : (
            <p className="kpi-value">{stats?.totalImpressions.toLocaleString()}</p>
          )}
          <p className="kpi-trend positive"><TrendingUp size={14} /> +12.5% this week</p>
        </div>

        <div className="kpi-card extruded-panel">
          <div className="kpi-header">
            <h3 className="kpi-title">Engagements</h3>
            <MousePointerClick className="kpi-icon text-primary" size={20} />
          </div>
          {loading ? (
            <Skeleton width="120px" height="36px" style={{ marginTop: '0.5rem' }} />
          ) : (
            <p className="kpi-value">{stats?.totalEngagements.toLocaleString()}</p>
          )}
          <p className="kpi-trend positive"><TrendingUp size={14} /> +8.2% this week</p>
        </div>

        <div className="kpi-card extruded-panel">
          <div className="kpi-header">
            <h3 className="kpi-title">Avg. Engagement Rate</h3>
            <Activity className="kpi-icon text-pink" size={20} />
          </div>
          {loading ? (
            <Skeleton width="100px" height="36px" style={{ marginTop: '0.5rem' }} />
          ) : (
            <p className="kpi-value">{stats?.avgEngagementRate}%</p>
          )}
          <p className="kpi-trend neutral">Stable</p>
        </div>

        <div className="kpi-card extruded-panel">
          <div className="kpi-header">
            <h3 className="kpi-title">New Followers</h3>
            <Users className="kpi-icon text-green" size={20} />
          </div>
          {loading ? (
            <Skeleton width="80px" height="36px" style={{ marginTop: '0.5rem' }} />
          ) : (
            <p className="kpi-value">+{stats?.followerGrowth}</p>
          )}
          <p className="kpi-trend positive"><TrendingUp size={14} /> +24% this week</p>
        </div>
      </div>

      {/* Charts Area */}
      <div className="charts-grid">
        <div className="chart-card extruded-panel">
          <h3 className="chart-title">Impressions Overview</h3>
          <div className="chart-wrapper">
            {loading ? (
              <Skeleton width="100%" height="100%" animation="wave" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorImpressions" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--cyan)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--cyan)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 12 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--panel-2)', borderColor: 'var(--border)', borderRadius: '8px', color: 'var(--text)' }}
                    itemStyle={{ color: 'var(--cyan)' }}
                  />
                  <Area type="monotone" dataKey="impressions" stroke="var(--cyan)" strokeWidth={3} fillOpacity={1} fill="url(#colorImpressions)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="chart-card extruded-panel">
          <h3 className="chart-title">Engagement Breakdown</h3>
          <div className="chart-wrapper">
            {loading ? (
              <Skeleton width="100%" height="100%" animation="wave" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 12 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--panel-2)', borderColor: 'var(--border)', borderRadius: '8px', color: 'var(--text)' }}
                    itemStyle={{ color: 'var(--primary)' }}
                  />
                  <Line type="monotone" dataKey="engagements" stroke="var(--primary-2)" strokeWidth={3} dot={{ r: 4, fill: 'var(--panel)', strokeWidth: 2 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
