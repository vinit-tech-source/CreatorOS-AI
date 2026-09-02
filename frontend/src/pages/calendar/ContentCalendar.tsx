import { useEffect, useState, useMemo } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  RefreshCw, 
  AlertCircle, 
  CalendarDays,
  LayoutGrid, 
  ListFilter, 
  Plus, 
  Search, 
  Clock, 
  CheckCircle2, 
  Zap, 
  Share2,
  Sparkles,
  Rocket
} from 'lucide-react';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { calendarService, CalendarPost } from '../../services/api/calendarService';
import { projectService } from '../../services/api/projectService';
import { Project } from '../../types';
import { MonthView, WeekView, AgendaView } from './components/CalendarViews';
import { PostDetailModal } from './components/PostDetailModal';
import { QuickScheduleModal } from './components/QuickScheduleModal';
import { RealBrandLogo } from '../../components/common/BrandLogos';
import { REAL_STOCK_PHOTOS } from '../../constants/realPhotography';
import styles from './ContentCalendar.module.css';

type ViewMode = 'month' | 'week' | 'agenda';

export function ContentCalendar() {
  const { activeWorkspace } = useWorkspaceStore();

  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [viewMode, setViewMode] = useState<ViewMode>('month');
  
  const [posts, setPosts] = useState<CalendarPost[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPopulatingDemo, setIsPopulatingDemo] = useState(false);

  // Filters & Search
  const [selectedPlatform, setSelectedPlatform] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Modals state
  const [selectedPostForDetail, setSelectedPostForDetail] = useState<CalendarPost | null>(null);
  const [isQuickScheduleOpen, setIsQuickScheduleOpen] = useState(false);
  const [quickScheduleDate, setQuickScheduleDate] = useState<Date | null>(null);

  const fetchCalendarData = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    setError(null);
    try {
      const [postsData, projectsData] = await Promise.all([
        calendarService.getWorkspaceCalendarPosts(activeWorkspace.id),
        projectService.getProjects(activeWorkspace.id).catch(() => [])
      ]);
      setPosts(postsData);
      setProjects(projectsData);
    } catch (err: any) {
      setError(err?.message || 'Failed to load content calendar data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCalendarData();
  }, [activeWorkspace]);

  // Handler to populate realistic demo posts with real photography
  const handlePopulateSamplePosts = async () => {
    if (!activeWorkspace || projects.length === 0) return;
    setIsPopulatingDemo(true);
    setError(null);

    const targetProject = projects[0];
    const now = new Date(currentDate);

    const sampleDemos = [
      {
        title: 'Master Content Repurposing Workflow',
        content: `Stop recreating the exact same post 5 times manually. CreatorOS turns 1 master input into platform-safe zones for Instagram, LinkedIn, and YouTube.\n\n[Attached Media]: ${REAL_STOCK_PHOTOS[0].url}`,
        platform: 'INSTAGRAM',
        dayOffset: 1,
        hours: 11,
      },
      {
        title: 'Why Consistency Beats Virality in 2026',
        content: `The creator economy rewards structured pipelines over sporadic motivation. Here is how our engineering team automates multi-market distribution.\n\n[Attached Media]: ${REAL_STOCK_PHOTOS[1].url}`,
        platform: 'LINKEDIN',
        dayOffset: 3,
        hours: 9,
      },
      {
        title: 'Complete Studio Setup & Lighting Breakdown',
        content: `Full behind-the-scenes breakdown of our audio mastering chain and 4K recording safe zones.\n\n[Attached Media]: ${REAL_STOCK_PHOTOS[3].url}`,
        platform: 'YOUTUBE',
        dayOffset: 5,
        hours: 15,
      },
      {
        title: 'CreatorOS 2.0 Feature Drop & Live Demo',
        content: `One idea. Every platform. Instant adaptation with audience intelligence.\n\n[Attached Media]: ${REAL_STOCK_PHOTOS[4].url}`,
        platform: 'X',
        dayOffset: 7,
        hours: 17,
      },
      {
        title: '10x Faster Video Hooks for Shorts',
        content: `How top creators keep retention high in the first 3 seconds.\n\n[Attached Media]: ${REAL_STOCK_PHOTOS[5].url}`,
        platform: 'TIKTOK',
        dayOffset: 9,
        hours: 19,
      },
    ];

    try {
      for (const demo of sampleDemos) {
        const d = new Date(now.getFullYear(), now.getMonth(), demo.dayOffset, demo.hours, 0, 0);

        await calendarService.quickCreateAndSchedule(targetProject.id, {
          title: demo.title,
          content: demo.content,
          platform: demo.platform,
          scheduled_at: d.toISOString(),
        });
      }
      await fetchCalendarData();
    } catch (err: any) {
      setError(err?.message || 'Failed to populate sample posts');
    } finally {
      setIsPopulatingDemo(false);
    }
  };

  // Date Navigation handlers
  const handlePrev = () => {
    if (viewMode === 'month') {
      setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
    } else if (viewMode === 'week') {
      const d = new Date(currentDate);
      d.setDate(d.getDate() - 7);
      setCurrentDate(d);
    } else {
      setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
    }
  };

  const handleNext = () => {
    if (viewMode === 'month') {
      setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
    } else if (viewMode === 'week') {
      const d = new Date(currentDate);
      d.setDate(d.getDate() + 7);
      setCurrentDate(d);
    } else {
      setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
    }
  };

  const handleToday = () => {
    setCurrentDate(new Date());
  };

  const handleOpenQuickSchedule = (date?: Date) => {
    setQuickScheduleDate(date || new Date());
    setIsQuickScheduleOpen(true);
  };

  // Cadence Summary Metrics
  const metrics = useMemo(() => {
    const curYear = currentDate.getFullYear();
    const curMonth = currentDate.getMonth();

    let scheduledMonthCount = 0;
    let publishedMonthCount = 0;
    let next7DaysCount = 0;
    const platformsSet = new Set<string>();

    const now = Date.now();
    const sevenDaysFromNow = now + 7 * 24 * 60 * 60 * 1000;

    posts.forEach(p => {
      if (p.platform) platformsSet.add(p.platform.toUpperCase());

      if (p.scheduled_for) {
        const pDate = new Date(p.scheduled_for);
        const pTime = pDate.getTime();

        if (pDate.getFullYear() === curYear && pDate.getMonth() === curMonth) {
          if (p.status === 'SCHEDULED') scheduledMonthCount++;
          if (p.status === 'PUBLISHED') publishedMonthCount++;
        }

        if (p.status === 'SCHEDULED' && pTime >= now && pTime <= sevenDaysFromNow) {
          next7DaysCount++;
        }
      }
    });

    return {
      scheduledMonth: scheduledMonthCount,
      publishedMonth: publishedMonthCount,
      upcomingNext7: next7DaysCount,
      activePlatforms: platformsSet.size,
    };
  }, [posts, currentDate]);

  // Filtered Posts
  const filteredPosts = useMemo(() => {
    return posts.filter(post => {
      // 1. Platform filter
      if (selectedPlatform !== 'ALL') {
        const postPlat = (post.platform || '').toUpperCase();
        if (!postPlat.includes(selectedPlatform)) return false;
      }

      // 2. Status filter
      if (selectedStatus !== 'ALL') {
        if (post.status !== selectedStatus) return false;
      }

      // 3. Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const titleMatch = (post.title || '').toLowerCase().includes(query);
        const contentMatch = (post.content || '').toLowerCase().includes(query);
        const projectMatch = (post.projectName || '').toLowerCase().includes(query);
        if (!titleMatch && !contentMatch && !projectMatch) return false;
      }

      return true;
    });
  }, [posts, selectedPlatform, selectedStatus, searchQuery]);

  // Date title formatter
  const dateTitle = useMemo(() => {
    const monthNames = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ];

    if (viewMode === 'week') {
      const start = new Date(currentDate);
      start.setDate(currentDate.getDate() - currentDate.getDay());
      const end = new Date(start);
      end.setDate(start.getDate() + 6);

      if (start.getMonth() === end.getMonth()) {
        return `${monthNames[start.getMonth()]} ${start.getDate()} – ${end.getDate()}, ${start.getFullYear()}`;
      }
      return `${monthNames[start.getMonth()]} ${start.getDate()} – ${monthNames[end.getMonth()]} ${end.getDate()}, ${end.getFullYear()}`;
    }

    return `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
  }, [currentDate, viewMode]);

  if (!activeWorkspace) {
    return (
      <div className={styles.container}>
        <div className={styles.calendarCard}>
          <div className={styles.errorState}>
            <AlertCircle size={36} className="mb-3 text-rose-400" />
            <h3 className="font-semibold text-lg text-white">No workspace selected</h3>
            <p className="mt-2 text-slate-400">Please select an active workspace from the sidebar to access your calendar.</p>
          </div>
        </div>
      </div>
    );
  }

  const platformButtons = [
    { id: 'ALL', label: 'All Platforms', icon: <Share2 size={12} /> },
    { id: 'INSTA', label: 'Instagram', icon: <RealBrandLogo platform="INSTAGRAM" size={13} /> },
    { id: 'LINKED', label: 'LinkedIn', icon: <RealBrandLogo platform="LINKEDIN" size={13} /> },
    { id: 'YOUTUBE', label: 'YouTube', icon: <RealBrandLogo platform="YOUTUBE" size={13} /> },
    { id: 'TIKTOK', label: 'TikTok', icon: <RealBrandLogo platform="TIKTOK" size={13} /> },
    { id: 'X', label: 'X', icon: <RealBrandLogo platform="X" size={13} /> },
  ];

  return (
    <div className={styles.container}>
      {/* Unified Top Header & Cadence Ribbon */}
      <div className={styles.calendarHeaderCard}>
        <div className={styles.headerTitleGroup}>
          <div className={styles.mainTitleRow}>
            <h1 className={styles.mainTitle}>Content Calendar</h1>
            <span className={styles.liveCountPill}>
              {posts.length} {posts.length === 1 ? 'post scheduled' : 'posts scheduled'}
            </span>
          </div>
          <p className={styles.mainSubtitle}>
            Publishing cadence, cross-platform release schedule, and multi-market distribution
          </p>
        </div>

        {/* Compact Cadence Stat Pills */}
        <div className={styles.statPillsStrip}>
          <div className={styles.statPill} title="Posts scheduled this month">
            <span className={styles.statIconWrap} style={{ color: '#fbbf24' }}>
              <Clock size={15} />
            </span>
            <span className={styles.statPillValue}>{metrics.scheduledMonth}</span>
            <span className={styles.statPillLabel}>Scheduled</span>
          </div>

          <div className={styles.statPill} title="Posts published this month">
            <span className={styles.statIconWrap} style={{ color: '#34d399' }}>
              <CheckCircle2 size={15} />
            </span>
            <span className={styles.statPillValue}>{metrics.publishedMonth}</span>
            <span className={styles.statPillLabel}>Published</span>
          </div>

          <div className={styles.statPill} title="Posts scheduled in the next 7 days">
            <span className={styles.statIconWrap} style={{ color: '#818cf8' }}>
              <Zap size={15} />
            </span>
            <span className={styles.statPillValue}>{metrics.upcomingNext7}</span>
            <span className={styles.statPillLabel}>Next 7 Days</span>
          </div>

          <div className={styles.statPill} title="Active publishing platforms">
            <span className={styles.statIconWrap} style={{ color: '#f472b6' }}>
              <Share2 size={15} />
            </span>
            <span className={styles.statPillValue}>{metrics.activePlatforms}</span>
            <span className={styles.statPillLabel}>Channels</span>
          </div>
        </div>

        {/* Header Action Buttons */}
        <div className={styles.headerActionsGroup}>
          {projects.length > 0 && (
            <button 
              type="button" 
              className={styles.sampleCampaignBtn}
              onClick={handlePopulateSamplePosts}
              disabled={isPopulatingDemo}
              title="Populate 5 multi-platform campaign posts with real photography"
            >
              <Sparkles size={14} className="text-indigo-400" />
              <span>{isPopulatingDemo ? 'Adding Posts...' : 'Sample Campaign'}</span>
            </button>
          )}

          <button
            type="button"
            className={styles.primaryScheduleBtn}
            onClick={() => handleOpenQuickSchedule()}
          >
            <Plus size={15} />
            <span>Schedule Post</span>
          </button>
        </div>
      </div>

      {/* Main Interactive Calendar Card */}
      <div className={styles.calendarCard}>
        {/* Navigation & Controls Command Bar */}
        <div className={styles.controlCommandBar}>
          {/* Date Navigator */}
          <div className={styles.dateNavCluster}>
            <h2 className={styles.dateNavTitle}>{dateTitle}</h2>

            <div className={styles.navArrowGroup}>
              <button 
                type="button" 
                className={styles.navArrowBtn} 
                onClick={handlePrev}
                title="Previous period"
              >
                <ChevronLeft size={15} />
              </button>
              <button 
                type="button" 
                className={styles.navArrowBtn} 
                onClick={handleNext}
                title="Next period"
              >
                <ChevronRight size={15} />
              </button>
            </div>

            <button 
              type="button" 
              className={styles.todayBtn} 
              onClick={handleToday}
            >
              Today
            </button>

            <button 
              type="button" 
              className={styles.refreshIconBtn} 
              onClick={fetchCalendarData} 
              disabled={isLoading}
              title="Refresh calendar"
            >
              <RefreshCw 
                size={14} 
                className={isLoading ? styles.spinner : ''} 
              />
            </button>
          </div>

          {/* Segmented View Switcher */}
          <div className={styles.viewSwitcher}>
            <button
              type="button"
              className={`${styles.viewTabBtn} ${viewMode === 'month' ? styles.viewTabActive : ''}`}
              onClick={() => setViewMode('month')}
            >
              <LayoutGrid size={13} />
              <span>Month</span>
            </button>

            <button
              type="button"
              className={`${styles.viewTabBtn} ${viewMode === 'week' ? styles.viewTabActive : ''}`}
              onClick={() => setViewMode('week')}
            >
              <CalendarDays size={13} />
              <span>Week</span>
            </button>

            <button
              type="button"
              className={`${styles.viewTabBtn} ${viewMode === 'agenda' ? styles.viewTabActive : ''}`}
              onClick={() => setViewMode('agenda')}
            >
              <ListFilter size={13} />
              <span>Agenda</span>
            </button>
          </div>
        </div>

        {/* Platform & Filter Secondary Bar */}
        <div className={styles.filterSecondaryBar}>
          <div className={styles.platformPillsFilter}>
            {platformButtons.map(btn => (
              <button
                type="button"
                key={btn.id}
                className={`${styles.filterPill} ${selectedPlatform === btn.id ? styles.filterPillActive : ''}`}
                onClick={() => setSelectedPlatform(btn.id)}
              >
                {btn.icon}
                <span>{btn.label}</span>
              </button>
            ))}
          </div>

          <div className={styles.filterRightControls}>
            {/* Search */}
            <div className={styles.searchInputWrapper}>
              <Search size={13} className={styles.searchIcon} />
              <input
                type="text"
                placeholder="Search posts..."
                className={styles.searchInput}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Status Dropdown */}
            <select
              className={styles.statusSelect}
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="SCHEDULED">Scheduled Only</option>
              <option value="PUBLISHED">Published Only</option>
              <option value="APPROVED">Ready / Approved</option>
            </select>
          </div>
        </div>

        {/* Empty Calendar Quick-Start Banner */}
        {posts.length === 0 && !isLoading && (
          <div className={styles.emptyStateBanner}>
            <div className={styles.emptyBannerLeft}>
              <div className={styles.emptyBannerIcon}>
                <Rocket size={18} />
              </div>
              <div>
                <h4 className={styles.emptyBannerTitle}>Your Content Calendar is ready to launch</h4>
                <p className={styles.emptyBannerText}>
                  Click any day cell to schedule, or click below to populate 5 multi-platform campaign posts with real photography.
                </p>
              </div>
            </div>

            {projects.length > 0 && (
              <button
                type="button"
                className={styles.emptyBannerActionBtn}
                onClick={handlePopulateSamplePosts}
                disabled={isPopulatingDemo}
              >
                <Sparkles size={14} />
                <span>{isPopulatingDemo ? 'Adding Campaign...' : 'Load Sample Campaign'}</span>
              </button>
            )}
          </div>
        )}

        {/* View Content */}
        {error ? (
          <div className={styles.errorState}>
            <AlertCircle size={30} className="mb-2 text-rose-400" />
            <p className="font-medium text-rose-300">{error}</p>
            <button 
              type="button" 
              className={styles.todayBtn} 
              style={{ marginTop: '0.75rem' }} 
              onClick={fetchCalendarData}
            >
              Retry
            </button>
          </div>
        ) : (
          <>
            {viewMode === 'month' && (
              <MonthView
                currentDate={currentDate}
                posts={filteredPosts}
                onSelectPost={(post) => setSelectedPostForDetail(post)}
                onSelectDate={(date) => handleOpenQuickSchedule(date)}
              />
            )}

            {viewMode === 'week' && (
              <WeekView
                currentDate={currentDate}
                posts={filteredPosts}
                onSelectPost={(post) => setSelectedPostForDetail(post)}
                onSelectDate={(date) => handleOpenQuickSchedule(date)}
              />
            )}

            {viewMode === 'agenda' && (
              <AgendaView
                posts={filteredPosts}
                onSelectPost={(post) => setSelectedPostForDetail(post)}
                onQuickSchedule={() => handleOpenQuickSchedule()}
              />
            )}
          </>
        )}
      </div>

      {/* Post Detail & Reschedule Modal */}
      {selectedPostForDetail && (
        <PostDetailModal
          post={selectedPostForDetail}
          onClose={() => setSelectedPostForDetail(null)}
          onPostUpdated={fetchCalendarData}
        />
      )}

      {/* Quick Schedule Modal */}
      {isQuickScheduleOpen && (
        <QuickScheduleModal
          initialDate={quickScheduleDate}
          projects={projects}
          onClose={() => {
            setIsQuickScheduleOpen(false);
            setQuickScheduleDate(null);
          }}
          onPostCreated={fetchCalendarData}
        />
      )}
    </div>
  );
}
