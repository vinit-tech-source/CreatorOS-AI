import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table';
import { Badge } from '../../components/ui/Badge';
import { Plus, FolderKanban, PenTool } from 'lucide-react';
import { Project } from '../../types';
import { Link } from 'react-router-dom';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { projectService } from '../../services/api/projectService';
import { CreateProjectModal } from './components/CreateProjectModal';

export function Projects() {
  const { activeWorkspace } = useWorkspaceStore();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchProjects = async () => {
    if (!activeWorkspace) {
      setIsLoading(false);
      return;
    }
    
    try {
      setIsLoading(true);
      const data = await projectService.getProjects(activeWorkspace.id);
      setProjects(data);
    } catch (error) {
      console.error('Failed to fetch projects', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [activeWorkspace]);

  const handleCreateProject = async (data: { name: string; description: string }) => {
    if (!activeWorkspace) return;
    
    await projectService.createProject(activeWorkspace.id, data);
    await fetchProjects(); // Refresh the list
  };

  if (!activeWorkspace) {
    return (
      <div className="flex justify-center p-8 text-secondary">
        Please select a workspace to view projects.
      </div>
    );
  }

  return (
    <div className="flex-col gap-6">
      <PageHeader 
        title="Projects" 
        subtitle="Organize your content into campaigns and themes"
        action={
          <Button onClick={() => setIsModalOpen(true)}>
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
              <Button variant="outline" className="mt-4" onClick={() => setIsModalOpen(true)}>
                Create your first project
              </Button>
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
                      <div className="flex gap-2">
                        <Link to={`/workspaces/${activeWorkspace.id}/projects/${project.id}/create`}>
                          <Button variant="outline" size="sm">
                            <PenTool size={14} className="mr-1" /> Create Post
                          </Button>
                        </Link>
                        <Button variant="ghost" size="sm">View</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
      
      <CreateProjectModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </div>
  );
}
