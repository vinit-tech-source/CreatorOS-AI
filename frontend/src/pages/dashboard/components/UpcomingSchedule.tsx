import { Link } from 'react-router-dom';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Calendar, Plus, Clock } from 'lucide-react';
import { Post } from '../../../types';
import { RealBrandLogo } from '../../../components/common/BrandLogos';

interface UpcomingScheduleProps {
  posts: Post[];
}

export function UpcomingSchedule({ posts }: UpcomingScheduleProps) {
  return (
    <Card glass>
      <CardHeader 
        title="Upcoming Releases" 
        subtitle="Posts scheduled for publication"
        action={
          <Link to="/calendar">
            <Button variant="outline" size="sm">
              <Calendar size={13} className="mr-1.5" /> Full Calendar
            </Button>
          </Link>
        }
      />
      <CardContent className="p-0">
        {posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <Calendar size={32} className="text-slate-500 mb-2 opacity-60" />
            <p className="text-sm font-semibold text-slate-300">No upcoming scheduled posts</p>
            <p className="text-xs text-slate-500 mt-1 mb-4">
              Schedule content to maintain a consistent multi-channel release cadence.
            </p>
            <Link to="/calendar">
              <Button size="sm">
                <Plus size={13} className="mr-1" /> Schedule Post
              </Button>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {posts.slice(0, 5).map(post => {
              const formattedDate = post.scheduled_for
                ? new Date(post.scheduled_for).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                  })
                : 'Date pending';

              const formattedTime = post.scheduled_for
                ? new Date(post.scheduled_for).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : '';

              return (
                <div key={post.id} className="p-3.5 hover:bg-white/[0.02] flex items-center justify-between transition-colors">
                  <div className="flex items-center gap-3 min-w-0 pr-4">
                    <div className="p-1.5 rounded-lg bg-white/5 border border-white/10 flex-shrink-0">
                      <RealBrandLogo platform={post.platform} size={15} />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <span className="text-sm font-semibold text-white truncate max-w-xs md:max-w-md">
                        {post.title || post.content}
                      </span>
                      <span className="text-xs text-slate-400 capitalize">
                        {post.platform.toLowerCase()} • {post.content_type?.toLowerCase() || 'post'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-md">
                      <Clock size={11} /> {formattedDate} {formattedTime}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
