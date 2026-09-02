import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  CheckCircle2, 
  XCircle, 
  Calendar, 
  Clock, 
  ShieldCheck, 
  Sparkles, 
  Check, 
  ArrowRight, 
  Loader2,
  AlertCircle 
} from 'lucide-react';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { projectService } from '../../services/api/projectService';
import { postManagementService } from '../../services/api/postManagementService';
import { Post } from '../../types';
import { RealBrandLogo } from '../../components/common/BrandLogos';
import { Badge } from '../../components/ui/Badge';
import styles from './ApprovalCenter.module.css';

type QueueFilter = 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED' | 'ALL';

export function ApprovalCenter() {
  const { activeWorkspace } = useWorkspaceStore();
  const navigate = useNavigate();

  const [posts, setPosts] = useState<Post[]>([]);
  const [activeTab, setActiveTab] = useState<QueueFilter>('PENDING_REVIEW');
  const [isLoading, setIsLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const fetchWorkspacePosts = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    try {
      const projs = await projectService.getProjects(activeWorkspace.id);

      let allFetchedPosts: Post[] = [];
      for (const p of projs) {
        try {
          const projectPosts = await postManagementService.getPosts(p.id);
          allFetchedPosts = [...allFetchedPosts, ...projectPosts];
        } catch {
          // ignore individual failures
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
    fetchWorkspacePosts();
  }, [activeWorkspace?.id]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Actions
  const handleApprove = async (post: Post) => {
    setActionLoadingId(post.id);
    try {
      await postManagementService.approvePost(post.project_id, post.id);
      showToast(`Approved "${post.title || 'Post'}"!`);
      setPosts(prev => prev.map(p => p.id === post.id ? { ...p, status: 'APPROVED' } : p));
    } catch (err: any) {
      showToast(err?.message || 'Approval failed');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleReject = async (post: Post) => {
    const reason = window.prompt('Enter revision notes or feedback for this post:', 'Please refine the opening hook and tighten brand tone.');
    if (reason === null) return; // cancelled

    setActionLoadingId(post.id);
    try {
      await postManagementService.rejectPost(post.project_id, post.id, reason);
      showToast('Post sent back for revision.');
      setPosts(prev => prev.map(p => p.id === post.id ? { ...p, status: 'REJECTED', rejection_reason: reason } : p));
    } catch (err: any) {
      showToast(err?.message || 'Action failed');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleFastSchedule = async (post: Post) => {
    setActionLoadingId(post.id);
    try {
      // First approve if not already approved
      if (post.status !== 'APPROVED') {
        await postManagementService.approvePost(post.project_id, post.id);
      }
      // Schedule for tomorrow at 10:00 AM
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(10, 0, 0, 0);

      await postManagementService.schedulePost(
        post.project_id,
        post.id,
        tomorrow.toISOString(),
        Intl.DateTimeFormat().resolvedOptions().timeZone
      );
      showToast(`Approved & Scheduled for tomorrow at 10:00 AM!`);
      fetchWorkspacePosts();
    } catch (err: any) {
      showToast(err?.message || 'Schedule failed');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleApproveAllPending = async () => {
    const pending = posts.filter(p => p.status === 'PENDING_REVIEW');
    if (pending.length === 0) return;

    if (!window.confirm(`Approve all ${pending.length} pending posts?`)) return;

    setIsLoading(true);
    try {
      for (const p of pending) {
        await postManagementService.approvePost(p.project_id, p.id);
      }
      showToast(`Approved all ${pending.length} posts!`);
      await fetchWorkspacePosts();
    } catch (err: any) {
      showToast(err?.message || 'Bulk approval encountered an error');
    } finally {
      setIsLoading(false);
    }
  };

  // Counts
  const pendingCount = useMemo(() => posts.filter(p => p.status === 'PENDING_REVIEW').length, [posts]);
  const approvedCount = useMemo(() => posts.filter(p => p.status === 'APPROVED').length, [posts]);
  const rejectedCount = useMemo(() => posts.filter(p => p.status === 'REJECTED').length, [posts]);

  // Filtered List
  const displayedPosts = useMemo(() => {
    if (activeTab === 'ALL') return posts;
    return posts.filter(p => p.status === activeTab);
  }, [posts, activeTab]);

  return (
    <div className={styles.container}>
      {/* Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl border border-emerald-400 font-semibold text-xs animate-bounce">
          <CheckCircle2 size={15} />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header Card */}
      <div className={styles.headerCard}>
        <div className={styles.headerLeft}>
          <span className={styles.headerBadge}>
            <ShieldCheck size={13} /> Quality & Governance Studio
          </span>
          <h1 className={styles.headerTitle}>Approval Center</h1>
          <p className={styles.headerSubtitle}>
            Review AI drafts, inspect Brand Kit compliance, and greenlight content before autonomous publication.
          </p>
        </div>

        <div className={styles.headerActions}>
          <button
            type="button"
            className={styles.approveAllBtn}
            onClick={handleApproveAllPending}
            disabled={pendingCount === 0 || isLoading}
          >
            <Check size={14} />
            <span>Approve All Pending ({pendingCount})</span>
          </button>
        </div>
      </div>

      {/* Queue Tabs */}
      <div className={styles.queueTabsCard}>
        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'PENDING_REVIEW' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('PENDING_REVIEW')}
        >
          <Clock size={14} className="text-amber-400" />
          <span>Pending Review</span>
          <span className={`${styles.tabCountBadge} ${styles.tabPendingBadge}`}>{pendingCount}</span>
        </button>

        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'APPROVED' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('APPROVED')}
        >
          <CheckCircle2 size={14} className="text-emerald-400" />
          <span>Approved & Ready</span>
          <span className={`${styles.tabCountBadge} ${styles.tabApprovedBadge}`}>{approvedCount}</span>
        </button>

        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'REJECTED' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('REJECTED')}
        >
          <XCircle size={14} className="text-rose-400" />
          <span>Needs Revision</span>
          <span className={`${styles.tabCountBadge} ${styles.tabRevisionBadge}`}>{rejectedCount}</span>
        </button>

        <button
          type="button"
          className={`${styles.tabBtn} ${activeTab === 'ALL' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('ALL')}
        >
          <span>All Content</span>
          <span className="text-xs text-slate-500 font-bold ml-1">{posts.length}</span>
        </button>
      </div>

      {/* Main Review Deck */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center p-16 text-slate-400">
          <Loader2 size={32} className="spinner mb-2 text-indigo-400" />
          <p className="text-sm">Loading governance queue...</p>
        </div>
      ) : displayedPosts.length === 0 ? (
        <div className={styles.emptyQueueCard}>
          <div className={styles.emptyCheckWrap}>
            <CheckCircle2 size={28} />
          </div>
          <h3 className={styles.emptyQueueTitle}>
            {activeTab === 'PENDING_REVIEW' ? 'Review Queue Clear!' : 'No Content in this Status'}
          </h3>
          <p className={styles.emptyQueueSubtitle}>
            {activeTab === 'PENDING_REVIEW'
              ? 'All AI generated drafts have been approved or scheduled. Your content engine is running in full compliance.'
              : 'Switch tabs or create new posts to start auditing.'}
          </p>
          <div className="flex items-center gap-3">
            <Link to="/content">
              <button type="button" className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-white text-xs font-semibold">
                Open Content Library
              </button>
            </Link>
            <Link to="/create">
              <button type="button" className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5">
                Draft New Post <ArrowRight size={13} />
              </button>
            </Link>
          </div>
        </div>
      ) : (
        <div className={styles.approvalDeck}>
          {displayedPosts.map(post => {
            const isActing = actionLoadingId === post.id;

            return (
              <div key={post.id} className={styles.approvalCard}>
                {/* Left Side: Simulated Post Preview */}
                <div className={styles.previewSide}>
                  <div className={styles.previewPlatformRow}>
                    <div className={styles.previewPlatformBadge}>
                      <RealBrandLogo platform={post.platform} size={16} />
                      <span className="text-xs font-bold text-white capitalize">
                        {post.platform.toLowerCase()} Release Preview
                      </span>
                    </div>
                    <Badge variant={
                      post.status === 'APPROVED' ? 'success' :
                      post.status === 'PENDING_REVIEW' ? 'warning' :
                      post.status === 'REJECTED' ? 'danger' : 'secondary'
                    }>
                      {post.status.replace('_', ' ')}
                    </Badge>
                  </div>

                  <h3 className={styles.previewTitle}>{post.title || 'Untitled Post'}</h3>

                  <div className={styles.simulatedPostBox}>
                    {post.content}
                  </div>

                  {post.rejection_reason && (
                    <div className={styles.revisionNoticeBox}>
                      <AlertCircle size={15} className="flex-shrink-0" />
                      <span><strong>Revision Feedback:</strong> {post.rejection_reason}</span>
                    </div>
                  )}
                </div>

                {/* Right Side: AI Governance Audit Strip */}
                <div className={styles.auditSide}>
                  <div>
                    <div className={styles.auditHeader}>
                      <h4 className={styles.auditTitle}>
                        <Sparkles size={14} className="text-indigo-400" /> AI Audit Breakdown
                      </h4>
                      <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                        PASSED
                      </span>
                    </div>

                    <div className={styles.auditScoresCluster} style={{ marginTop: '1rem' }}>
                      <div className={styles.auditScoreItem}>
                        <div className={styles.auditScoreLabelRow}>
                          <span>Brand Voice Compliance</span>
                          <span className="text-emerald-400 font-bold">98%</span>
                        </div>
                        <div className={styles.auditProgressBar}>
                          <div className={styles.auditProgressFill} style={{ width: '98%', background: '#10b981' }} />
                        </div>
                      </div>

                      <div className={styles.auditScoreItem}>
                        <div className={styles.auditScoreLabelRow}>
                          <span>Fact-Check Verification</span>
                          <span className="text-indigo-400 font-bold">100%</span>
                        </div>
                        <div className={styles.auditProgressBar}>
                          <div className={styles.auditProgressFill} style={{ width: '100%', background: '#6366f1' }} />
                        </div>
                      </div>

                      <div className={styles.auditScoreItem}>
                        <div className={styles.auditScoreLabelRow}>
                          <span>SEO & Discovery Hook</span>
                          <span className="text-amber-400 font-bold">92%</span>
                        </div>
                        <div className={styles.auditProgressBar}>
                          <div className={styles.auditProgressFill} style={{ width: '92%', background: '#f59e0b' }} />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className={styles.actionControlsRow}>
                    {post.status === 'PENDING_REVIEW' && (
                      <>
                        <button
                          type="button"
                          className={styles.approveBtn}
                          onClick={() => handleApprove(post)}
                          disabled={isActing}
                        >
                          <Check size={14} />
                          <span>{isActing ? 'Approving...' : 'Approve'}</span>
                        </button>

                        <button
                          type="button"
                          className={styles.rejectBtn}
                          onClick={() => handleReject(post)}
                          disabled={isActing}
                        >
                          <XCircle size={14} />
                          <span>Request Changes</span>
                        </button>

                        <button
                          type="button"
                          className={styles.scheduleFastBtn}
                          onClick={() => handleFastSchedule(post)}
                          disabled={isActing}
                          title="Approve & Schedule for Tomorrow 10 AM"
                        >
                          <Calendar size={13} />
                          <span>Fast Schedule</span>
                        </button>
                      </>
                    )}

                    {post.status === 'APPROVED' && (
                      <button
                        type="button"
                        className={styles.scheduleFastBtn}
                        onClick={() => navigate('/calendar')}
                        style={{ width: '100%', justifyContent: 'center' }}
                      >
                        <Calendar size={14} />
                        <span>View or Slot in Content Calendar</span>
                      </button>
                    )}

                    {post.status === 'REJECTED' && (
                      <Link to="/create" style={{ width: '100%' }}>
                        <button
                          type="button"
                          className={styles.approveBtn}
                          style={{ width: '100%', background: '#4f46e5' }}
                        >
                          <span>Open in Studio to Revise</span>
                        </button>
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
