import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../../components/ui/Table';
import { Badge } from '../../../components/ui/Badge';
import { Post } from '../../../types';

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
      <CardHeader title="Recent Posts" subtitle="Most recently updated content" />
      <CardContent className="p-0">
        {posts.length === 0 ? (
          <div className="flex justify-center p-8 text-secondary">
            No recent posts found.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title/Content</TableHead>
                <TableHead>Platform</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.map(post => (
                <TableRow key={post.id}>
                  <TableCell className="font-medium max-w-xs truncate">
                    {post.title || post.content}
                  </TableCell>
                  <TableCell>{post.platform}</TableCell>
                  <TableCell>{getStatusBadge(post.status)}</TableCell>
                  <TableCell>{new Date(post.updated_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
