import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  FolderKanban, 
  Plus, 
  Search, 
  LayoutGrid, 
  List, 
  Trash2, 
  Calendar, 
  Send, 
  FileText, 
  CheckCircle2, 
  Clock, 
  Sparkles,
  Loader2
} from 'lucide-react';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { projectService } from '../../services/api/projectService';
import { postManagementService } from '../../services/api/postManagementService';
import { Project, Post } from '../../types';
import { RealBrandLogo } from '../../components/common/BrandLogos';
import { Badge } from '../../components/ui/Badge';
import styles from './ContentLibrary.module.css';

const PLATFORMS = ['ALL', 'INSTAGRAM', 'LINKEDIN', 'YOUTUBE', 'X', 'TIKTOK'];
const STATUSES = ['ALL', 'DRAFT', 'PENDING_REVIEW', 'APPROVED', 'SCHEDULED', 'PUBLISHED'];

const SAMPLE_CAMPAIGN_POSTS = [
  {
    title: "10 Lessons Building an Autonomous Creator Engine",
    content: "Most founders fail to distribute because they treat social media as an afterthought.\n\nHere is how we automate 80% of our distribution workflow using 10 specialized AI agents:\n\n1. Strategy first: Map exact persona bottlenecks\n2. Trend intelligence: Monitor real-time engagement spikes\n3. Tone enforcement: Check against our Brand Kit rules before publishing\n\nWhat is your biggest distribution bottleneck right now?",
    platform: "LINKEDIN",
    status: "DRAFT" as const,
  },
  {
    title: "Visual Breakdown: 2026 Modern Creator Tech Stack",
    content: "Swipe through our full breakdown of the tools that power top-tier 7-figure creator operations. Minimal friction, maximal leverage.\n\nSave this for your next workflow redesign! 🚀",
    platform: "INSTAGRAM",
    status: "PENDING_REVIEW" as const,
  },
  {
    title: "Why Consistency Beats Virality for Tech Founders",
    content: "1 viral post gives you 24 hours of vanity attention.\n\n365 days of relentless, high-signal consistency gives you distribution dominance.\n\nChoose compounds over spikes every single time.",
    platform: "X",
    status: "APPROVED" as const,
  },
  {
    title: "How We Built a 10-Agent Pipeline in 48 Hours",
    content: "Full walkthrough script showing the LangGraph orchestration flow and automated fact-checking engine.",
    platform: "YOUTUBE",
    status: "SCHEDULED" as const,
    scheduled_for: new Date(Date.now() + 86400000 * 2).toISOString(),
  },
  {
    title: "Behind the Scenes: Autonomous Social Scheduling",
    content: "Watch how 1 master asset turns into 5 platform-native releases automatically in under 60 seconds.",
    platform: "TIKTOK",
    status: "PUBLISHED" as const,
  }
];

export function ContentLibrary() {
  const { activeWorkspace } = useWorkspaceStore();
  const navigate = useNavigate();

  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('ALL');
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isSeeding, setIsSeeding] = useState(false);

  // 1. Fetch Projects for active workspace
  useEffect(() => {
    if (!activeWorkspace) return;
    projectService.getProjects(activeWorkspace.id)
      .then(data => {
        setProjects(data);
      })
      .catch(() => {});
  }, [activeWorkspace]);

  // 2. Fetch Posts for workspace projects
  const fetchAllPosts = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    try {
      const projs = await projectService.getProjects(activeWorkspace.id);
      setProjects(projs);

      let allFetchedPosts: Post[] = [];
      for (const p of projs) {
        try {
          const projectPosts = await postManagementService.getPosts(p.id);
          allFetchedPosts = [...allFetchedPosts, ...projectPosts];
        } catch {
          // ignore individual project failures
        }
      }
      setPosts(allFetchedPosts);
    } catch {
      // ignore
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAllPosts();
  }, [activeWorkspace?.id]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Actions
  const handleSubmitReview = async (post: Post) => {
    try {
      await postManagementService.submitForReview(post.project_id, post.id);
      showToast('Post submitted to Approval Center!');
      fetchAllPosts();
    } catch (err: any) {
      showToast(err?.message || 'Failed to submit review');
    }
  };

  const handleDeletePost = async (post: Post) => {
    if (!window.confirm('Delete this post permanently?')) return;
    try {
      await postManagementService.deletePost(post.project_id, post.id);
      showToast('Post deleted.');
      setPosts(prev => prev.filter(p => p.id !== post.id));
    } catch (err: any) {
      showToast(err?.message || 'Failed to delete post');
    }
  };

  const handleSeedSampleCampaign = async () => {
    if (!activeWorkspace) return;
    setIsSeeding(true);
    try {
      let targetProjectId = projects[0]?.id;
      if (!targetProjectId) {
        const newProj = await projectService.createProject(activeWorkspace.id, {
          name: 'Main Content Engine',
          description: 'Autonomous multi-channel distribution campaign'
        });
        targetProjectId = newProj.id;
      }

      for (const item of SAMPLE_CAMPAIGN_POSTS) {
        await postManagementService.createPost(targetProjectId, item);
      }
      showToast('Created 5-post Sample Campaign!');
      await fetchAllPosts();
    } catch (err: any) {
      showToast(err?.message || 'Failed to seed sample posts');
    } finally {
      setIsSeeding(false);
    }
  };

  // Filtered Posts
  const filteredPosts = useMemo(() => {
    return posts.filter(post => {
      if (selectedProjectId !== 'ALL' && post.project_id !== selectedProjectId) return false;
      if (selectedPlatform !== 'ALL' && post.platform.toUpperCase() !== selectedPlatform) return false;
      if (selectedStatus !== 'ALL' && post.status !== selectedStatus) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = post.title?.toLowerCase().includes(q);
        const matchContent = post.content?.toLowerCase().includes(q);
        if (!matchTitle && !matchContent) return false;
      }
      return true;
    });
  }, [posts, selectedProjectId, selectedPlatform, selectedStatus, searchQuery]);

  // Metric counts
  const stats = useMemo(() => {
    return {
      total: posts.length,
      drafts: posts.filter(p => p.status === 'DRAFT').length,
      review: posts.filter(p => p.status === 'PENDING_REVIEW').length,
      approved: posts.filter(p => p.status === 'APPROVED').length,
      scheduled: posts.filter(p => p.status === 'SCHEDULED').length,
      published: posts.filter(p => p.status === 'PUBLISHED').length,
    };
  }, [posts]);

  const getStatusBadge = (status: Post['status']) => {
    switch (status) {
      case 'PUBLISHED': return <Badge variant="success">Published</Badge>;
      case 'SCHEDULED': return <Badge variant="info">Scheduled</Badge>;
      case 'APPROVED': return <Badge variant="primary">Approved</Badge>;
      case 'PENDING_REVIEW': return <Badge variant="warning">In Review</Badge>;
      case 'REJECTED': return <Badge variant="danger">Revision</Badge>;
      default: return <Badge variant="secondary">Draft</Badge>;
    }
  };

  return (
    <div className={styles.container}>
      {/* Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-xl shadow-2xl border border-indigo-400 font-semibold text-xs animate-bounce">
          <CheckCircle2 size={15} />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header Card */}
      <div className={styles.headerCard}>
        <div className={styles.headerLeft}>
          <span className={styles.headerBadge}>
            <FolderKanban size={13} /> Asset Repository
          </span>
          <h1 className={styles.headerTitle}>Content Library</h1>
          <p className={styles.headerSubtitle}>
            Organize, audit, and distribute all drafted and published assets across your channels.
          </p>
        </div>

        <div className={styles.headerActions}>
          {posts.length === 0 && (
            <button
              type="button"
              className={styles.secondaryActionBtn}
              onClick={handleSeedSampleCampaign}
              disabled={isSeeding}
            >
              <Sparkles size={14} className="text-amber-400" />
              <span>{isSeeding ? 'Generating...' : 'Seed Sample Campaign'}</span>
            </button>
          )}

          <Link to="/create">
            <button type="button" className={styles.primaryActionBtn}>
              <Plus size={15} /> Create in Studio
            </button>
          </Link>
        </div>
      </div>

      {/* Stat Ribbon */}
      <div className={styles.statRibbon}>
        <div className={styles.statPillCard}>
          <div className={styles.statIconWrap} style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            <FileText size={16} />
          </div>
          <div className={styles.statContent}>
            <span className={styles.statLabel}>Total Assets</span>
            <span className={styles.statNumber}>{stats.total}</span>
          </div>
        </div>

        <div className={styles.statPillCard}>
          <div className={styles.statIconWrap} style={{ background: 'rgba(148, 163, 184, 0.15)', color: '#94a3b8' }}>
            <FileText size={16} />
          </div>
          <div className={styles.statContent}>
            <span className={styles.statLabel}>Drafts</span>
            <span className={styles.statNumber}>{stats.drafts}</span>
          </div>
        </div>

        <div className={styles.statPillCard}>
          <div className={styles.statIconWrap} style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <Clock size={16} />
          </div>
          <div className={styles.statContent}>
            <span className={styles.statLabel}>Pending Review</span>
            <span className={styles.statNumber}>{stats.review}</span>
          </div>
        </div>

        <div className={styles.statPillCard}>
          <div className={styles.statIconWrap} style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
            <CheckCircle2 size={16} />
          </div>
          <div className={styles.statContent}>
            <span className={styles.statLabel}>Approved</span>
            <span className={styles.statNumber}>{stats.approved}</span>
          </div>
        </div>

        <div className={styles.statPillCard}>
          <div className={styles.statIconWrap} style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' }}>
            <Calendar size={16} />
          </div>
          <div className={styles.statContent}>
            <span className={styles.statLabel}>Scheduled</span>
            <span className={styles.statNumber}>{stats.scheduled}</span>
          </div>
        </div>

        <div className={styles.statPillCard}>
          <div className={styles.statIconWrap} style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <CheckCircle2 size={16} />
          </div>
          <div className={styles.statContent}>
            <span className={styles.statLabel}>Published</span>
            <span className={styles.statNumber}>{stats.published}</span>
          </div>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className={styles.toolbarCard}>
        <div className={styles.toolbarTopRow}>
          {/* Search */}
          <div className={styles.searchWrap}>
            <Search size={15} className={styles.searchIcon} />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Search posts by title, hook, or hashtag..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Campaign Selector */}
          {projects.length > 0 && (
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="bg-[var(--panel-2)] border border-white/10 rounded-lg px-3 py-2 text-xs font-semibold text-slate-300 outline-none"
            >
              <option value="ALL">All Campaigns</option>
              {projects.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          )}

          {/* View Toggle */}
          <div className={styles.viewModeToggle}>
            <button
              type="button"
              className={`${styles.viewToggleBtn} ${viewMode === 'grid' ? styles.viewToggleActive : ''}`}
              onClick={() => setViewMode('grid')}
              title="Grid View"
            >
              <LayoutGrid size={15} />
            </button>
            <button
              type="button"
              className={`${styles.viewToggleBtn} ${viewMode === 'table' ? styles.viewToggleActive : ''}`}
              onClick={() => setViewMode('table')}
              title="Table View"
            >
              <List size={15} />
            </button>
          </div>
        </div>

        <div className={styles.toolbarFiltersRow}>
          {/* Platform Pills */}
          <div className={styles.platformPillsCluster}>
            {PLATFORMS.map(p => (
              <button
                type="button"
                key={p}
                className={`${styles.platformPill} ${selectedPlatform === p ? styles.platformPillActive : ''}`}
                onClick={() => setSelectedPlatform(p)}
              >
                {p !== 'ALL' && <RealBrandLogo platform={p} size={13} />}
                <span>{p === 'ALL' ? 'All Channels' : p.charAt(0) + p.slice(1).toLowerCase()}</span>
              </button>
            ))}
          </div>

          {/* Status Tabs */}
          <div className={styles.statusTabsCluster}>
            {STATUSES.map(s => (
              <button
                type="button"
                key={s}
                className={`${styles.statusTabBtn} ${selectedStatus === s ? styles.statusTabActive : ''}`}
                onClick={() => setSelectedStatus(s)}
              >
                {s === 'ALL' ? 'All Statuses' : s.replace('_', ' ').toLowerCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center p-16 text-slate-400">
          <Loader2 size={32} className="spinner mb-2 text-indigo-400" />
          <p className="text-sm">Loading your content library...</p>
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className={styles.emptyStateCard}>
          <div className={styles.emptyIconWrap}>
            <FolderKanban size={26} />
          </div>
          <h3 className={styles.emptyTitle}>
            {posts.length === 0 ? 'Your Content Library is Empty' : 'No posts match your active filter'}
          </h3>
          <p className={styles.emptySubtitle}>
            {posts.length === 0 
              ? 'Draft high-impact posts with the 3D Create Studio or populate a sample campaign to preview library workflows.'
              : 'Try selecting a different channel, status, or clearing your search keywords.'}
          </p>
          <div className={styles.emptyActionsRow}>
            {posts.length === 0 && (
              <button
                type="button"
                className={styles.secondaryActionBtn}
                onClick={handleSeedSampleCampaign}
                disabled={isSeeding}
              >
                <Sparkles size={14} className="text-amber-400" />
                <span>{isSeeding ? 'Populating...' : 'Seed Sample Campaign (5 Posts)'}</span>
              </button>
            )}
            <Link to="/create">
              <button type="button" className={styles.primaryActionBtn}>
                <Plus size={14} /> Draft in Studio
              </button>
            </Link>
          </div>
        </div>
      ) : viewMode === 'grid' ? (
        <div className={styles.postsGrid}>
          {filteredPosts.map(post => (
            <div key={post.id} className={styles.postCard}>
              <div>
                <div className={styles.postCardHeader}>
                  <div className={styles.postCardPlatformWrap}>
                    <div className={styles.platformIconBadge}>
                      <RealBrandLogo platform={post.platform} size={15} />
                    </div>
                    <span className={styles.postPlatformName}>
                      {post.platform.toLowerCase()}
                    </span>
                  </div>
                  {getStatusBadge(post.status)}
                </div>

                <div className={styles.postMainContent} style={{ marginTop: '0.85rem' }}>
                  <h4 className={styles.postTitle}>{post.title || 'Untitled Post'}</h4>
                  <p className={styles.postSnippet}>{post.content}</p>
                </div>
              </div>

              <div className={styles.postFooter}>
                <span className={styles.postTimestamp}>
                  <Clock size={11} /> {new Date(post.updated_at).toLocaleDateString()}
                </span>

                <div className={styles.postActionsCluster}>
                  {post.status === 'DRAFT' && (
                    <button
                      type="button"
                      className={styles.postActionBtn}
                      onClick={() => handleSubmitReview(post)}
                      title="Submit for Review"
                    >
                      <Send size={11} /> Review
                    </button>
                  )}

                  <button
                    type="button"
                    className={styles.postActionBtn}
                    onClick={() => navigate('/calendar')}
                    title="View on Calendar"
                  >
                    <Calendar size={11} />
                  </button>

                  <button
                    type="button"
                    className={`${styles.postActionBtn} ${styles.deleteActionBtn}`}
                    onClick={() => handleDeletePost(post)}
                    title="Delete Post"
                  >
                    <Trash2 size={11} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className={styles.tableViewCard}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Platform</th>
                <th>Title / Headline</th>
                <th>Status</th>
                <th>Scheduled Date</th>
                <th>Updated</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPosts.map(post => (
                <tr key={post.id}>
                  <td>
                    <div className="flex items-center gap-2">
                      <RealBrandLogo platform={post.platform} size={15} />
                      <span className="capitalize font-semibold text-xs">{post.platform.toLowerCase()}</span>
                    </div>
                  </td>
                  <td>
                    <div className="flex flex-col max-w-sm">
                      <span className="font-semibold text-white truncate">{post.title || 'Untitled Post'}</span>
                      <span className="text-xs text-slate-400 truncate">{post.content}</span>
                    </div>
                  </td>
                  <td>{getStatusBadge(post.status)}</td>
                  <td>
                    {post.scheduled_for 
                      ? new Date(post.scheduled_for).toLocaleDateString()
                      : <span className="text-slate-500 text-xs">Unscheduled</span>}
                  </td>
                  <td className="text-xs text-slate-400">
                    {new Date(post.updated_at).toLocaleDateString()}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div className="inline-flex items-center gap-2">
                      {post.status === 'DRAFT' && (
                        <button
                          type="button"
                          className={styles.postActionBtn}
                          onClick={() => handleSubmitReview(post)}
                          title="Submit for Review"
                        >
                          <Send size={11} />
                        </button>
                      )}
                      <button
                        type="button"
                        className={`${styles.postActionBtn} ${styles.deleteActionBtn}`}
                        onClick={() => handleDeletePost(post)}
                        title="Delete Post"
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
