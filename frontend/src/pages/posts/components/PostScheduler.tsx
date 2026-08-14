import { useState } from 'react';
import { Card, CardHeader, CardContent } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Post } from '../../../types';
import { CalendarDays, Clock, Trash } from 'lucide-react';

interface PostSchedulerProps {
  post: Post;
  onSchedule: (date: string, timezone: string) => Promise<void>;
  onReschedule: (date: string, timezone: string) => Promise<void>;
  onCancelSchedule: () => Promise<void>;
  isLoading: boolean;
}

export function PostScheduler({ post, onSchedule, onReschedule, onCancelSchedule, isLoading }: PostSchedulerProps) {
  // Use local state for datetime input
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  
  // A real app might auto-detect timezone, we default to UTC or simple string
  const [timezone] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone);

  const handleScheduleAction = (action: 'schedule' | 'reschedule') => {
    if (!date || !time) {
      alert("Please select both date and time.");
      return;
    }
    
    // Construct ISO string (assuming local time entry for simplicity, combined into ISO)
    // Note: In a production app, robust timezone handling using date-fns or moment-timezone is preferred.
    const isoString = new Date(`${date}T${time}`).toISOString();
    
    if (action === 'schedule') {
      onSchedule(isoString, timezone);
    } else {
      onReschedule(isoString, timezone);
    }
  };

  const handleCancel = () => {
    if (confirm("Are you sure you want to cancel the schedule? This will revert the post to APPROVED status.")) {
      onCancelSchedule();
    }
  };

  if (post.status !== 'APPROVED' && post.status !== 'SCHEDULED') {
    return null;
  }

  return (
    <Card glass>
      <CardHeader 
        title={<><CalendarDays size={18} className="inline-block mr-2" />{post.status === 'SCHEDULED' ? "Reschedule Post" : "Schedule Post"}</>} 
      />
      <CardContent>
        {post.status === 'SCHEDULED' && post.scheduled_for && (
          <div className="mb-4 p-3 bg-info/10 border border-info/20 rounded-md">
            <p className="text-sm font-bold text-info flex items-center gap-2">
              <Clock size={16} /> Currently Scheduled For:
            </p>
            <p className="text-sm text-info mt-1">
              {new Date(post.scheduled_for).toLocaleString()}
            </p>
          </div>
        )}

        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Date</label>
              <input 
                type="date" 
                className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary"
                value={date}
                onChange={e => setDate(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium">Time</label>
              <input 
                type="time" 
                className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary"
                value={time}
                onChange={e => setTime(e.target.value)}
              />
            </div>
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium">Timezone</label>
            <input 
              type="text" 
              className="w-full px-3 py-2 bg-surface border border-border rounded-md text-sm outline-none focus:border-primary opacity-70"
              value={timezone}
              readOnly
            />
            <p className="text-xs text-secondary mt-1">Auto-detected local timezone</p>
          </div>

          <div className="flex gap-3 mt-2">
            <Button 
              variant="primary" 
              onClick={() => handleScheduleAction(post.status === 'SCHEDULED' ? 'reschedule' : 'schedule')}
              isLoading={isLoading}
            >
              {post.status === 'SCHEDULED' ? 'Update Schedule' : 'Schedule'}
            </Button>
            
            {post.status === 'SCHEDULED' && (
              <Button 
                variant="danger" 
                onClick={handleCancel}
                isLoading={isLoading}
              >
                <Trash size={16} className="mr-2" /> Cancel Schedule
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
