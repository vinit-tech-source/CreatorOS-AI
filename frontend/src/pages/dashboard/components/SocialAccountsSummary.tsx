import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../../components/ui/Table';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { SocialAccount } from '../../../types';

interface SocialAccountsSummaryProps {
  accounts: SocialAccount[];
}

export function SocialAccountsSummary({ accounts }: SocialAccountsSummaryProps) {
  return (
    <Card glass>
      <CardHeader 
        title="Connected Accounts" 
        subtitle="Social profiles active in this workspace"
        action={
          <Link to="/social-accounts">
            <Button variant="outline" size="sm">Manage Accounts</Button>
          </Link>
        }
      />
      <CardContent className="p-0">
        {accounts.length === 0 ? (
          <div className="flex justify-center p-8 text-secondary">
            No connected accounts.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Platform</TableHead>
                <TableHead>Username</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Connected</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accounts.map(acc => (
                <TableRow key={acc.id}>
                  <TableCell className="font-medium">
                    {acc.account_name}
                  </TableCell>
                  <TableCell>{acc.platform}</TableCell>
                  <TableCell>
                    <Badge variant={acc.is_active ? 'success' : 'danger'}>
                      {acc.is_active ? 'Active' : 'Disconnected'}
                    </Badge>
                  </TableCell>
                  <TableCell>{new Date(acc.connected_at).toLocaleDateString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
