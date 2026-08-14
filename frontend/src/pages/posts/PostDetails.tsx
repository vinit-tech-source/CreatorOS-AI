import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardHeader, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { PostEditor } from './components/PostEditor';
import { PostApproval } from './components/PostApproval';
import { PostScheduler } from './components/PostScheduler';
import { Post } from '../../types';
import { postManagementService } from '../../services/api/postManagementService';
import { ArrowLeft, BarChart3, AlertCircle } from 'lucide-react';

export function PostDetails() {
  const { workspaceId, projectId, postId } = useParams<{ workspaceId: string, projectId: string, postId: string }>();
  
  const [post, setPost] = useState<Post | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPost = async () => {
    if (!projectId || !postId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await postManagementService.getPost(projectId, postId);
      setPost(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load post details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPost();
  }, [projectId, postId]);

  const handleAction = async (actionFn: () => Promise<Post>) => {
    setIsActionLoading(true);
    setError(null);
    try {
      const updatedPost = await actionFn();
      setPost(updatedPost);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || err.message || 'Action failed');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleSave = (data: Partial<Post>) => handleAction(() => postManagementService.updatePost(projectId!, postId!, data));
  const handleSubmitReview = () => handleAction(() => postManagementService.submitForReview(projectId!, postId!));
  const handleApprove = () => handleAction(() => postManagementService.approvePost(projectId!, postId!));
  const handleReject = (reason: string) => handleAction(() => postManagementService.rejectPost(projectId!, postId!, reason));
  const handleSchedule = (date: string, timezone: string) => handleAction(() => postManagementService.schedulePost(projectId!, postId!, date, timezone));
  const handleReschedule = (date: string, timezone: string) => handleAction(() => postManagementService.reschedulePost(projectId!, postId!, date, timezone));
  const handleCancelSchedule = () => handleAction(() => postManagementService.cancelSchedule(projectId!, postId!));

  if (isLoading) return <div className="p-8 text-center text-secondary">Loading post details...</div>;
  if (!post) return <div className="p-8 text-center text-danger">Post not found.</div>;

  const getStatusBadge = (status: Post['status']) => {
    switch(status) {
      case 'PUBLISHED': return <Badge variant="success">Published</Badge>;
      case 'SCHEDULED': return <Badge variant="info">Scheduled</Badge>;
      case 'APPROVED': return <Badge variant="primary">Approved</Badge>;
      case 'PENDING_REVIEW': return <Badge variant="warning">Review</Badge>;
      case 'REJECTED': return <Badge variant="danger">Rejected</Badge>;
      default: return <Badge variant="secondary">Draft</Badge>;
    }
  };

  return (
    <div className="flex-col gap-6 w-full max-w-5xl mx-auto">
      <div className="flex items-center gap-4 mb-2">
        <Link to={`/workspaces/${workspaceId}/projects/${projectId}/posts`} className="text-secondary hover:text-primary transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <PageHeader 
          title="Post Details" 
          subtitle="Manage, review, and schedule this post."
        />
      </div>

      {error && (
        <div className="bg-danger/10 text-danger border border-danger/20 p-4 rounded-md mb-6 flex items-start gap-3">
          <AlertCircle size={20} className="mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column - Main Content */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <PostEditor 
            post={post} 
            onSave={handleSave} 
            isSaving={isActionLoading} 
          />
        </div>

        {/* Right Column - Status & Actions */}
        <div className="flex flex-col gap-6">
          
          <Card glass>
            <CardHeader title="Metadata" />
            <CardContent>
              <div className="flex flex-col gap-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary">Status</span>
                  {getStatusBadge(post.status)}
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-secondary">Platform</span>
                  <span className="text-sm font-semibold">{post.platform}</span>
                </div>
                {post.published_at && (
                  <div className="flex flex-col gap-1 mt-2 p-3 bg-success/10 border border-success/20 rounded-md">
                    <span className="text-xs font-bold text-success">Published</span>
                    <span className="text-sm text-success">{new Date(post.published_at).toLocaleString()}</span>
                  </div>
                )}
                {post.status === 'PUBLISHED' && (
                  <Link to={`/workspaces/${workspaceId}/projects/${projectId}/posts/${postId}/analytics`} className="mt-2">
                    <Button variant="outline" fullWidth>
                      <BarChart3 size={16} className="mr-2" /> View Analytics
                    </Button>
                  </Link>
                )}
              </div>
            </CardContent>
          </Card>

          <PostApproval 
            post={post}
            onSubmitReview={handleSubmitReview}
            onApprove={handleApprove}
            onReject={handleReject}
            isLoading={isActionLoading}
          />

          <PostScheduler 
            post={post}
            onSchedule={handleSchedule}
            onReschedule={handleReschedule}
            onCancelSchedule={handleCancelSchedule}
            isLoading={isActionLoading}
          />

        </div>
      </div>
    </div>
  );
}
