import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table';
import { Badge } from '../../components/ui/Badge';
import { PenTool, Plus } from 'lucide-react';
import { Post } from '../../types';

export function Posts() {
  const [posts, _setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Placeholder fetching logic
    setTimeout(() => {
      setIsLoading(false);
    }, 500);
  }, []);

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
    <div className="flex-col gap-6">
      <PageHeader 
        title="Posts" 
        subtitle="Manage your social media content workflow"
        action={
          <Button>
            <Plus size={16} /> Create Post
          </Button>
        }
      />

      <Card glass>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center p-8 text-secondary">Loading posts...</div>
          ) : posts.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <PenTool size={48} className="opacity-20 mb-4" />
              <p>No posts found.</p>
              <Button variant="outline" className="mt-4">Draft your first post</Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Content</TableHead>
                  <TableHead>Platform</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Updated</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {posts.map((post) => (
                  <TableRow key={post.id}>
                    <TableCell className="font-medium max-w-xs truncate">
                      {post.title || post.content}
                    </TableCell>
                    <TableCell>{post.platform}</TableCell>
                    <TableCell>{getStatusBadge(post.status)}</TableCell>
                    <TableCell>{new Date(post.updated_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">Edit</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
