import { useState } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Post } from '../../../types';
import { CheckCircle2, XCircle } from 'lucide-react';

interface PostApprovalProps {
  post: Post;
  onSubmitReview: () => Promise<void>;
  onApprove: () => Promise<void>;
  onReject: (reason: string) => Promise<void>;
  isLoading: boolean;
}

export function PostApproval({ post, onSubmitReview, onApprove, onReject, isLoading }: PostApprovalProps) {
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectInput, setShowRejectInput] = useState(false);

  const handleReject = () => {
    if (!rejectReason.trim()) {
      alert("Please provide a rejection reason.");
      return;
    }
    if (confirm("Are you sure you want to reject this post?")) {
      onReject(rejectReason);
    }
  };

  if (post.status === 'DRAFT' || post.status === 'REJECTED') {
    return (
      <Card glass>
        <CardHeader title="Review Workflow" />
        <CardContent>
          {post.status === 'REJECTED' && (
            <div className="mb-4 p-3 bg-danger/10 border border-danger/20 rounded-md">
              <p className="text-sm font-bold text-danger flex items-center gap-2">
                <XCircle size={16} /> Post Rejected
              </p>
              <p className="text-sm text-danger mt-1">{post.rejection_reason}</p>
            </div>
          )}
          <p className="text-sm text-secondary mb-4">
            When you are ready, submit this post for managerial review.
          </p>
          <Button variant="primary" onClick={onSubmitReview} isLoading={isLoading}>
            Submit for Review
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (post.status === 'PENDING_REVIEW') {
    return (
      <Card glass>
        <CardHeader title="Review Post" />
        <CardContent>
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <Button variant="primary" onClick={onApprove} isLoading={isLoading}>
                <CheckCircle2 size={16} className="mr-2" /> Approve
              </Button>
              <Button variant="outline" onClick={() => setShowRejectInput(!showRejectInput)}>
                <XCircle size={16} className="mr-2 text-danger" /> Reject
              </Button>
            </div>

            {showRejectInput && (
              <div className="flex flex-col gap-2 mt-2 p-4 bg-surface border border-border rounded-md">
                <label className="text-sm font-medium">Rejection Reason</label>
                <textarea
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm outline-none focus:border-danger min-h-[80px]"
                  value={rejectReason}
                  onChange={e => setRejectReason(e.target.value)}
                  placeholder="Explain what needs to be changed..."
                />
                <div className="flex justify-end">
                  <Button variant="danger" onClick={handleReject} isLoading={isLoading}>
                    Confirm Reject
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return null; // Don't show approval card for APPROVED/SCHEDULED/PUBLISHED
}
