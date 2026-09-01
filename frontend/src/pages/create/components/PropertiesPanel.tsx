import { useState } from 'react';
import { StudioState, CanvasElement } from '../CreateStudio';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import { Trash2, AlignLeft, AlignCenter, AlignRight, Bold, Sliders, Activity } from 'lucide-react';
import { ContentQualityEngine } from './ContentQualityEngine';
import styles from './PropertiesPanel.module.css';

interface PropertiesPanelProps {
  selectedElement: CanvasElement | null;
  state: StudioState;
  platformConfig: PlatformConfig;
  format: ContentFormat;
  onUpdateElement: (id: string, updates: Partial<CanvasElement>) => void;
  onDeleteElement: (id: string) => void;
  onStateChange: (updates: Partial<StudioState>) => void;
}

export function PropertiesPanel({
  selectedElement, state, platformConfig, format,
  onUpdateElement, onDeleteElement, onStateChange
}: PropertiesPanelProps) {
  const [activeTab, setActiveTab] = useState<'properties' | 'quality'>('properties');

  return (
    <div className={styles.panel}>
      {/* Tabs */}
      <div className={styles.tabsContainer}>
        <button 
          className={`${styles.tabBtn} ${activeTab === 'properties' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('properties')}
        >
          <Sliders size={14} /> Properties
        </button>
        <button 
          className={`${styles.tabBtn} ${activeTab === 'quality' ? styles.tabBtnActive : ''}`}
          onClick={() => setActiveTab('quality')}
        >
          <Activity size={14} /> AI Score
        </button>
      </div>

      {activeTab === 'quality' ? (
        <ContentQualityEngine state={state} platformConfig={platformConfig} format={format} />
      ) : (
        <>
          {/* Platform Info */}
      <div className={styles.platformSection}>
        <div className={styles.platformGradientBar} style={{ background: platformConfig.gradient }} />
        <div className={styles.platformMeta}>
          <div className={styles.platformName}>{platformConfig.name}</div>
          <div className={styles.formatLabel}>{format.icon} {format.label}</div>
          <div className={styles.specs}>
            <span>{format.aspectRatio}</span>
            {format.charLimit > 0 && <span>{format.charLimit.toLocaleString()} ch limit</span>}
          </div>
        </div>
      </div>

      {/* Element Properties */}
      {selectedElement ? (
        <div className={styles.section}>
          <div className={styles.sectionTitle}>Element Properties</div>
          
          {selectedElement.type === 'text' && (
            <>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Font Size</label>
                <input
                  type="range"
                  min={8}
                  max={80}
                  value={selectedElement.fontSize || 16}
                  onChange={e => onUpdateElement(selectedElement.id, { fontSize: Number(e.target.value) })}
                  className={styles.rangeInput}
                  style={{ '--accent': platformConfig.accentColor } as any}
                />
                <span className={styles.rangeValue}>{selectedElement.fontSize || 16}px</span>
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel}>Color</label>
                <input
                  type="color"
                  value={selectedElement.color || '#ffffff'}
                  onChange={e => onUpdateElement(selectedElement.id, { color: e.target.value })}
                  className={styles.colorInput}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel}>Alignment</label>
                <div className={styles.alignBtns}>
                  {(['left', 'center', 'right'] as const).map(align => (
                    <button
                      key={align}
                      className={`${styles.alignBtn} ${selectedElement.textAlign === align ? styles.alignBtnActive : ''}`}
                      onClick={() => onUpdateElement(selectedElement.id, { textAlign: align })}
                      style={selectedElement.textAlign === align ? { color: platformConfig.accentColor } : {}}
                    >
                      {align === 'left' ? <AlignLeft size={14} /> : align === 'center' ? <AlignCenter size={14} /> : <AlignRight size={14} />}
                    </button>
                  ))}
                </div>
              </div>

              <div className={styles.field}>
                <label className={styles.fieldLabel}>Weight</label>
                <div className={styles.alignBtns}>
                  <button
                    className={`${styles.alignBtn} ${selectedElement.fontWeight === '400' ? styles.alignBtnActive : ''}`}
                    onClick={() => onUpdateElement(selectedElement.id, { fontWeight: '400' })}
                  >Normal</button>
                  <button
                    className={`${styles.alignBtn} ${selectedElement.fontWeight === '700' || selectedElement.fontWeight === 'bold' ? styles.alignBtnActive : ''}`}
                    onClick={() => onUpdateElement(selectedElement.id, { fontWeight: '700' })}
                  ><Bold size={14} /></button>
                  <button
                    className={`${styles.alignBtn} ${selectedElement.fontWeight === '900' ? styles.alignBtnActive : ''}`}
                    onClick={() => onUpdateElement(selectedElement.id, { fontWeight: '900' })}
                  >Black</button>
                </div>
              </div>
            </>
          )}

          {selectedElement.type === 'shape' && (
            <div className={styles.field}>
              <label className={styles.fieldLabel}>Fill Color</label>
              <input
                type="color"
                value={selectedElement.backgroundColor || '#4F46E5'}
                onChange={e => onUpdateElement(selectedElement.id, { backgroundColor: e.target.value + 'cc' })}
                className={styles.colorInput}
              />
            </div>
          )}

          {selectedElement.type === 'image' && (
            <>
              <div className={styles.field}>
                <label className={styles.fieldLabel}>Rounded Corners</label>
                <input
                  type="range"
                  min={0}
                  max={40}
                  value={selectedElement.borderRadius || 12}
                  onChange={e => onUpdateElement(selectedElement.id, { borderRadius: Number(e.target.value) })}
                  className={styles.rangeInput}
                  style={{ '--accent': platformConfig.accentColor } as any}
                />
                <span className={styles.rangeValue}>{selectedElement.borderRadius || 12}px</span>
              </div>
            </>
          )}

          <button className={styles.deleteBtn} onClick={() => onDeleteElement(selectedElement.id)}>
            <Trash2 size={14} />
            Delete Element
          </button>
        </div>
      ) : (
        <div className={styles.section}>
          <div className={styles.sectionTitle}>Canvas</div>
          <div className={styles.noSelection}>Select an element to edit its properties.</div>
        </div>
      )}

      {/* Caption / Copy Section */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>
          <span>{format.id === 'article' ? 'Article Content' : 'Post Caption'}</span>
          {format.charLimit > 0 && (
            <span className={`${styles.charCount} ${state.caption.length > format.charLimit ? styles.charCountWarn : ''}`}>
              {state.caption.length}/{format.charLimit}
            </span>
          )}
        </div>

        {/* Over limit warning with 1-click AI fix */}
        {format.charLimit > 0 && state.caption.length > format.charLimit && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '8px',
            padding: '0.45rem 0.75rem',
            fontSize: '0.75rem',
            color: '#f87171',
            gap: '0.5rem'
          }}>
            <span>Over limit by {state.caption.length - format.charLimit} chars</span>
            <button
              type="button"
              onClick={() => {
                // Smart truncate to closest sentence/word boundary under limit
                const target = state.caption.slice(0, format.charLimit - 5);
                const lastSentence = target.lastIndexOf('. ');
                const lastSpace = target.lastIndexOf(' ');
                const cutPoint = lastSentence > format.charLimit * 0.7 ? lastSentence + 1 : lastSpace > 0 ? lastSpace : target.length;
                onStateChange({ caption: state.caption.slice(0, cutPoint).trim() + '…' });
              }}
              style={{
                background: '#ef4444',
                color: '#fff',
                border: 'none',
                borderRadius: '5px',
                padding: '0.2rem 0.5rem',
                fontSize: '0.7rem',
                fontWeight: 700,
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              ✂️ Auto-Shorten
            </button>
          </div>
        )}

        <textarea
          className={styles.captionInput}
          style={{ borderColor: platformConfig.accentColor + '40' }}
          placeholder={format.id === 'article' ? 'Your article title...' : `Write your ${platformConfig.name} caption…`}
          value={state.caption}
          onChange={e => onStateChange({ caption: e.target.value })}
          rows={6}
        />

        {/* AI Quick Polish Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.15rem' }}>
          <button
            type="button"
            className={styles.alignBtn}
            style={{ fontSize: '0.7rem', padding: '0.25rem 0.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
            onClick={() => {
              const hooks = [
                'Most creators get this completely backwards: ',
                'The brutal truth about growing in 2026: ',
                'Stop scrolling if you care about your audience: ',
                'Here is the exact formula nobody is sharing: '
              ];
              const randomHook = hooks[Math.floor(Math.random() * hooks.length)];
              onStateChange({ caption: randomHook + state.caption });
            }}
          >
            ⚡ Add Hook
          </button>
          <button
            type="button"
            className={styles.alignBtn}
            style={{ fontSize: '0.7rem', padding: '0.25rem 0.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
            onClick={() => {
              if (format.charLimit > 0 && state.caption.length > format.charLimit) {
                const trimmed = state.caption.slice(0, format.charLimit - 25).trim();
                onStateChange({ caption: trimmed + '\n\nFull breakdown in thread 👇' });
              }
            }}
          >
            ✂️ Fit to {format.charLimit || 280}
          </button>
          <button
            type="button"
            className={styles.alignBtn}
            style={{ fontSize: '0.7rem', padding: '0.25rem 0.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}
            onClick={() => {
              const lines = state.caption.split('\n');
              const emojified = lines.map(l => l.trim() ? '✨ ' + l.replace(/^[•\-\*]\s*/, '') : '').join('\n');
              onStateChange({ caption: emojified });
            }}
          >
            ✨ Bullet Style
          </button>
        </div>
      </div>

      {/* Hashtags */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>
          <span>Hashtags</span>
          <span className={styles.charCount}>{state.hashtags.length}/{format.maxHashtags || 30}</span>
        </div>
        <input
          className={styles.hashInput}
          placeholder="Type #tag and press Enter"
          onKeyDown={e => {
            if (e.key === ' ' || e.key === 'Enter') {
              e.preventDefault();
              const val = (e.target as HTMLInputElement).value.trim();
              if (val && state.hashtags.length < (format.maxHashtags || 30)) {
                const tag = val.startsWith('#') ? val : '#' + val;
                onStateChange({ hashtags: [...state.hashtags, tag] });
                (e.target as HTMLInputElement).value = '';
              }
            }
          }}
        />
        {/* Suggested popular tags */}
        <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginTop: '0.2rem' }}>
          {['#creator', '#growth', '#buildinpublic', '#ai', '#tips'].filter(t => !state.hashtags.includes(t)).slice(0, 3).map(tag => (
            <button
              key={tag}
              type="button"
              onClick={() => onStateChange({ hashtags: [...state.hashtags, tag] })}
              style={{
                fontSize: '0.6875rem',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                color: 'rgba(255,255,255,0.5)',
                borderRadius: '6px',
                padding: '0.15rem 0.4rem',
                cursor: 'pointer'
              }}
            >
              + {tag}
            </button>
          ))}
        </div>
        <div className={styles.tagList}>
          {state.hashtags.map((tag, i) => (
            <span key={i} className={styles.tag} style={{ borderColor: platformConfig.accentColor + '50', color: platformConfig.accentColor }}>
              {tag}
              <button className={styles.tagRemove} onClick={() => onStateChange({ hashtags: state.hashtags.filter((_, idx) => idx !== i) })}>×</button>
            </span>
          ))}
        </div>
      </div>

      {/* Platform Guidance */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Platform Tips</div>
        <div className={styles.tipList}>
          <div className={styles.tip}>📐 {format.aspectRatio} aspect ratio</div>
          {format.charLimit > 0 && <div className={styles.tip}>📝 {format.charLimit.toLocaleString()} character limit</div>}
          {format.maxHashtags && <div className={styles.tip}># Up to {format.maxHashtags} hashtags</div>}
          {format.supportsCarousel && <div className={styles.tip}>🎠 Carousel: up to 10 slides</div>}
          {format.supportsMedia && <div className={styles.tip}>🖼️ Supports images & video</div>}
        </div>
      </div>
      </>
      )}
    </div>
  );
}
