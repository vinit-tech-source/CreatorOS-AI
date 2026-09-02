import React, { useState } from 'react';
import { CalendarPost, calendarService } from '../../../services/api/calendarService';
import { StatusBadge, extractPostMediaUrl, cleanPostCaption } from './CalendarViews';
import { RealBrandLogo, PLATFORM_METAS } from '../../../components/common/BrandLogos';
import { 
  X, 
  Clock, 
  Trash2, 
  Check, 
  AlertCircle,
  FolderKanban,
  Edit3
} from 'lucide-react';
import styles from '../ContentCalendar.module.css';

interface PostDetailModalProps {
  post: CalendarPost | null;
  onClose: () => void;
  onPostUpdated: () => void;
}

export function PostDetailModal({ post, onClose, onPostUpdated }: PostDetailModalProps) {
  if (!post) return null;

  const meta = PLATFORM_METAS[post.platform?.toUpperCase()] || PLATFORM_METAS.INSTAGRAM;
  const mediaUrl = extractPostMediaUrl(post.content);
  const cleanCaption = cleanPostCaption(post.content);
  
  // Format current scheduled date for datetime-local input (YYYY-MM-DDTHH:mm)
  const formatForInput = (isoDate?: string) => {
    if (!isoDate) return '';
    const d = new Date(isoDate);
    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const [newDateTime, setNewDateTime] = useState<string>(formatForInput(post.scheduled_for));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const applyReschedulePreset = (daysAhead: number, hours: number) => {
    const d = new Date();
    d.setDate(d.getDate() + daysAhead);
    d.setHours(hours, 0, 0, 0);
    const pad = (n: number) => n.toString().padStart(2, '0');
    setNewDateTime(`${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`);
  };

  const handleReschedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDateTime) {
      setError('Please select a valid date and time.');
      return;
    }

    const selectedTimestamp = new Date(newDateTime).getTime();
    if (selectedTimestamp <= Date.now()) {
      setError('Scheduled time must be in the future.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const isoString = new Date(newDateTime).toISOString();
      await calendarService.reschedulePost(post.project_id, post.id, isoString);
      setSuccessMsg('Post rescheduled successfully!');
      setTimeout(() => {
        onPostUpdated();
        onClose();
      }, 700);
    } catch (err: any) {
      setError(err?.response?.data?.message || err.message || 'Failed to reschedule post.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelSchedule = async () => {
    if (!window.confirm('Are you sure you want to cancel the scheduled release for this post?')) {
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await calendarService.cancelSchedule(post.project_id, post.id);
      setSuccessMsg('Schedule cancelled successfully.');
      setTimeout(() => {
        onPostUpdated();
        onClose();
      }, 700);
    } catch (err: any) {
      setError(err?.response?.data?.message || err.message || 'Failed to cancel schedule.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalDialog} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <div className={styles.modalHeaderLeft}>
            <span 
              className={styles.platformBadgePill}
              style={{
                backgroundColor: meta.accentBg,
                borderColor: meta.borderColor,
                color: meta.primaryColor
              }}
            >
              <RealBrandLogo platform={post.platform} size={15} />
              <span>{meta.name}</span>
            </span>
            <StatusBadge status={post.status} />
          </div>

          <button className={styles.modalCloseBtn} onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className={styles.modalBody}>
          <h2 className={styles.modalPostTitle}>
            {post.title || 'Untitled Post'}
          </h2>

          {post.projectName && (
            <div className={styles.modalProjectInfo}>
              <FolderKanban size={14} className="text-indigo-400" />
              <span>Campaign: <strong>{post.projectName}</strong></span>
            </div>
          )}

          {/* Attached Real Image Preview */}
          {mediaUrl && (
            <div className={styles.modalAttachedImageCard}>
              <img 
                src={mediaUrl} 
                alt={post.title || 'Attached Media'} 
                className={styles.modalAttachedImg}
                loading="lazy"
              />
              <div className={styles.modalAttachedImgOverlay}>
                <span>Verified High-Res Media</span>
              </div>
            </div>
          )}

          <div className={styles.modalCaptionCard}>
            <label className={styles.modalFieldLabel}>Caption Content</label>
            <div className={styles.modalCaptionText}>
              {cleanCaption}
            </div>
            <div className={styles.captionMetaFooter}>
              <span>{cleanCaption.length} characters</span>
              <span>{cleanCaption.split(/\s+/).filter(Boolean).length} words</span>
            </div>
          </div>

          {/* Reschedule Form */}
          <form onSubmit={handleReschedule} className={styles.rescheduleSection}>
            <div className="flex items-center justify-between">
              <label className={styles.modalFieldLabel}>
                <Clock size={14} />
                <span>Reschedule Release Time</span>
              </label>

              <div className={styles.presetButtonsRow}>
                <button
                  type="button"
                  className={styles.presetTimeBtn}
                  onClick={() => applyReschedulePreset(1, 10)}
                >
                  Tomorrow 10 AM
                </button>
                <button
                  type="button"
                  className={styles.presetTimeBtn}
                  onClick={() => applyReschedulePreset(3, 16)}
                >
                  +3 Days 4 PM
                </button>
              </div>
            </div>

            <div className={styles.rescheduleInputRow}>
              <input
                type="datetime-local"
                className={styles.datetimeInput}
                value={newDateTime}
                onChange={(e) => setNewDateTime(e.target.value)}
                disabled={isSubmitting}
              />
              <button 
                type="submit" 
                className={styles.rescheduleSubmitBtn}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Updating...' : 'Update Schedule'}
              </button>
            </div>
          </form>

          {error && (
            <div className={styles.modalAlertError}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className={styles.modalAlertSuccess}>
              <Check size={15} />
              <span>{successMsg}</span>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className={styles.modalFooter}>
          <div className={styles.modalFooterLeft}>
            {post.status === 'SCHEDULED' && (
              <button
                type="button"
                className={styles.dangerBtn}
                onClick={handleCancelSchedule}
                disabled={isSubmitting}
                title="Cancel publication schedule"
              >
                <Trash2 size={14} /> Unschedule
              </button>
            )}
          </div>

          <div className={styles.modalFooterRight}>
            <button
              type="button"
              className={styles.secondaryBtn}
              onClick={() => window.location.href = '/create'}
            >
              <Edit3 size={14} /> Open in Studio
            </button>
            <button
              type="button"
              className={styles.primaryBtn}
              onClick={onClose}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
