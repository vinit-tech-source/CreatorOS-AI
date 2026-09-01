import { StudioState, CanvasElement } from '../CreateStudio';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import { TwitterPreview } from '../../../components/previews/TwitterPreview';
import { LinkedInPreview } from '../../../components/previews/LinkedInPreview';
import styles from './PlatformPreview.module.css';

interface PlatformPreviewProps {
  state: StudioState;
  platformConfig: PlatformConfig;
  format: ContentFormat;
}

// Helper to render elements inside a specific aspect ratio container
function ReadOnlyCanvas({ elements, format }: { elements: CanvasElement[]; format: ContentFormat }) {
  if (elements.length === 0) return null;
  return (
    <div className={styles.roCanvas}>
      {elements.map(el => {
        const left = (el.x / format.canvasW) * 100 + '%';
        const top = (el.y / format.canvasH) * 100 + '%';
        const width = (el.w / format.canvasW) * 100 + '%';
        const height = (el.h / format.canvasH) * 100 + '%';
        const fontSize = (el.fontSize || 16) / format.canvasW * 100 + 'cqi';

        return (
          <div key={el.id} className={styles.roElement} style={{ left, top, width, height, zIndex: el.zIndex }}>
            {el.type === 'text' ? (
              <div
                className={styles.roText}
                style={{ fontSize, color: el.color, fontWeight: el.fontWeight, textAlign: el.textAlign }}
              >
                {el.content}
              </div>
            ) : el.type === 'shape' ? (
              <div
                className={styles.roShape}
                style={{ backgroundColor: el.backgroundColor, borderRadius: el.borderRadius || 0 }}
              />
            ) : el.type === 'image' ? (
              <img
                src={el.src || el.content}
                alt=""
                style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: (el.borderRadius || 8), display: 'block' }}
              />
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

function InstagramFeedPreview({ caption, hashtags, elements, format }: { caption: string; hashtags: string[]; elements: CanvasElement[]; format: ContentFormat }) {
  return (
    <div className={styles.igContainer}>
      <div className={styles.igHeader}>
        <div className={styles.igAvatar}>C</div>
        <div className={styles.igAuthorInfo}>
          <div className={styles.igUsername}>creator_studio</div>
          <div className={styles.igFollowed}>• Follow</div>
        </div>
        <div className={styles.igMore}>···</div>
      </div>
      <div className={styles.igCanvas}>
        {elements.length > 0 ? (
          <ReadOnlyCanvas elements={elements} format={format} />
        ) : (
          <div className={styles.igPlaceholder}>
            <span>📸</span>
            <span className={styles.igPlaceholderText}>Your visual content</span>
          </div>
        )}
      </div>
      <div className={styles.igActions}>
        <div className={styles.igActionLeft}>
          <button className={styles.igActionBtn}>❤️</button>
          <button className={styles.igActionBtn}>💬</button>
          <button className={styles.igActionBtn}>✈️</button>
        </div>
        <button className={styles.igActionBtn}>🔖</button>
      </div>
      <div className={styles.igLikes}>1,234 likes</div>
      <div className={styles.igCaption}>
        <span className={styles.igCaptionUser}>creator_studio</span>{' '}
        {caption || 'Your caption will appear here…'}
        {hashtags.length > 0 && <div className={styles.igHashtags}>{hashtags.join(' ')}</div>}
      </div>
    </div>
  );
}

function TikTokPreview({ caption, hashtags, elements, format }: { caption: string; hashtags: string[]; elements: CanvasElement[]; format: ContentFormat }) {
  return (
    <div className={styles.ttContainer}>
      <div className={styles.ttVideoArea}>
        {elements.length > 0 && <ReadOnlyCanvas elements={elements} format={format} />}
        <div className={styles.ttOverlay}>
          <div className={styles.ttBottomInfo}>
            <div className={styles.ttUsername}>@creator_studio</div>
            <div className={styles.ttCaption}>{caption || 'Your caption…'}</div>
            <div className={styles.ttHashtags}>{hashtags.join(' ')}</div>
          </div>
        </div>
      </div>
      <div className={styles.ttSidebar}>
        <div className={styles.ttAction}>❤️<span>12K</span></div>
        <div className={styles.ttAction}>💬<span>234</span></div>
        <div className={styles.ttAction}>🔖<span>1.2K</span></div>
        <div className={styles.ttAction}>↗️<span>Share</span></div>
      </div>
    </div>
  );
}

function GenericPreview({ caption, platformConfig, format, elements }: { caption: string; platformConfig: PlatformConfig; format: ContentFormat; elements: CanvasElement[] }) {
  return (
    <div className={styles.genericContainer}>
      <div className={styles.genericContent} style={{ background: platformConfig.gradient }}>
        {elements.length > 0 ? (
          <ReadOnlyCanvas elements={elements} format={format} />
        ) : (
          <>
            <span style={{ fontSize: '3rem' }}>{format.icon}</span>
            <div className={styles.genericLabel}>{platformConfig.name} {format.label}</div>
          </>
        )}
      </div>
      <div className={styles.genericCaption}>{caption || 'Your caption will appear here…'}</div>
    </div>
  );
}

export function PlatformPreview({ state, platformConfig, format }: PlatformPreviewProps) {
  const caption = [state.caption, ...state.hashtags].join(' ');

  return (
    <div className={styles.wrapper}>
      <div className={styles.previewLabel}>
        <span>Platform Preview</span>
        <span className={styles.previewSub}>This is how your content will look on {platformConfig.name}</span>
      </div>

      <div className={styles.deviceFrame}>
        {platformConfig.id === 'twitter' ? (
          <TwitterPreview
            content={caption || 'Your content will appear here.'}
            mediaSlot={state.elements.length > 0 ? <ReadOnlyCanvas elements={state.elements} format={format} /> : undefined}
          />
        ) : platformConfig.id === 'linkedin' ? (
          <LinkedInPreview content={caption || 'Your content will appear here.'} />
        ) : platformConfig.id === 'instagram' ? (
          <InstagramFeedPreview caption={state.caption} hashtags={state.hashtags} elements={state.elements} format={format} />
        ) : platformConfig.id === 'tiktok' ? (
          <TikTokPreview caption={state.caption} hashtags={state.hashtags} elements={state.elements} format={format} />
        ) : (
          <GenericPreview caption={state.caption} platformConfig={platformConfig} format={format} elements={state.elements} />
        )}
      </div>
    </div>
  );
}
