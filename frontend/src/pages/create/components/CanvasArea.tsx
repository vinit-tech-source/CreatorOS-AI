import { useRef, useState, useCallback } from 'react';
import { StudioState, CanvasElement } from '../CreateStudio';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import { Trash2, Type, Move } from 'lucide-react';
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

// Scale: canvas is always rendered at DISPLAY_SIZE but logically at canvasW/canvasH
const DISPLAY_MAX = 480;

export function CanvasArea({
  state, format, platformConfig, activeTool, onSelectElement, onUpdateElement, onDeleteElement, onAddText
}: CanvasAreaProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const scaleX = DISPLAY_MAX / format.canvasW;
  const scaleY = (DISPLAY_MAX * (format.canvasH / format.canvasW)) / format.canvasH;
  const scale = Math.min(scaleX, scaleY);
  const displayW = format.canvasW * scale;
  const displayH = format.canvasH * scale;

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      onSelectElement(null);
      if (activeTool === 'text') {
        onAddText();
      }
    }
  }, [activeTool, onSelectElement, onAddText]);

  const handleMouseDown = useCallback((e: React.MouseEvent, elId: string) => {
    e.stopPropagation();
    onSelectElement(elId);
    setDrag({ elId, startX: e.clientX, startY: e.clientY, origX: state.elements.find(el => el.id === elId)?.x || 0, origY: state.elements.find(el => el.id === elId)?.y || 0 });
  }, [onSelectElement, state.elements]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!drag) return;
    const dx = (e.clientX - drag.startX) / scale;
    const dy = (e.clientY - drag.startY) / scale;
    onUpdateElement(drag.elId, { x: drag.origX + dx, y: drag.origY + dy });
  }, [drag, scale, onUpdateElement]);

  const handleMouseUp = useCallback(() => setDrag(null), []);

  const handleDoubleClick = useCallback((e: React.MouseEvent, elId: string) => {
    e.stopPropagation();
    setEditingId(elId);
  }, []);

  const handleBlur = useCallback(() => setEditingId(null), []);

  return (
    <div className={styles.wrapper}>
      {/* Canvas Label */}
      <div className={styles.canvasLabel}>
        <span style={{ background: platformConfig.gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          {format.label}
        </span>
        <span className={styles.canvasDims}>{format.canvasW}×{format.canvasH} · {format.aspectRatio}</span>
      </div>

      {/* The Canvas */}
      <div
        className={styles.canvasOuter}
        style={{ width: displayW, height: displayH }}
      >
        {/* Checkerboard background hint */}
        <div className={styles.canvasChecker} />
        
        {/* Platform-tinted canvas background */}
        <div
          ref={canvasRef}
          className={styles.canvas}
          style={{
            width: displayW,
            height: displayH,
            cursor: activeTool === 'text' ? 'text' : activeTool === 'select' ? 'default' : 'crosshair',
            background: `linear-gradient(145deg, rgba(20,20,30,0.98), rgba(10,10,18,0.98))`,
            borderColor: platformConfig.accentColor + '40',
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
            const x = el.x * scale;
            const y = el.y * scale;
            const w = el.w * scale;
            const h = el.h * scale;
            const fontSize = (el.fontSize || 16) * scale;

            return (
              <div
                key={el.id}
                className={`${styles.element} ${isSelected ? styles.elementSelected : ''}`}
                style={{ left: x, top: y, width: w, height: h, zIndex: el.zIndex }}
                onMouseDown={(e) => handleMouseDown(e, el.id)}
                onDoubleClick={(e) => handleDoubleClick(e, el.id)}
              >
                {el.type === 'text' ? (
                  isEditing ? (
                    <textarea
                      autoFocus
                      className={styles.textEditor}
                      style={{ fontSize, color: el.color, fontWeight: el.fontWeight, textAlign: el.textAlign, height: h }}
                      value={el.content}
                      onChange={e => onUpdateElement(el.id, { content: e.target.value })}
                      onBlur={handleBlur}
                    />
                  ) : (
                    <div
                      className={styles.textEl}
                      style={{ fontSize, color: el.color, fontWeight: el.fontWeight, textAlign: el.textAlign }}
                    >
                      {el.content}
                    </div>
                  )
                ) : el.type === 'shape' ? (
                  <div
                    className={styles.shapeEl}
                    style={{ backgroundColor: el.backgroundColor, borderRadius: el.borderRadius || 0, width: '100%', height: '100%' }}
                  />
                ) : null}

                {/* Selection controls */}
                {isSelected && !isEditing && (
                  <div className={styles.selectionOverlay}>
                    <button className={styles.deleteBtn} onClick={(e) => { e.stopPropagation(); onDeleteElement(el.id); }}>
                      <Trash2 size={11} />
                    </button>
                    <div className={styles.moveHandle}><Move size={11} /></div>
                    {el.type === 'text' && (
                      <button className={styles.editBtn} onClick={(e) => { e.stopPropagation(); setEditingId(el.id); }}>
                        <Type size={11} />
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Empty state */}
          {state.elements.length === 0 && (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon} style={{ borderColor: platformConfig.accentColor + '60' }}>
                <span style={{ fontSize: '2rem' }}>{format.icon}</span>
              </div>
              <p className={styles.emptyText}>Click to add a text element, or use the AI Assist button above.</p>
            </div>
          )}
        </div>
        
        {/* Corner resize dots */}
        <div className={styles.cornerTL} />
        <div className={styles.cornerTR} />
        <div className={styles.cornerBL} />
        <div className={styles.cornerBR} />
      </div>

      {/* Character count if there's a caption limit */}
      {format.charLimit > 0 && state.caption && (
        <div className={styles.charCounter}>
          <div className={styles.charCountBar}>
            <div className={styles.charCountFill} style={{ width: `${Math.min((state.caption.length / format.charLimit) * 100, 100)}%`, backgroundColor: state.caption.length > format.charLimit * 0.9 ? '#ef4444' : platformConfig.accentColor }} />
          </div>
          <span className={state.caption.length > format.charLimit ? styles.charCountOver : ''}>
            {state.caption.length} / {format.charLimit}
          </span>
        </div>
      )}
    </div>
  );
}
