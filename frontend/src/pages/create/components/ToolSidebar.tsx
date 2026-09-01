import { MousePointer2, Type, Image, Shapes, Sparkles, LayoutTemplate, Quote, ListOrdered, TrendingUp, Bookmark } from 'lucide-react';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import styles from './ToolSidebar.module.css';

interface ToolSidebarProps {
  activeTool: string;
  onSelectTool: (tool: any) => void;
  onAddText: () => void;
  onAddMedia: () => void;
  onAddShape: (shape: 'rect' | 'circle') => void;
  onApplyTemplate?: (templateId: string) => void;
  platformConfig: PlatformConfig;
  format: ContentFormat;
}

const tools = [
  { id: 'select', icon: MousePointer2, label: 'Select' },
  { id: 'templates', icon: LayoutTemplate, label: 'Templates' },
  { id: 'text', icon: Type, label: 'Text' },
  { id: 'shapes', icon: Shapes, label: 'Shapes' },
  { id: 'media', icon: Image, label: 'Media' },
  { id: 'ai', icon: Sparkles, label: 'AI Magic' },
];

const TEMPLATES = [
  { id: 'quote', name: 'Thought Leader Quote', icon: Quote, desc: 'Big quote mark with punchy insight' },
  { id: 'tips', name: '3-Step Framework', icon: ListOrdered, desc: 'Numbered actionable takeaways' },
  { id: 'stat', name: 'Key Stat / Metric', icon: TrendingUp, desc: 'Giant number with headline' },
  { id: 'minimal', name: 'Minimal Header', icon: Bookmark, desc: 'Clean tag, title, and CTA pill' },
];

export function ToolSidebar({
  activeTool, onSelectTool, onAddText, onAddMedia, onAddShape, onApplyTemplate, platformConfig
}: ToolSidebarProps) {
  const handleToolClick = (toolId: string) => {
    onSelectTool(toolId);
    if (toolId === 'text') onAddText();
    if (toolId === 'media') onAddMedia();
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.toolList}>
        {tools.map(tool => {
          const Icon = tool.icon;
          const isActive = activeTool === tool.id;
          return (
            <button
              key={tool.id}
              className={`${styles.toolBtn} ${isActive ? styles.toolBtnActive : ''}`}
              onClick={() => handleToolClick(tool.id)}
              style={isActive ? { '--accent': platformConfig.accentColor } as any : {}}
              title={tool.label}
            >
              <Icon size={18} />
              <span className={styles.toolLabel}>{tool.label}</span>
            </button>
          );
        })}
      </div>

      {/* Templates sub-panel */}
      {activeTool === 'templates' && (
        <div className={styles.subPanel}>
          <div className={styles.subPanelTitle}>Card Layouts</div>
          <div className={styles.templateList}>
            {TEMPLATES.map(tmpl => {
              const TIcon = tmpl.icon;
              return (
                <button
                  key={tmpl.id}
                  className={styles.templateItem}
                  onClick={() => onApplyTemplate?.(tmpl.id)}
                >
                  <div className={styles.templateIcon}>
                    <TIcon size={14} style={{ color: platformConfig.accentColor }} />
                  </div>
                  <div className={styles.templateInfo}>
                    <div className={styles.templateName}>{tmpl.name}</div>
                    <div className={styles.templateDesc}>{tmpl.desc}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Shape sub-panel */}
      {activeTool === 'shapes' && (
        <div className={styles.subPanel}>
          <div className={styles.subPanelTitle}>Shapes</div>
          <button className={styles.shapeBtn} onClick={() => onAddShape('rect')}>
            <div className={styles.shapeRect} style={{ borderColor: platformConfig.accentColor }} />
            Rectangle Pill
          </button>
          <button className={styles.shapeBtn} onClick={() => onAddShape('circle')}>
            <div className={styles.shapeCircle} style={{ borderColor: platformConfig.accentColor }} />
            Circle Badge
          </button>
        </div>
      )}
    </div>
  );
}
