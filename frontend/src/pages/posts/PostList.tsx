import { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table';
import { Badge } from '../../components/ui/Badge';
import { PenTool, Plus, Search, Filter } from 'lucide-react';
import { Post } from '../../types';
import { postManagementService } from '../../services/api/postManagementService';

export function PostList() {
  const { workspaceId, projectId } = useParams<{ workspaceId: string, projectId: string }>();
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [platformFilter, setPlatformFilter] = useState('');
  
  // Sort
  const [sortBy, setSortBy] = useState<'updated_at' | 'created_at'>('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    if (!projectId) return;

    const fetchPosts = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await postManagementService.getPosts(projectId);
        setPosts(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load posts');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPosts();
  }, [projectId]);

  const filteredAndSortedPosts = useMemo(() => {
    let result = [...posts];

    // Search
    if (search) {
      const lowerSearch = search.toLowerCase();
      result = result.filter(p => 
        (p.title && p.title.toLowerCase().includes(lowerSearch)) || 
        (p.content && p.content.toLowerCase().includes(lowerSearch))
      );
    }

    // Filters
    if (statusFilter) {
      result = result.filter(p => p.status === statusFilter);
    }
    if (platformFilter) {
      result = result.filter(p => p.platform === platformFilter);
    }

    // Sort
    result.sort((a, b) => {
      const aVal = new Date(a[sortBy]).getTime();
      const bVal = new Date(b[sortBy]).getTime();
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return result;
  }, [posts, search, statusFilter, platformFilter, sortBy, sortOrder]);

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

  const handleSort = (field: 'updated_at' | 'created_at') => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="flex-col gap-6">
      <PageHeader 
        title="Project Posts" 
        subtitle="Manage and track your project's social media content"
        action={
          <Link to={`/workspaces/${workspaceId}/projects/${projectId}/create`}>
            <Button variant="primary">
              <Plus size={16} className="mr-2" /> Create Post
            </Button>
          </Link>
        }
      />

      <Card glass className="mb-6">
        <CardContent className="p-4 flex flex-col md:flex-row gap-4 items-center bg-surface/50 border-b border-border">
          <div className="relative flex-1 w-full">
            <Search size={18} className="absolute left-3 top-2.5 text-secondary" />
            <input 
              type="text" 
              placeholder="Search posts..." 
              className="w-full pl-10 pr-3 py-2 bg-background border border-border rounded-md text-sm outline-none focus:border-primary"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="flex gap-4 w-full md:w-auto">
            <div className="flex items-center gap-2">
              <Filter size={16} className="text-secondary" />
              <select 
                className="px-3 py-2 bg-background border border-border rounded-md text-sm outline-none focus:border-primary"
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="DRAFT">Draft</option>
                <option value="PENDING_REVIEW">Review</option>
                <option value="APPROVED">Approved</option>
                <option value="SCHEDULED">Scheduled</option>
                <option value="PUBLISHED">Published</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <select 
                className="px-3 py-2 bg-background border border-border rounded-md text-sm outline-none focus:border-primary"
                value={platformFilter}
                onChange={e => setPlatformFilter(e.target.value)}
              >
                <option value="">All Platforms</option>
                <option value="X">X (Twitter)</option>
                <option value="LINKEDIN">LinkedIn</option>
                <option value="INSTAGRAM">Instagram</option>
                <option value="FACEBOOK">Facebook</option>
                <option value="THREADS">Threads</option>
                <option value="BLUESKY">Bluesky</option>
              </select>
            </div>
          </div>
        </CardContent>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center p-8 text-secondary">Loading posts...</div>
          ) : error ? (
            <div className="flex justify-center p-8 text-danger">{error}</div>
          ) : filteredAndSortedPosts.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <PenTool size={48} className="opacity-20 mb-4" />
              <p>No posts match your filters.</p>
              {posts.length === 0 && (
                <Link to={`/workspaces/${workspaceId}/projects/${projectId}/create`}>
                  <Button variant="outline" className="mt-4">Draft your first post</Button>
                </Link>
              )}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Content</TableHead>
                  <TableHead>Platform</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>
                    <div className="cursor-pointer hover:text-primary transition-colors flex items-center" onClick={() => handleSort('updated_at')}>
                      Updated {sortBy === 'updated_at' && (sortOrder === 'asc' ? '↑' : '↓')}
                    </div>
                  </TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAndSortedPosts.map((post) => (
                  <TableRow key={post.id}>
                    <TableCell className="font-medium max-w-xs truncate">
                      {post.title || post.content}
                    </TableCell>
                    <TableCell>{post.platform}</TableCell>
                    <TableCell>{getStatusBadge(post.status)}</TableCell>
                    <TableCell>{new Date(post.updated_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Link to={`/workspaces/${workspaceId}/projects/${projectId}/posts/${post.id}`}>
                        <Button variant="ghost" size="sm">Manage</Button>
                      </Link>
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
