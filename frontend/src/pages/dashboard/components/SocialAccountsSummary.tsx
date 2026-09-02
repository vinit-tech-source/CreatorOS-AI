import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { Share2, Plus, ExternalLink } from 'lucide-react';
import { SocialAccount } from '../../../types';
import { RealBrandLogo } from '../../../components/common/BrandLogos';

interface SocialAccountsSummaryProps {
  accounts: SocialAccount[];
}

export function SocialAccountsSummary({ accounts }: SocialAccountsSummaryProps) {
  return (
    <Card glass>
      <CardHeader 
        title="Publishing Channels" 
        subtitle="Connected social distribution endpoints" 
        action={
          <Link to="/social-accounts">
            <Button variant="outline" size="sm">
              <Share2 size={13} className="mr-1.5" /> Manage
            </Button>
          </Link>
        }
      />
      <CardContent className="p-0">
        {accounts.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
            <Share2 size={32} className="text-slate-500 mb-2 opacity-60" />
            <p className="text-sm font-semibold text-slate-300">No social accounts connected</p>
            <p className="text-xs text-slate-500 mt-1 mb-3">
              Connect Instagram, LinkedIn, YouTube, or X to automate releases.
            </p>
            <Link to="/social-accounts">
              <Button size="sm">
                <Plus size={13} className="mr-1" /> Connect Channel
              </Button>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {accounts.map(acc => (
              <div key={acc.id} className="p-3.5 hover:bg-white/[0.02] flex items-center justify-between transition-colors">
                <div className="flex items-center gap-3 min-w-0 pr-4">
                  <div className="p-1.5 rounded-lg bg-white/5 border border-white/10 flex-shrink-0">
                    <RealBrandLogo platform={acc.platform} size={16} />
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-sm font-semibold text-white truncate">
                      {acc.account_name}
                    </span>
                    <span className="text-xs text-slate-400 capitalize">
                      {acc.platform.toLowerCase()} • Connected {new Date(acc.connected_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge variant={acc.is_active ? 'success' : 'danger'}>
                    <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${acc.is_active ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                    {acc.is_active ? 'Active' : 'Offline'}
                  </Badge>
                  <Link 
                    to="/social-accounts"
                    className="text-slate-400 hover:text-white p-1 rounded hover:bg-white/10 transition-colors"
                  >
                    <ExternalLink size={13} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
