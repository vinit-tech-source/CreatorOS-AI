import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { PenTool, FolderKanban, Share2, BarChart3 } from 'lucide-react';

export function QuickActions() {
  return (
    <Card glass>
      <CardHeader title="Quick Actions" />
      <CardContent>
        <div className="flex flex-col gap-3">
          <Link to="/posts">
            <Button variant="primary" fullWidth className="justify-start">
              <PenTool size={18} className="mr-2" /> Create Post
            </Button>
          </Link>
          <Link to="/projects">
            <Button variant="secondary" fullWidth className="justify-start">
              <FolderKanban size={18} className="mr-2" /> Create Project
            </Button>
          </Link>
          <Link to="/social-accounts">
            <Button variant="secondary" fullWidth className="justify-start">
              <Share2 size={18} className="mr-2" /> Connect Account
            </Button>
          </Link>
          <Link to="/analytics">
            <Button variant="outline" fullWidth className="justify-start">
              <BarChart3 size={18} className="mr-2" /> View Analytics
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
