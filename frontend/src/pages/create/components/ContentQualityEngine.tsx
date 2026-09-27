import { useMemo } from 'react';
import { StudioState } from '../CreateStudio';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import { CheckCircle2, AlertTriangle, XCircle, Sparkles } from 'lucide-react';
import styles from './ContentQualityEngine.module.css';

interface ContentQualityEngineProps {
  state: StudioState;
  platformConfig: PlatformConfig;
  format: ContentFormat;
}

interface QualityFeedback {
  id: string;
  type: 'success' | 'warning' | 'error';
  message: string;
}

export function ContentQualityEngine({ state, platformConfig, format }: ContentQualityEngineProps) {
  const { score, feedback } = useMemo(() => {
    let currentScore = 100;
    const items: QualityFeedback[] = [];

    // 1. Caption & Limits
    if (format.charLimit > 0 && state.caption.length > format.charLimit) {
      currentScore -= 20;
      items.push({ id: 'char_limit', type: 'error', message: `Caption exceeds ${format.charLimit} character limit.` });
    } else if (state.caption.length === 0) {
      currentScore -= 10;
      items.push({ id: 'caption_empty', type: 'warning', message: 'Adding a caption increases engagement.' });
    } else {
      items.push({ id: 'caption_good', type: 'success', message: 'Caption length is optimal.' });
    }

    // 2. Hashtags
    if (state.hashtags.length === 0) {
      currentScore -= 15;
      items.push({ id: 'hash_none', type: 'warning', message: 'No hashtags used. Add some to increase reach.' });
    } else if (platformConfig.name === 'Instagram' && state.hashtags.length < 5) {
      currentScore -= 5;
      items.push({ id: 'hash_insta', type: 'warning', message: 'Instagram posts perform better with 5-15 hashtags.' });
    } else if (platformConfig.name === 'TikTok' && state.hashtags.length > 5) {
      currentScore -= 5;
      items.push({ id: 'hash_tiktok', type: 'warning', message: 'TikTok prefers 3-5 highly relevant hashtags.' });
    } else {
      items.push({ id: 'hash_good', type: 'success', message: 'Hashtag usage is optimized.' });
    }

    // 3. Elements / Hooks
    if (state.elements.length === 0) {
      currentScore -= 20;
      items.push({ id: 'elements_none', type: 'error', message: 'Canvas is empty. Add a hook or visual element.' });
    } else {
      const hasText = state.elements.some(e => e.type === 'text' && (e.content || '').length > 0);
      if (!hasText) {
        currentScore -= 10;
        items.push({ id: 'no_text', type: 'warning', message: 'Visuals without text hooks often have lower retention.' });
      } else {
        items.push({ id: 'text_good', type: 'success', message: 'Strong visual hook detected.' });
      }
    }

    // 4. Safe Zones (Simulated logic for short form video)
    const isVideo = ['reel', 'tiktok', 'short', 'story'].some(v => format.label.toLowerCase().includes(v));
    if (isVideo && state.elements.length > 0) {
      const bottomElements = state.elements.some(e => e.y + e.h > format.canvasH * 0.8);
      const rightElements = state.elements.some(e => e.x + e.w > format.canvasW * 0.85);
      
      if (bottomElements) {
        currentScore -= 10;
        items.push({ id: 'safe_bottom', type: 'warning', message: 'Elements near the bottom may be covered by the platform caption UI.' });
      }
      if (rightElements) {
        currentScore -= 10;
        items.push({ id: 'safe_right', type: 'warning', message: 'Elements on the right may overlap with interaction buttons (Like, Share).' });
      }
      
      if (!bottomElements && !rightElements) {
        items.push({ id: 'safe_good', type: 'success', message: 'All elements are within safe zones.' });
      }
    }

    return { score: Math.max(0, currentScore), feedback: items };
  }, [state, platformConfig, format]);

  const getScoreColor = () => {
    if (score >= 90) return 'var(--panel-2)'; // Green
    if (score >= 70) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };
  
  const color = getScoreColor();
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={styles.engine}>
      <div className={styles.header}>
        <div className={styles.scoreRingContainer}>
          <svg className={styles.scoreRing} width="120" height="120">
            <circle className={styles.ringBg} cx="60" cy="60" r={radius} strokeWidth="8" fill="transparent" />
            <circle
              className={styles.ringProgress}
              cx="60" cy="60" r={radius} strokeWidth="8" fill="transparent"
              stroke={color}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className={styles.scoreValue} style={{ color }}>{score}</div>
        </div>
        <div className={styles.scoreMeta}>
          <h3 className={styles.scoreTitle}>Quality Engine</h3>
          <p className={styles.scoreDesc}>
            {score >= 90 ? 'Perfectly optimized for ' + platformConfig.name + '!' :
             score >= 70 ? 'Looks good, but could be improved.' :
             'Needs work before publishing.'}
          </p>
        </div>
      </div>

      <div className={styles.feedbackList}>
        <h4 className={styles.feedbackTitle}>
          <Sparkles size={14} /> Actionable Insights
        </h4>
        {feedback.map(item => (
          <div key={item.id} className={`${styles.feedbackItem} ${styles[item.type]}`}>
            <div className={styles.feedbackIcon}>
              {item.type === 'success' && <CheckCircle2 size={16} />}
              {item.type === 'warning' && <AlertTriangle size={16} />}
              {item.type === 'error' && <XCircle size={16} />}
            </div>
            <div className={styles.feedbackText}>{item.message}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
