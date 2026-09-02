import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { useAuthStore } from '../../stores/authStore';
import { dashboardService, DashboardData } from '../../services/api/dashboardService';
import { KPICards } from './components/KPICards';
import { RecentPosts } from './components/RecentPosts';
import { UpcomingSchedule } from './components/UpcomingSchedule';
import { SocialAccountsSummary } from './components/SocialAccountsSummary';
import { QuickActions } from './components/QuickActions';
import { 
  Loader2, 
  AlertCircle, 
  Bot, 
  Calendar, 
  Palette, 
  Plus, 
  ArrowRight,
  CheckCircle2
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import styles from './Dashboard.module.css';

const AUTONOMOUS_AGENTS_RADAR = [
  { name: 'Strategy Agent', role: 'Audience & Goals' },
  { name: 'Trend Agent', role: 'Velocity Scraper' },
  { name: 'Research Agent', role: 'Fact Extraction' },
  { name: 'Content Planner', role: 'Story Framework' },
  { name: 'Content Generator', role: 'Copywriting' },
  { name: 'Brand Voice Agent', role: 'Rule Compliance' },
  { name: 'Fact Checker', role: 'Truth Verification' },
  { name: 'SEO Agent', role: 'Discovery Rank' },
  { name: 'Hashtag Agent', role: 'Niche Graph' },
  { name: 'Image Prompt Agent', role: 'Visual Brief' },
];

export function Dashboard() {
  const { activeWorkspace, isLoading: isWorkspaceLoading } = useWorkspaceStore();
  const { user } = useAuthStore();
  
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    if (!activeWorkspace) return;
    
    setIsLoading(true);
    setError(null);
    setData(null);
    
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

  const creatorName = user?.first_name 
    ? `${user.first_name} ${user.last_name || ''}`.trim() 
    : user?.username || user?.email?.split('@')[0] || 'Creator';

  return (
    <div className={styles.container}>
      {/* 1. Executive Hero & Live Engine Status */}
      <div className={styles.executiveHeroCard}>
        <div className={styles.heroLeft}>
          <div className={styles.greetingRow}>
            <h1 className={styles.greetingTitle}>Welcome back, {creatorName}</h1>
            <span className={styles.workspacePill}>{activeWorkspace.name}</span>
          </div>
          <p className={styles.heroSubtitle}>
            Your autonomous content engine is running optimally with cross-channel scheduling active.
          </p>
        </div>

        <div className={styles.heroRight}>
          <div className={styles.engineStatusBadge}>
            <span className={styles.enginePulseDot} />
            <span>10 AI Agents Active</span>
          </div>

          <div className={styles.quickToolbarRow}>
            <Link to="/create">
              <button type="button" className={`${styles.quickToolBtn} ${styles.quickToolBtnPrimary}`}>
                <Plus size={14} /> Create Post
              </button>
            </Link>

            <Link to="/automation/pipeline">
              <button type="button" className={styles.quickToolBtn}>
                <Bot size={14} className="text-indigo-400" /> Pipeline
              </button>
            </Link>

            <Link to="/calendar">
              <button type="button" className={styles.quickToolBtn}>
                <Calendar size={14} /> Calendar
              </button>
            </Link>

            <Link to="/brand-kit">
              <button type="button" className={styles.quickToolBtn}>
                <Palette size={14} /> Brand Kit
              </button>
            </Link>
          </div>
        </div>
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
          {/* 2. AI Idea Canvas (Interactive Generator) */}
          <QuickActions />
          
          {/* 3. Executive KPI Cadence Metrics Strip */}
          <KPICards data={data} />
          
          {/* 4. Modular 2-Column Operational Grid */}
          <div className={styles.contentGrid}>
            {/* Left Column: Scheduled Releases & Recent Content */}
            <div className="flex flex-col gap-6">
              <UpcomingSchedule posts={data.upcomingScheduledPosts} />
              <RecentPosts posts={data.recentPosts} />
            </div>

            {/* Right Column: Autonomous Agents Radar & Connected Channels */}
            <div className="flex flex-col gap-6">
              {/* Autonomous Agents Live Radar Card */}
              <div className={styles.agentRadarCard}>
                <div className={styles.agentRadarHeader}>
                  <div className={styles.agentRadarTitleWrap}>
                    <Bot size={18} className="text-indigo-400" />
                    <h3 className={styles.agentRadarTitle}>Autonomous Multi-Agent Swarm</h3>
                  </div>
                  <Link 
                    to="/automation/pipeline" 
                    className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                  >
                    Live Pipeline <ArrowRight size={12} />
                  </Link>
                </div>

                <div className={styles.agentChipsGrid}>
                  {AUTONOMOUS_AGENTS_RADAR.map(agent => (
                    <div key={agent.name} className={styles.agentMiniPill}>
                      <span className={styles.agentMiniName}>{agent.name}</span>
                      <span className={styles.agentMiniStatus}>
                        <CheckCircle2 size={10} /> ready
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Connected Social Accounts Summary */}
              <SocialAccountsSummary accounts={data.accounts} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
