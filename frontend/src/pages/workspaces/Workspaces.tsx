import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table';
import { Plus, Building2 } from 'lucide-react';
import { apiClient } from '../../services/api';
import { Workspace } from '../../types';

export function Workspaces() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchWorkspaces = async () => {
      try {
        const response = await apiClient.get('/workspaces');
        if (response.data.success) {
          setWorkspaces(response.data.data);
        }
      } catch (error) {
        console.error('Failed to fetch workspaces', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWorkspaces();
  }, []);

  return (
    <div className="flex-col gap-6">
      <PageHeader 
        title="Workspaces" 
        subtitle="Manage your organizations and teams"
        action={
          <Button>
            <Plus size={16} /> New Workspace
          </Button>
        }
      />

      <Card glass>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex justify-center p-8 text-secondary">Loading workspaces...</div>
          ) : workspaces.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-secondary">
              <Building2 size={48} className="opacity-20 mb-4" />
              <p>No workspaces found.</p>
              <Button variant="outline" className="mt-4">Create your first workspace</Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Slug</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {workspaces.map((workspace) => (
                  <TableRow key={workspace.id}>
                    <TableCell className="font-medium">{workspace.name}</TableCell>
                    <TableCell>{workspace.slug}</TableCell>
                    <TableCell>{new Date(workspace.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">Manage</Button>
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
