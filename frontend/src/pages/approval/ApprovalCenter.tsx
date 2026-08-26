import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { CheckSquare } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function ApprovalCenter() {
  return (
    <div className="flex-col gap-6 w-full">
      <PageHeader 
        title="Approval Center" 
        subtitle="Review and approve content before it is published."
      />
      <Card glass>
        <CardContent>
          <div className="flex flex-col items-center justify-center p-12 text-secondary">
            <CheckSquare size={48} className="opacity-20 mb-4" />
            <p className="mb-4 text-center">You have no content pending review.</p>
            <Button onClick={() => window.location.href = '/create'}>
              Create Content
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
