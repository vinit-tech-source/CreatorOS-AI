import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { FolderKanban } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function ContentLibrary() {
  return (
    <div className="flex-col gap-6 w-full">
      <PageHeader 
        title="Content Library" 
        subtitle="Manage all your generated and scheduled content."
      />
      <Card glass>
        <CardContent>
          <div className="flex flex-col items-center justify-center p-12 text-secondary">
            <FolderKanban size={48} className="opacity-20 mb-4" />
            <p className="mb-4 text-center">Your content library will appear here.</p>
            <Button onClick={() => window.location.href = '/create'}>
              Create Content
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
