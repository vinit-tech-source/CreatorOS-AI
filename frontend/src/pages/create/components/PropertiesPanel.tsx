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
          {format.id === 'article' ? 'Title' : 'Caption'}
          {format.charLimit > 0 && (
            <span className={`${styles.charCount} ${state.caption.length > format.charLimit * 0.9 ? styles.charCountWarn : ''}`}>
              {state.caption.length}/{format.charLimit}
            </span>
          )}
        </div>
        <textarea
          className={styles.captionInput}
          style={{ borderColor: platformConfig.accentColor + '40' }}
          placeholder={format.id === 'article' ? 'Your article title...' : `Write your ${platformConfig.name} caption…`}
          value={state.caption}
          onChange={e => onStateChange({ caption: e.target.value })}
          rows={5}
          maxLength={format.charLimit > 0 ? format.charLimit : undefined}
        />
      </div>

      {/* Hashtags */}
      {format.maxHashtags && (
        <div className={styles.section}>
          <div className={styles.sectionTitle}>
            Hashtags
            <span className={styles.charCount}>{state.hashtags.length}/{format.maxHashtags}</span>
          </div>
          <input
            className={styles.hashInput}
            placeholder="#trending #creator"
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
          <div className={styles.tagList}>
            {state.hashtags.map((tag, i) => (
              <span key={i} className={styles.tag} style={{ borderColor: platformConfig.accentColor + '50', color: platformConfig.accentColor }}>
                {tag}
                <button className={styles.tagRemove} onClick={() => onStateChange({ hashtags: state.hashtags.filter((_, idx) => idx !== i) })}>×</button>
              </span>
            ))}
          </div>
        </div>
      )}

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
