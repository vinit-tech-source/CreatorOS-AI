import { useRef, useState, useCallback } from 'react';
import { StudioState, CanvasElement } from '../CreateStudio';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import { Trash2, Type, Move, Sparkles, Wand2, Palette } from 'lucide-react';
import styles from './CanvasArea.module.css';

interface CanvasAreaProps {
  state: StudioState;
  format: ContentFormat;
  platformConfig: PlatformConfig;
  activeTool: string;
  onSelectElement: (id: string | null) => void;
  onUpdateElement: (id: string, updates: Partial<CanvasElement>) => void;
  onDeleteElement: (id: string) => void;
  onAddText: () => void;
}

interface DragState {
  elId: string;
  startX: number;
  startY: number;
  origX: number;
  origY: number;
}

// 640px display size provides a much more generous, crisp canvas view
const DISPLAY_MAX = 640;

const CARD_THEMES = [
  { id: 'obsidian', name: 'Obsidian', bg: 'radial-gradient(ellipse at top left, #1e1b4b 0%, #080811 75%)', border: 'rgba(99, 102, 241, 0.3)' },
  { id: 'cyber', name: 'Cyber Glow', bg: 'radial-gradient(ellipse at bottom right, rgba(139,92,246,0.3) 0%, #06060f 80%)', border: 'rgba(168, 85, 247, 0.4)' },
  { id: 'sunset', name: 'Sunset Bold', bg: 'radial-gradient(ellipse at top right, rgba(244,63,94,0.25) 0%, rgba(245,158,11,0.15) 50%, #070710 80%)', border: 'rgba(244, 63, 94, 0.35)' },
  { id: 'emerald', name: 'Emerald Tech', bg: 'radial-gradient(ellipse at center, rgba(16,185,129,0.2) 0%, #040907 80%)', border: 'rgba(16, 185, 129, 0.35)' },
  { id: 'slate', name: 'Minimal Slate', bg: 'linear-gradient(145deg, #181824, #0a0a12)', border: 'rgba(255,255,255,0.12)' },
];

export function CanvasArea({
  state, format, platformConfig, activeTool, onSelectElement, onUpdateElement, onDeleteElement, onAddText
}: CanvasAreaProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [currentTheme, setCurrentTheme] = useState(CARD_THEMES[0]);

  const scaleX = DISPLAY_MAX / format.canvasW;
  const scaleY = (DISPLAY_MAX * (format.canvasH / format.canvasW)) / format.canvasH;
  const scale = Math.min(scaleX, scaleY);
  const displayW = Math.round(format.canvasW * scale);
  const displayH = Math.round(format.canvasH * scale);

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      onSelectElement(null);
      if (activeTool === 'text') onAddText();
    }
  }, [activeTool, onSelectElement, onAddText]);

  const handleMouseDown = useCallback((e: React.MouseEvent, elId: string) => {
    e.stopPropagation();
    onSelectElement(elId);
    setDrag({
      elId,
      startX: e.clientX,
      startY: e.clientY,
      origX: state.elements.find(el => el.id === elId)?.x || 0,
      origY: state.elements.find(el => el.id === elId)?.y || 0
    });
  }, [onSelectElement, state.elements]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!drag) return;
    const dx = (e.clientX - drag.startX) / scale;
    const dy = (e.clientY - drag.startY) / scale;
    onUpdateElement(drag.elId, { x: Math.round(drag.origX + dx), y: Math.round(drag.origY + dy) });
  }, [drag, scale, onUpdateElement]);

  const handleMouseUp = useCallback(() => setDrag(null), []);
  const handleDoubleClick = useCallback((e: React.MouseEvent, elId: string) => {
    e.stopPropagation();
    setEditingId(elId);
  }, []);
  const handleBlur = useCallback(() => setEditingId(null), []);

  // Smart Auto-Balance: spaces elements cleanly so nothing ever overlaps
  const handleAutoBalance = useCallback(() => {
    if (state.elements.length === 0) return;
    const cardH = format.canvasH;
    const cardW = format.canvasW;
    const padding = 32;
    const contentW = cardW - (padding * 2);

    const textElements = state.elements.filter(el => el.type === 'text');
    const shapeElements = state.elements.filter(el => el.type === 'shape');

    let currentY = 30;
    textElements.forEach((el, index) => {
      if (index === 0 && el.fontSize && el.fontSize <= 13) {
        // Tag / Badge
        onUpdateElement(el.id, { x: padding, y: currentY, w: contentW, h: 24, textAlign: 'center' });
        currentY += 34;
      } else if (index === 0 || (index === 1 && textElements.length > 2)) {
        // Headline
        onUpdateElement(el.id, { x: padding, y: currentY, w: contentW, h: 70, textAlign: 'center', fontSize: 21 });
        currentY += 78;
      } else if (index === textElements.length - 1 && el.fontSize && el.fontSize <= 13) {
        // CTA text at bottom
        onUpdateElement(el.id, { x: cardW / 2 - 70, y: cardH - 46, w: 140, h: 22, textAlign: 'center' });
      } else {
        // Body / takeaway
        onUpdateElement(el.id, { x: padding + 15, y: currentY, w: contentW - 30, h: 55, textAlign: 'center', fontSize: 13 });
        currentY += 60;
      }
    });

    shapeElements.forEach(shape => {
      // Dock shape pill to bottom CTA
      onUpdateElement(shape.id, { x: cardW / 2 - 70, y: cardH - 52, w: 140, h: 32, borderRadius: 16 });
    });
  }, [state.elements, format, onUpdateElement]);

  return (
    <div className={styles.wrapper}>
      {/* Canvas Top Control Bar */}
      <div className={styles.canvasTopBar}>
        <div className={styles.canvasMeta}>
          <span className={styles.formatIcon}>{format.icon}</span>
          <span className={styles.formatName}>{format.label}</span>
          <span className={styles.formatDimensions}>{format.canvasW}×{format.canvasH} · {format.aspectRatio}</span>
        </div>

        {/* Theme Pills */}
        <div className={styles.themeSelector}>
          <Palette size={13} className={styles.themeIcon} />
          {CARD_THEMES.map(theme => (
            <button
              key={theme.id}
              className={`${styles.themePill} ${currentTheme.id === theme.id ? styles.themePillActive : ''}`}
              onClick={() => setCurrentTheme(theme)}
              title={theme.name}
            >
              {theme.name.split(' ')[0]}
            </button>
          ))}
        </div>

        <div className={styles.canvasQuickActions}>
          <button
            className={styles.canvasActionBtn}
            onClick={handleAutoBalance}
            title="Auto-space elements cleanly so nothing overlaps"
          >
            <Wand2 size={13} />
            <span>Auto-Balance</span>
          </button>
          <button
            className={styles.canvasActionBtn}
            onClick={onAddText}
            title="Add text to canvas"
          >
            <Type size={13} />
            <span>Add Text</span>
          </button>
        </div>
      </div>

      {/* The Canvas Viewport */}
      <div
        className={styles.canvasOuter}
        style={{ width: displayW, height: displayH }}
      >
        <div
          ref={canvasRef}
          className={styles.canvas}
          style={{
            width: displayW,
            height: displayH,
            cursor: activeTool === 'text' ? 'text' : activeTool === 'select' ? 'default' : 'crosshair',
            background: currentTheme.bg,
            borderColor: currentTheme.border,
            boxShadow: `0 32px 80px rgba(0,0,0,0.7), 0 0 40px ${currentTheme.border}30, 0 0 0 1px rgba(255,255,255,0.06)`,
          }}
          onClick={handleCanvasClick}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          {/* Elements */}
          {state.elements.map(el => {
            const isSelected = state.selectedElementId === el.id;
            const isEditing = editingId === el.id;
            const x = Math.round(el.x * scale);
            const y = Math.round(el.y * scale);
            const w = Math.round(el.w * scale);
            const h = Math.round(el.h * scale);
            const fontSize = Math.max(10, Math.round((el.fontSize || 16) * scale));

            return (
              <div
                key={el.id}
                className={`${styles.element} ${isSelected ? styles.elementSelected : ''}`}
                style={{
                  left: x,
                  top: y,
                  width: w,
                  height: h,
                  zIndex: el.zIndex,
                  borderColor: isSelected ? platformConfig.accentColor : undefined,
                }}
                onMouseDown={(e) => handleMouseDown(e, el.id)}
                onDoubleClick={(e) => handleDoubleClick(e, el.id)}
              >
                {el.type === 'text' ? (
                  isEditing ? (
                    <textarea
                      autoFocus
                      className={styles.textEditor}
                      style={{
                        fontSize,
                        color: el.color || '#fff',
                        fontWeight: el.fontWeight || '700',
                        textAlign: el.textAlign || 'center',
                        height: h,
                      }}
                      value={el.content}
                      onChange={e => onUpdateElement(el.id, { content: e.target.value })}
                      onBlur={handleBlur}
                    />
                  ) : (
                    <div
                      className={styles.textEl}
                      style={{
                        fontSize,
                        color: el.color || '#fff',
                        fontWeight: el.fontWeight || '700',
                        textAlign: el.textAlign || 'center',
                        textShadow: '0 2px 8px rgba(0,0,0,0.5)',
                      }}
                    >
                      {el.content}
                    </div>
                  )
                ) : el.type === 'shape' ? (
                  <div
                    className={styles.shapeEl}
                    style={{
                      backgroundColor: el.backgroundColor || platformConfig.accentColor,
                      borderRadius: (el.borderRadius || 0) * scale,
                      width: '100%',
                      height: '100%',
                      boxShadow: `0 4px 16px ${el.backgroundColor || platformConfig.accentColor}40`,
                    }}
                  />
                ) : el.type === 'image' ? (
                  <img
                    src={el.src || el.content}
                    alt=""
                    className={styles.imageEl}
                    style={{
                      borderRadius: (el.borderRadius || 12) * scale,
                      boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
                    }}
                  />
                ) : null}

                {/* Selection floating toolbar */}
                {isSelected && !isEditing && (
                  <div className={styles.selectionOverlay}>
                    <button
                      className={styles.deleteBtn}
                      onClick={(e) => { e.stopPropagation(); onDeleteElement(el.id); }}
                      title="Delete element"
                    >
                      <Trash2 size={12} />
                    </button>
                    {el.type === 'text' && (
                      <button
                        className={styles.editBtn}
                        onClick={(e) => { e.stopPropagation(); setEditingId(el.id); }}
                        title="Edit text"
                      >
                        <Type size={12} />
                      </button>
                    )}
                    <div className={styles.moveHandle} title="Drag to move"><Move size={12} /></div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Empty state */}
          {state.elements.length === 0 && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon} style={{ borderColor: platformConfig.accentColor + '60' }}>
                <Sparkles size={28} style={{ color: platformConfig.accentColor }} />
              </div>
              <h4 className={styles.emptyTitle}>Graphic Canvas is Empty</h4>
              <p className={styles.emptyText}>
                Click <strong>Auto-Balance</strong>, add elements from the left dock, or use <strong>AI Assist</strong> to generate a design card.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
