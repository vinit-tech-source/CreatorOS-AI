import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table';
import { Badge } from '../../components/ui/Badge';
import { Plus, FolderKanban } from 'lucide-react';
import { Project } from '../../types';

export function Projects() {
  const [projects, _setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // In a real app, workspaceId would come from a global selector or URL
    const fetchProjects = async () => {
      try {
        // We'll pass a dummy workspace ID or fetch the first one if we need to.
        // For now, we assume the backend has an endpoint to get projects across all workspaces 
        // or we use a hardcoded one for the shell.
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to fetch projects', error);
        setIsLoading(false);
      }
    };

    fetchProjects();
  }, []);

  return (
    <div className="flex-col gap-6">
      <PageHeader 
        title="Projects" 
        subtitle="Organize your content into campaigns and themes"
        action={
          <Button>
            <Plus size={16} /> New Project
          </Button>
        }
      />

      <Card glass>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center p-8 text-secondary">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <FolderKanban size={48} className="opacity-20 mb-4" />
              <p>No projects found in this workspace.</p>
              <Button variant="outline" className="mt-4">Create your first project</Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium">{project.name}</TableCell>
                    <TableCell>
                      <Badge variant={project.is_active ? 'success' : 'secondary'}>
                        {project.is_active ? 'Active' : 'Archived'}
                      </Badge>
                    </TableCell>
                    <TableCell>{new Date(project.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">View</Button>
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
