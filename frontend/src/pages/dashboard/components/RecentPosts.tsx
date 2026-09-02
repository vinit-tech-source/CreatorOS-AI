import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { FileText, ArrowUpRight } from 'lucide-react';
import { Post } from '../../../types';
import { RealBrandLogo } from '../../../components/common/BrandLogos';

interface RecentPostsProps {
  posts: Post[];
}

export function RecentPosts({ posts }: RecentPostsProps) {
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
    <Card glass>
      <CardHeader 
        title="Recent Activity & Content" 
        subtitle="Latest drafts and published assets" 
        action={
          <Link to="/content">
            <Button variant="outline" size="sm">
              <FileText size={13} className="mr-1.5" /> All Content
            </Button>
          </Link>
        }
      />
      <CardContent className="p-0">
        {posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
            <FileText size={32} className="text-slate-500 mb-2 opacity-60" />
            <p className="text-sm font-semibold text-slate-300">No content found in this workspace</p>
            <p className="text-xs text-slate-500 mt-1 mb-3">
              Use the AI Idea Canvas or Create Studio to draft your first asset.
            </p>
            <Link to="/create">
              <Button size="sm">Open Create Studio</Button>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {posts.slice(0, 5).map(post => (
              <div key={post.id} className="p-3.5 hover:bg-white/[0.02] flex items-center justify-between transition-colors">
                <div className="flex items-center gap-3 min-w-0 pr-4">
                  <div className="p-1.5 rounded-lg bg-white/5 border border-white/10 flex-shrink-0">
                    <RealBrandLogo platform={post.platform} size={15} />
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-sm font-semibold text-white truncate max-w-xs md:max-w-md">
                      {post.title || post.content}
                    </span>
                    <span className="text-xs text-slate-400">
                      Updated {new Date(post.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0">
                  {getStatusBadge(post.status)}
                  <Link 
                    to="/create" 
                    className="text-slate-400 hover:text-white p-1 rounded hover:bg-white/10 transition-colors"
                    title="Open in Studio"
                  >
                    <ArrowUpRight size={15} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
