import { MousePointer2, Type, Image, Shapes, MessageSquare, Sparkles, LayoutTemplate } from 'lucide-react';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import styles from './ToolSidebar.module.css';

interface ToolSidebarProps {
  activeTool: string;
  onSelectTool: (tool: any) => void;
  onAddText: () => void;
  onAddShape: (shape: 'rect' | 'circle') => void;
  platformConfig: PlatformConfig;
  format: ContentFormat;
}

const tools = [
  { id: 'select', icon: MousePointer2, label: 'Select' },
  { id: 'text', icon: Type, label: 'Text' },
  { id: 'media', icon: Image, label: 'Media' },
  { id: 'shapes', icon: Shapes, label: 'Shapes' },
  { id: 'captions', icon: MessageSquare, label: 'Caption' },
  { id: 'templates', icon: LayoutTemplate, label: 'Templates' },
  { id: 'ai', icon: Sparkles, label: 'AI' },
];

export function ToolSidebar({ activeTool, onSelectTool, onAddText, onAddShape, platformConfig }: Omit<ToolSidebarProps, 'format'> & { format: ContentFormat }) {
  const handleToolClick = (toolId: string) => {
    onSelectTool(toolId);
    if (toolId === 'text') onAddText();
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

      {/* Shape sub-panel */}
      {activeTool === 'shapes' && (
        <div className={styles.subPanel}>
          <div className={styles.subPanelTitle}>Shapes</div>
          <button className={styles.shapeBtn} onClick={() => onAddShape('rect')}>
            <div className={styles.shapeRect} style={{ borderColor: platformConfig.accentColor }} />
            Rectangle
          </button>
          <button className={styles.shapeBtn} onClick={() => onAddShape('circle')}>
            <div className={styles.shapeCircle} style={{ borderColor: platformConfig.accentColor }} />
            Circle
          </button>
        </div>
      )}
    </div>
  );
}
