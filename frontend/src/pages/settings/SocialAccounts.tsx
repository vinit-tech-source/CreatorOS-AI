import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Share2, Plus } from 'lucide-react';
import { SocialAccount } from '../../types';

export function SocialAccounts() {
  const [accounts, _setAccounts] = useState<SocialAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setIsLoading(false);
    }, 500);
  }, []);

  return (
    <div className="flex-col gap-6">
      <PageHeader 
        title="Social Accounts" 
        subtitle="Connect platforms to publish content directly"
        action={
          <Button>
            <Plus size={16} /> Connect Account
          </Button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          <div className="col-span-full flex justify-center p-8 text-secondary">Loading accounts...</div>
        ) : accounts.length === 0 ? (
          <div className="col-span-full">
            <Card glass>
              <CardContent>
                <div className="flex flex-col items-center justify-center p-12 text-secondary">
                  <Share2 size={48} className="opacity-20 mb-4" />
                  <p>No social accounts connected.</p>
                  <Button variant="primary" className="mt-4">Connect Platform</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          accounts.map(account => (
            <Card key={account.id} glass>
              <CardContent className="pt-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-xl font-bold">
                      {account.platform.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-semibold">{account.display_name}</h3>
                      <p className="text-sm text-secondary">@{account.username}</p>
                    </div>
                  </div>
                  <Badge variant={account.is_active ? 'success' : 'danger'}>
                    {account.is_active ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>
                
                <div className="flex gap-2 mt-6">
                  <Button variant="outline" size="sm" fullWidth>Settings</Button>
                  <Button variant="danger" size="sm" fullWidth>Disconnect</Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
