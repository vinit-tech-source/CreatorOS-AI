import styles from './LinkedInPreview.module.css';
import { ThumbsUp, MessageSquare, Repeat2, Send, MoreHorizontal, Globe2 } from 'lucide-react';

interface LinkedInPreviewProps {
  content: string;
  name?: string;
  headline?: string;
  avatarUrl?: string;
}

export function LinkedInPreview({ content, name = "Creator Name", headline = "Content Creator | Storyteller", avatarUrl }: LinkedInPreviewProps) {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.avatar}>
          {avatarUrl ? <img src={avatarUrl} alt="Avatar" /> : name.charAt(0)}
        </div>
        <div className={styles.authorInfo}>
          <div className={styles.nameRow}>
            <span className={styles.name}>{name}</span>
            <span className={styles.degree}>• 1st</span>
          </div>
          <div className={styles.headline}>{headline}</div>
          <div className={styles.timeRow}>
            <span>1h •</span>
            <Globe2 size={12} className={styles.globeIcon} />
          </div>
        </div>
        <div className={styles.moreAction}>
          <MoreHorizontal size={20} />
        </div>
      </div>
      
      <div className={styles.body}>
        {content || "What do you want to talk about?"}
      </div>
      
      <div className={styles.statsRow}>
        <div className={styles.likes}>
          <div className={styles.likeIcon}>👍</div>
          <span>0</span>
        </div>
        <div className={styles.comments}>0 comments</div>
      </div>
      
      <div className={styles.actions}>
        <div className={styles.actionItem}>
          <ThumbsUp size={18} />
          <span>Like</span>
        </div>
        <div className={styles.actionItem}>
          <MessageSquare size={18} />
          <span>Comment</span>
        </div>
        <div className={styles.actionItem}>
          <Repeat2 size={18} />
          <span>Repost</span>
        </div>
        <div className={styles.actionItem}>
          <Send size={18} />
          <span>Send</span>
        </div>
      </div>
    </div>
  );
}
