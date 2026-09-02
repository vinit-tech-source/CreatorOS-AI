import { CalendarPost } from '../../../services/api/calendarService';
import { RealBrandLogo, PLATFORM_METAS } from '../../../components/common/BrandLogos';
import { 
  Clock, 
  CheckCircle2, 
  FileText, 
  Plus, 
  Calendar as CalendarIcon
} from 'lucide-react';
import styles from '../ContentCalendar.module.css';

// Helper to extract attached image URL from post content
export const extractPostMediaUrl = (content?: string): string | null => {
  if (!content) return null;
  const match = content.match(/\[Attached Media\]:\s*(https?:\/\/[^\s]+)/i);
  if (match && match[1]) {
    return match[1];
  }
  // Check for raw unsplash image URL
  const rawMatch = content.match(/(https:\/\/images\.unsplash\.com\/[^\s]+)/i);
  if (rawMatch && rawMatch[1]) {
    return rawMatch[1];
  }
  return null;
};

// Clean caption text without media tag
export const cleanPostCaption = (content?: string): string => {
  if (!content) return '';
  return content.replace(/\[Attached Media\]:\s*https?:\/\/[^\s]+/gi, '').trim();
};

export function StatusBadge({ status }: { status: string }) {
  const s = (status || '').toUpperCase();
  if (s === 'PUBLISHED') {
    return (
      <span className={`${styles.statusChip} ${styles.statusPublished}`}>
        <CheckCircle2 size={10} /> Published
      </span>
    );
  }
  if (s === 'SCHEDULED') {
    return (
      <span className={`${styles.statusChip} ${styles.statusScheduled}`}>
        <Clock size={10} /> Scheduled
      </span>
    );
  }
  if (s === 'APPROVED') {
    return (
      <span className={`${styles.statusChip} ${styles.statusApproved}`}>
        <CheckCircle2 size={10} /> Ready
      </span>
    );
  }
  return (
    <span className={`${styles.statusChip} ${styles.statusDraft}`}>
      <FileText size={10} /> Draft
    </span>
  );
}

// ----------------------------------------------------------------------
// Month View
// ----------------------------------------------------------------------
interface MonthViewProps {
  currentDate: Date;
  posts: CalendarPost[];
  onSelectPost: (post: CalendarPost) => void;
  onSelectDate: (date: Date) => void;
}

export function MonthView({ currentDate, posts, onSelectPost, onSelectDate }: MonthViewProps) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayIndex = new Date(year, month, 1).getDay();

  const days = [];
  const prevMonthDays = new Date(year, month, 0).getDate();

  // Trailing previous month days
  for (let i = firstDayIndex - 1; i >= 0; i--) {
    days.push({
      date: new Date(year, month - 1, prevMonthDays - i),
      isTrailing: true,
    });
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    days.push({
      date: new Date(year, month, i),
      isTrailing: false,
    });
  }

  // Trailing next month days (up to 42 cells)
  const remaining = 42 - days.length;
  for (let i = 1; i <= remaining; i++) {
    days.push({
      date: new Date(year, month + 1, i),
      isTrailing: true,
    });
  }

  const isToday = (d: Date) => {
    const now = new Date();
    return d.getDate() === now.getDate() &&
           d.getMonth() === now.getMonth() &&
           d.getFullYear() === now.getFullYear();
  };

  const getDayPosts = (d: Date) => {
    return posts.filter(p => {
      if (!p.scheduled_for) return false;
      const pd = new Date(p.scheduled_for);
      return pd.getDate() === d.getDate() &&
             pd.getMonth() === d.getMonth() &&
             pd.getFullYear() === d.getFullYear();
    });
  };

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className={styles.monthContainer}>
      <div className={styles.weekdayHeaderRow}>
        {dayNames.map(day => (
          <div key={day} className={styles.weekdayHeaderCol}>
            {day}
          </div>
        ))}
      </div>

      <div className={styles.monthGrid}>
        {days.map((dayItem, idx) => {
          const dayPosts = getDayPosts(dayItem.date);
          const today = isToday(dayItem.date);
          const maxVisible = 3;
          const visiblePosts = dayPosts.slice(0, maxVisible);
          const hiddenCount = dayPosts.length - maxVisible;

          return (
            <div
              key={idx}
              className={`
                ${styles.monthCell}
                ${dayItem.isTrailing ? styles.cellTrailing : ''}
                ${today ? styles.cellToday : ''}
              `}
              onClick={(e) => {
                if ((e.target as HTMLElement).closest(`.${styles.postBadgeItem}`)) return;
                onSelectDate(dayItem.date);
              }}
            >
              <div className={styles.cellHeader}>
                <span className={`${styles.cellDayNumber} ${today ? styles.dayNumberToday : ''}`}>
                  {dayItem.date.getDate()}
                </span>
                <button
                  type="button"
                  className={styles.cellAddBtn}
                  title="Schedule post on this day"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectDate(dayItem.date);
                  }}
                >
                  <Plus size={11} />
                </button>
              </div>

              <div className={styles.cellPostsList}>
                {visiblePosts.map(post => {
                  const meta = PLATFORM_METAS[post.platform?.toUpperCase()] || PLATFORM_METAS.INSTAGRAM;
                  const time = new Date(post.scheduled_for!).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  });
                  const mediaUrl = extractPostMediaUrl(post.content);
                  const cleanCaption = cleanPostCaption(post.content);

                  return (
                    <div
                      key={post.id}
                      className={styles.postBadgeItem}
                      style={{
                        backgroundColor: meta.accentBg,
                        borderColor: meta.borderColor,
                        color: meta.primaryColor,
                      }}
                      title={`${meta.name} • ${time} • ${post.title || cleanCaption}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectPost(post);
                      }}
                    >
                      <span className={styles.badgeIcon}>
                        <RealBrandLogo platform={post.platform} size={12} />
                      </span>
                      <span className={styles.badgeTime}>{time}</span>
                      {mediaUrl && (
                        <img 
                          src={mediaUrl} 
                          alt="" 
                          className={styles.badgeThumbMini}
                          loading="lazy"
                        />
                      )}
                      <span className={styles.badgeTitle}>
                        {post.title || cleanCaption.substring(0, 16)}
                      </span>
                    </div>
                  );
                })}

                {hiddenCount > 0 && (
                  <div 
                    className={styles.morePostsPill}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectDate(dayItem.date);
                    }}
                  >
                    +{hiddenCount} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// Week View
// ----------------------------------------------------------------------
interface WeekViewProps {
  currentDate: Date;
  posts: CalendarPost[];
  onSelectPost: (post: CalendarPost) => void;
  onSelectDate: (date: Date) => void;
}

export function WeekView({ currentDate, posts, onSelectPost, onSelectDate }: WeekViewProps) {
  const startOfWeek = new Date(currentDate);
  startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());

  const weekDays = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + i);
    weekDays.push(d);
  }

  const isToday = (d: Date) => {
    const now = new Date();
    return d.getDate() === now.getDate() &&
           d.getMonth() === now.getMonth() &&
           d.getFullYear() === now.getFullYear();
  };

  const getDayPosts = (d: Date) => {
    return posts.filter(p => {
      if (!p.scheduled_for) return false;
      const pd = new Date(p.scheduled_for);
      return pd.getDate() === d.getDate() &&
             pd.getMonth() === d.getMonth() &&
             pd.getFullYear() === d.getFullYear();
    }).sort((a, b) => new Date(a.scheduled_for!).getTime() - new Date(b.scheduled_for!).getTime());
  };

  const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  return (
    <div className={styles.weekContainer}>
      <div className={styles.weekGrid}>
        {weekDays.map((dateObj, idx) => {
          const dayPosts = getDayPosts(dateObj);
          const today = isToday(dateObj);

          return (
            <div 
              key={idx} 
              className={`${styles.weekColumn} ${today ? styles.weekColumnToday : ''}`}
            >
              <div className={styles.weekColumnHeader}>
                <div className={styles.weekHeaderDayName}>{dayNames[idx]}</div>
                <div className={`${styles.weekHeaderDate} ${today ? styles.weekDateToday : ''}`}>
                  {dateObj.getDate()}
                </div>
                <div className={styles.weekHeaderCount}>
                  {dayPosts.length} {dayPosts.length === 1 ? 'post' : 'posts'}
                </div>
                <button 
                  type="button"
                  className={styles.weekAddBtn}
                  onClick={() => onSelectDate(dateObj)}
                  title="Schedule post for this day"
                >
                  <Plus size={11} /> Add
                </button>
              </div>

              <div className={styles.weekPostsContainer}>
                {dayPosts.length === 0 ? (
                  <div className={styles.emptyDayNotice}>
                    <span>No posts</span>
                  </div>
                ) : (
                  dayPosts.map(post => {
                    const meta = PLATFORM_METAS[post.platform?.toUpperCase()] || PLATFORM_METAS.INSTAGRAM;
                    const time = new Date(post.scheduled_for!).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    });
                    const mediaUrl = extractPostMediaUrl(post.content);
                    const cleanCaption = cleanPostCaption(post.content);

                    return (
                      <div
                        key={post.id}
                        className={styles.weekPostCard}
                        onClick={() => onSelectPost(post)}
                      >
                        <div className={styles.weekCardTop}>
                          <span 
                            className={styles.platformBadgePill}
                            style={{
                              backgroundColor: meta.accentBg,
                              borderColor: meta.borderColor,
                              color: meta.primaryColor
                            }}
                          >
                            <RealBrandLogo platform={post.platform} size={13} />
                            <span>{meta.name}</span>
                          </span>
                          <span className={styles.weekCardTime}>{time}</span>
                        </div>

                        {mediaUrl && (
                          <div className={styles.weekPostImageWrapper}>
                            <img 
                              src={mediaUrl} 
                              alt="" 
                              className={styles.weekPostImg} 
                              loading="lazy" 
                            />
                          </div>
                        )}

                        <div className={styles.weekCardTitle}>
                          {post.title || 'Untitled Post'}
                        </div>

                        <p className={styles.weekCardSnippet}>
                          {cleanCaption}
                        </p>

                        <div className={styles.weekCardFooter}>
                          <StatusBadge status={post.status} />
                          {post.projectName && (
                            <span className={styles.projectTag}>{post.projectName}</span>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ----------------------------------------------------------------------
// Agenda / List View
// ----------------------------------------------------------------------
interface AgendaViewProps {
  posts: CalendarPost[];
  onSelectPost: (post: CalendarPost) => void;
  onQuickSchedule: () => void;
}

export function AgendaView({ posts, onSelectPost, onQuickSchedule }: AgendaViewProps) {
  const sorted = [...posts].sort((a, b) => {
    const timeA = a.scheduled_for ? new Date(a.scheduled_for).getTime() : 0;
    const timeB = b.scheduled_for ? new Date(b.scheduled_for).getTime() : 0;
    return timeA - timeB;
  });

  const grouped: { [key: string]: CalendarPost[] } = {};
  sorted.forEach(post => {
    if (!post.scheduled_for) return;
    const d = new Date(post.scheduled_for);
    const key = d.toLocaleDateString(undefined, {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(post);
  });

  const dateKeys = Object.keys(grouped);

  if (dateKeys.length === 0) {
    return (
      <div className={styles.agendaEmpty}>
        <CalendarIcon size={40} className="opacity-40 mb-3 text-indigo-400" />
        <h3>No scheduled posts found</h3>
        <p>There are no posts scheduled for the selected filter or date range.</p>
        <button className={styles.primaryActionButton} onClick={onQuickSchedule}>
          <Plus size={15} /> Schedule Your First Post
        </button>
      </div>
    );
  }

  return (
    <div className={styles.agendaContainer}>
      {dateKeys.map(dateKey => {
        const dayPosts = grouped[dateKey];
        return (
          <div key={dateKey} className={styles.agendaGroup}>
            <div className={styles.agendaDateHeader}>
              <div className={styles.agendaDateTitle}>
                <CalendarIcon size={15} />
                <span>{dateKey}</span>
              </div>
              <span className={styles.agendaGroupCount}>
                {dayPosts.length} {dayPosts.length === 1 ? 'post' : 'posts'}
              </span>
            </div>

            <div className={styles.agendaItemsList}>
              {dayPosts.map(post => {
                const meta = PLATFORM_METAS[post.platform?.toUpperCase()] || PLATFORM_METAS.INSTAGRAM;
                const timeStr = new Date(post.scheduled_for!).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                });
                const mediaUrl = extractPostMediaUrl(post.content);
                const cleanCaption = cleanPostCaption(post.content);

                return (
                  <div
                    key={post.id}
                    className={styles.agendaItemRow}
                    onClick={() => onSelectPost(post)}
                  >
                    <div className={styles.agendaTimeCol}>
                      <span className={styles.agendaTimeText}>{timeStr}</span>
                      <StatusBadge status={post.status} />
                    </div>

                    {mediaUrl && (
                      <img 
                        src={mediaUrl} 
                        alt="" 
                        className={styles.agendaRowThumb} 
                        loading="lazy"
                      />
                    )}

                    <div className={styles.agendaContentCol}>
                      <div className={styles.agendaContentHeader}>
                        <span 
                          className={styles.platformBadgePill}
                          style={{
                            backgroundColor: meta.accentBg,
                            borderColor: meta.borderColor,
                            color: meta.primaryColor
                          }}
                        >
                          <RealBrandLogo platform={post.platform} size={13} />
                          <span>{meta.name}</span>
                        </span>
                        {post.projectName && (
                          <span className={styles.projectTag}>{post.projectName}</span>
                        )}
                        <h4 className={styles.agendaPostTitle}>
                          {post.title || 'Untitled Post'}
                        </h4>
                      </div>

                      <p className={styles.agendaSnippet}>{cleanCaption}</p>
                    </div>

                    <div className={styles.agendaActionCol}>
                      <button 
                        type="button" 
                        className={styles.agendaManageBtn}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectPost(post);
                        }}
                      >
                        Manage &rarr;
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
