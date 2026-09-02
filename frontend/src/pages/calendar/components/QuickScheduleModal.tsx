import { useState, useEffect } from 'react';
import { Project } from '../../../types';
import { calendarService } from '../../../services/api/calendarService';
import { RealBrandLogo, PLATFORM_METAS } from '../../../components/common/BrandLogos';
import { REAL_STOCK_PHOTOS, RealStockPhoto } from '../../../constants/realPhotography';
import { 
  X, 
  Sparkles, 
  Clock, 
  AlertCircle,
  Check,
  Image as ImageIcon,
  Trash2,
  Calendar as CalendarIcon,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import styles from '../ContentCalendar.module.css';

interface QuickScheduleModalProps {
  initialDate: Date | null;
  projects: Project[];
  onClose: () => void;
  onPostCreated: () => void;
}

const PLATFORM_LIST = ['INSTAGRAM', 'LINKEDIN', 'YOUTUBE', 'TIKTOK', 'X'];

export function QuickScheduleModal({ initialDate, projects, onClose, onPostCreated }: QuickScheduleModalProps) {
  const getDefaultDateTime = () => {
    const d = initialDate ? new Date(initialDate) : new Date();
    if (!initialDate || d.getTime() <= Date.now()) {
      d.setDate(d.getDate() + 1);
    }
    d.setHours(10, 0, 0, 0);

    const pad = (n: number) => n.toString().padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const [projectId, setProjectId] = useState<string>(projects[0]?.id || '');
  const [platform, setPlatform] = useState<string>('INSTAGRAM');
  const [title, setTitle] = useState<string>('');
  const [content, setContent] = useState<string>('');
  const [scheduledAt, setScheduledAt] = useState<string>(getDefaultDateTime());

  // Real Photo Attachment state
  const [selectedPhoto, setSelectedPhoto] = useState<RealStockPhoto | null>(null);
  const [showPhotoPicker, setShowPhotoPicker] = useState(false);
  const [customImageUrl, setCustomImageUrl] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (projects.length > 0 && !projectId) {
      setProjectId(projects[0].id);
    }
  }, [projects, projectId]);

  const activeMeta = PLATFORM_METAS[platform] || PLATFORM_METAS.INSTAGRAM;
  const charsRemaining = activeMeta.charLimit - content.length;
  const isOverLimit = charsRemaining < 0;

  // Preset time helpers
  const applyPreset = (daysAhead: number, hours: number) => {
    const d = new Date();
    d.setDate(d.getDate() + daysAhead);
    d.setHours(hours, 0, 0, 0);
    const pad = (n: number) => n.toString().padStart(2, '0');
    setScheduledAt(`${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!projectId) {
      setError('Please select a target project.');
      return;
    }
    if (!content.trim()) {
      setError('Please enter caption content for your post.');
      return;
    }
    if (isOverLimit) {
      setError(`Caption exceeds the ${activeMeta.charLimit} character limit for ${activeMeta.name}.`);
      return;
    }
    if (!scheduledAt) {
      setError('Please select a scheduled date and time.');
      return;
    }

    const targetDate = new Date(scheduledAt);
    if (targetDate.getTime() <= Date.now()) {
      setError('Scheduled time must be in the future.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Append image URL to content if an authentic photo was attached
      const imageUrl = selectedPhoto?.url || customImageUrl.trim();
      let finalContent = content.trim();
      if (imageUrl && !finalContent.includes(imageUrl)) {
        finalContent += `\n\n[Attached Media]: ${imageUrl}`;
      }

      await calendarService.quickCreateAndSchedule(projectId, {
        title: title.trim() || undefined,
        content: finalContent,
        platform,
        scheduled_at: targetDate.toISOString(),
      });

      setSuccess(true);
      setTimeout(() => {
        onPostCreated();
        onClose();
      }, 700);
    } catch (err: any) {
      setError(err?.response?.data?.message || err.message || 'Failed to schedule post.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalDialog} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.modalHeader}>
          <div className={styles.modalHeaderTitleGroup}>
            <div className={styles.quickCreateIconWrapper}>
              <Sparkles size={18} />
            </div>
            <div>
              <h3 className={styles.quickModalTitle}>Schedule New Post</h3>
              <p className={styles.quickModalSubtitle}>Platform-native post with verified brand styling and photography</p>
            </div>
          </div>

          <button className={styles.modalCloseBtn} onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className={styles.modalBody}>
          {/* Project Selector */}
          <div className={styles.quickModalField}>
            <label className={styles.modalFieldLabel}>Project Campaign</label>
            <select
              className={styles.modalSelect}
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              disabled={isSubmitting || projects.length === 0}
            >
              {projects.length === 0 ? (
                <option value="">No projects available in this workspace</option>
              ) : (
                projects.map(proj => (
                  <option key={proj.id} value={proj.id}>
                    {proj.name}
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Real Platform Selector */}
          <div className={styles.quickModalField}>
            <div className="flex items-center justify-between">
              <label className={styles.modalFieldLabel}>Target Platform</label>
              <span className={styles.bestTimeChip}>
                <Clock size={11} /> {activeMeta.bestTime}
              </span>
            </div>

            <div className={styles.platformPillsRow}>
              {PLATFORM_LIST.map(pId => {
                const meta = PLATFORM_METAS[pId];
                const isActive = platform === pId;

                return (
                  <button
                    type="button"
                    key={pId}
                    className={`${styles.platformSelectPill} ${isActive ? styles.platformPillActive : ''}`}
                    style={isActive ? {
                      borderColor: meta.primaryColor,
                      boxShadow: `0 0 12px ${meta.borderColor}`,
                      background: meta.accentBg,
                      color: '#ffffff'
                    } : {}}
                    onClick={() => setPlatform(pId)}
                  >
                    <RealBrandLogo platform={pId} size={18} />
                    <span>{meta.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Post Title */}
          <div className={styles.quickModalField}>
            <label className={styles.modalFieldLabel}>Post Title (Optional)</label>
            <input
              type="text"
              className={styles.modalTextInput}
              placeholder="e.g., Q3 Feature Announcement & Live Demo"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Post Content */}
          <div className={styles.quickModalField}>
            <div className="flex items-center justify-between">
              <label className={styles.modalFieldLabel}>
                Post Caption / Content <span className="text-rose-400">*</span>
              </label>
              <span 
                className={styles.charCounter}
                style={{ color: isOverLimit ? '#f87171' : charsRemaining < 100 ? '#fbbf24' : '#94a3b8' }}
              >
                {content.length} / {activeMeta.charLimit.toLocaleString()} chars
              </span>
            </div>

            <textarea
              className={styles.modalTextarea}
              rows={4}
              placeholder={`Write native copy tailored for ${activeMeta.name}...`}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {/* Real Photo / Media Attachment Section */}
          <div className={styles.mediaAttachmentSection}>
            <div 
              className={styles.mediaAttachmentHeader}
              onClick={() => setShowPhotoPicker(!showPhotoPicker)}
            >
              <div className="flex items-center gap-2">
                <ImageIcon size={15} className="text-indigo-400" />
                <span className="font-semibold text-slate-200 text-xs">
                  {selectedPhoto ? 'Attached Photo' : 'Attach Real Stock Photo'}
                </span>
                {selectedPhoto && (
                  <span className={styles.photoAttachedBadge}>1 Photo Attached</span>
                )}
              </div>
              <button type="button" className={styles.togglePickerBtn}>
                {showPhotoPicker ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </div>

            {/* Selected Photo Preview */}
            {selectedPhoto && (
              <div className={styles.selectedPhotoPreviewRow}>
                <img 
                  src={selectedPhoto.thumbUrl} 
                  alt={selectedPhoto.title} 
                  className={styles.selectedPhotoThumb} 
                />
                <div className={styles.selectedPhotoDetails}>
                  <span className={styles.selectedPhotoTitle}>{selectedPhoto.title}</span>
                  <span className={styles.selectedPhotoCategory}>Category: {selectedPhoto.category} • High Res Unsplash</span>
                </div>
                <button
                  type="button"
                  className={styles.removePhotoBtn}
                  onClick={() => setSelectedPhoto(null)}
                  title="Remove photo"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            )}

            {/* Curated Real Photography Grid */}
            {showPhotoPicker && !selectedPhoto && (
              <div className={styles.realPhotoGridContainer}>
                <p className={styles.photoGridSubtitle}>
                  Choose from curated authentic photography (no AI-generated images):
                </p>
                <div className={styles.realPhotoGrid}>
                  {REAL_STOCK_PHOTOS.slice(0, 6).map(photo => (
                    <div
                      key={photo.id}
                      className={styles.photoGridCard}
                      onClick={() => {
                        setSelectedPhoto(photo);
                        setShowPhotoPicker(false);
                      }}
                    >
                      <img 
                        src={photo.thumbUrl} 
                        alt={photo.title} 
                        className={styles.photoGridImg} 
                        loading="lazy"
                      />
                      <span className={styles.photoGridLabel}>{photo.title}</span>
                    </div>
                  ))}
                </div>

                <div className="mt-2 flex items-center gap-2">
                  <input
                    type="url"
                    className={styles.modalTextInput}
                    placeholder="Or paste any real photo URL (Unsplash, etc.)..."
                    value={customImageUrl}
                    onChange={(e) => setCustomImageUrl(e.target.value)}
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Schedule Datetime & Presets */}
          <div className={styles.quickModalField}>
            <div className="flex items-center justify-between">
              <label className={styles.modalFieldLabel}>
                <CalendarIcon size={14} /> Scheduled Date & Time
              </label>
              <div className={styles.presetButtonsRow}>
                <button 
                  type="button" 
                  className={styles.presetTimeBtn}
                  onClick={() => applyPreset(1, 10)}
                >
                  Tomorrow 10 AM
                </button>
                <button 
                  type="button" 
                  className={styles.presetTimeBtn}
                  onClick={() => applyPreset(2, 17)}
                >
                  In 2 Days 5 PM
                </button>
                <button 
                  type="button" 
                  className={styles.presetTimeBtn}
                  onClick={() => applyPreset(7, 9)}
                >
                  Next Week 9 AM
                </button>
              </div>
            </div>

            <input
              type="datetime-local"
              className={styles.datetimeInput}
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              disabled={isSubmitting}
            />
          </div>

          {error && (
            <div className={styles.modalAlertError}>
              <AlertCircle size={15} />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className={styles.modalAlertSuccess}>
              <Check size={15} />
              <span>Post scheduled successfully with verified brand settings! Adding to calendar...</span>
            </div>
          )}

          {/* Footer */}
          <div className={styles.modalFooter}>
            <button
              type="button"
              className={styles.secondaryBtn}
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={styles.primaryBtn}
              disabled={isSubmitting || projects.length === 0 || isOverLimit}
            >
              {isSubmitting ? 'Scheduling Post...' : 'Schedule Post'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
