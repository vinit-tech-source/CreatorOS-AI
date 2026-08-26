import { useEffect, useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ChevronLeft, ChevronRight, RefreshCw, AlertCircle } from 'lucide-react';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { calendarService } from '../../services/api/calendarService';
import { Post } from '../../types';
import styles from './ContentCalendar.module.css';

export function ContentCalendar() {
  const { activeWorkspace } = useWorkspaceStore();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPosts = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await calendarService.getWorkspaceCalendarPosts(activeWorkspace.id);
      setPosts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load calendar posts');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [activeWorkspace]);

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const today = () => {
    setCurrentDate(new Date());
  };

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay();
  };

  const generateCalendarGrid = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);
    
    const days = [];
    
    // Trailing days from previous month
    const prevMonthDays = getDaysInMonth(year, month - 1);
    for (let i = firstDay - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthDays - i),
        isTrailing: true,
      });
    }

    // Days in current month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({
        date: new Date(year, month, i),
        isTrailing: false,
      });
    }

    // Trailing days from next month
    const remainingCells = 42 - days.length; // 6 rows * 7 days
    for (let i = 1; i <= remainingCells; i++) {
      days.push({
        date: new Date(year, month + 1, i),
        isTrailing: true,
      });
    }

    return days;
  };

  const getPostsForDate = (date: Date) => {
    return posts.filter(post => {
      if (!post.scheduled_for) return false;
      const postDate = new Date(post.scheduled_for);
      return postDate.getDate() === date.getDate() &&
             postDate.getMonth() === date.getMonth() &&
             postDate.getFullYear() === date.getFullYear();
    });
  };

  const isToday = (date: Date) => {
    const now = new Date();
    return date.getDate() === now.getDate() &&
           date.getMonth() === now.getMonth() &&
           date.getFullYear() === now.getFullYear();
  };

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  if (!activeWorkspace) {
    return (
      <div className={styles.container}>
        <PageHeader title="Content Calendar" subtitle="View and manage your scheduled content." />
        <Card glass>
          <CardContent>
            <div className={styles.errorState}>
              <AlertCircle size={40} className="mb-4" />
              <p className="font-medium text-lg">No workspace selected</p>
              <p className="mt-2">Select a workspace to view the content calendar.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const calendarDays = generateCalendarGrid();

  return (
    <div className={styles.container}>
      <PageHeader 
        title="Content Calendar" 
        subtitle="Visualize and track your scheduled posts across all projects."
        action={
          <Button onClick={() => window.location.href = '/create'}>
            Create Post
          </Button>
        }
      />

      <Card glass>
        <CardContent>
          <div className={styles.calendarControls}>
            <div className={styles.monthDisplay}>
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </div>
            <div className={styles.navButtons}>
              <Button variant="outline" size="sm" onClick={today}>Today</Button>
              <Button variant="outline" size="sm" onClick={prevMonth}>
                <ChevronLeft size={16} />
              </Button>
              <Button variant="outline" size="sm" onClick={nextMonth}>
                <ChevronRight size={16} />
              </Button>
              <Button variant="ghost" size="sm" onClick={fetchPosts} disabled={isLoading}>
                <RefreshCw size={16} className={isLoading ? styles.spinner : ''} style={{ animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
              </Button>
            </div>
          </div>

          {error ? (
            <div className={styles.errorState}>
              <AlertCircle size={32} className="mb-4" />
              <p>{error}</p>
              <Button variant="outline" className="mt-4" onClick={fetchPosts}>Retry</Button>
            </div>
          ) : (
            <div className={styles.calendarGrid}>
              {dayNames.map(day => (
                <div key={day} className={styles.dayOfWeek}>{day}</div>
              ))}
              
              {calendarDays.map((dayObj, index) => {
                const dayPosts = getPostsForDate(dayObj.date);
                return (
                  <div 
                    key={index} 
                    className={`${styles.dayCell} ${dayObj.isTrailing ? styles.isTrailing : ''} ${isToday(dayObj.date) ? styles.isToday : ''}`}
                  >
                    <span className={styles.dateNumber}>{dayObj.date.getDate()}</span>
                    
                    {dayPosts.map(post => (
                      <div 
                        key={post.id} 
                        className={`${styles.postBadge} ${post.status === 'PUBLISHED' ? styles.published : styles.scheduled}`}
                        title={post.content || post.title || 'Untitled Post'}
                        onClick={() => window.location.href = `/posts/${post.id}`} // Assuming post detail routing
                      >
                        <span className={styles.postTime}>
                          {new Date(post.scheduled_for!).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <span className={styles.postTitle}>
                          {post.title || (post.content ? post.content.substring(0, 20) + '...' : 'Untitled')}
                        </span>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
