import styles from './TwitterPreview.module.css';
import { Heart, MessageCircle, Repeat, Share, MoreHorizontal } from 'lucide-react';

interface TwitterPreviewProps {
  content: string;
  name?: string;
  handle?: string;
  avatarUrl?: string;
}

export function TwitterPreview({ content, name = "Creator", handle = "@creator", avatarUrl }: TwitterPreviewProps) {
  return (
    <div className={styles.tweetContainer}>
      <div className={styles.avatarCol}>
        <div className={styles.avatar}>
          {avatarUrl ? <img src={avatarUrl} alt="Avatar" /> : name.charAt(0)}
        </div>
      </div>
      <div className={styles.contentCol}>
        <div className={styles.header}>
          <div className={styles.authorInfo}>
            <span className={styles.name}>{name}</span>
            <span className={styles.handle}>{handle}</span>
            <span className={styles.dot}>·</span>
            <span className={styles.time}>1m</span>
          </div>
          <MoreHorizontal size={18} className={styles.moreIcon} />
        </div>
        <div className={styles.body}>
          {content || "Your post text will appear here."}
        </div>
        <div className={styles.actions}>
          <div className={styles.actionItem}>
            <MessageCircle size={16} />
            <span>0</span>
          </div>
          <div className={styles.actionItem}>
            <Repeat size={16} />
            <span>0</span>
          </div>
          <div className={styles.actionItem}>
            <Heart size={16} />
            <span>0</span>
          </div>
          <div className={styles.actionItem}>
            <Share size={16} />
          </div>
        </div>
      </div>
    </div>
  );
}
