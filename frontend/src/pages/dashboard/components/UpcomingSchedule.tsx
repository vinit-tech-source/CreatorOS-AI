import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../../components/ui/Table';
import { Button } from '../../../components/ui/Button';
import { Post } from '../../../types';

interface UpcomingScheduleProps {
  posts: Post[];
}

export function UpcomingSchedule({ posts }: UpcomingScheduleProps) {
  return (
    <Card glass>
      <CardHeader 
        title="Upcoming Schedule" 
        subtitle="Posts scheduled for publication"
        action={
          <Link to="/posts">
            <Button variant="outline" size="sm">View Schedule</Button>
          </Link>
        }
      />
      <CardContent className="p-0">
        {posts.length === 0 ? (
          <div className="flex justify-center p-8 text-secondary">
            No upcoming scheduled posts.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Content</TableHead>
                <TableHead>Platform</TableHead>
                <TableHead>Scheduled Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.map(post => (
                <TableRow key={post.id}>
                  <TableCell className="font-medium max-w-xs truncate">
                    {post.title || post.content}
                  </TableCell>
                  <TableCell>{post.platform}</TableCell>
                  <TableCell>
                    {post.scheduled_for ? new Date(post.scheduled_for).toLocaleString() : 'N/A'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
