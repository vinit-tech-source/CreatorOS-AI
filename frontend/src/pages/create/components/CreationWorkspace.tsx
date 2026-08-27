import { useState, useRef, useCallback } from 'react';
import { StudioState, CanvasElement } from '../CreateStudio';
import { PlatformConfig, getPlatformLogoUrl, platformConfigs } from '../../../constants/platformConfigs';
import { CanvasArea } from './CanvasArea';
import { ToolSidebar } from './ToolSidebar';
import { PropertiesPanel } from './PropertiesPanel';
import { PlatformPreview } from './PlatformPreview';
import { AICreationFlow, AIResult } from './AICreationFlow';
import {
  ArrowLeft, Save, Share2, Eye, Zap, ChevronDown, Sparkles, Wand2
} from 'lucide-react';
import styles from './CreationWorkspace.module.css';

interface CreationWorkspaceProps {
  state: StudioState;
  platformConfig: PlatformConfig;
  onBack: () => void;
  onStateChange: (updates: Partial<StudioState>) => void;
}

type ActiveTool = 'select' | 'text' | 'media' | 'shapes' | 'captions' | 'ai' | 'templates';
type ViewMode = 'edit' | 'preview';

export function CreationWorkspace({ state, platformConfig, onBack, onStateChange }: CreationWorkspaceProps) {
  const [activeTool, setActiveTool] = useState<ActiveTool>('select');
  const [viewMode, setViewMode] = useState<ViewMode>('edit');
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [showAiPanel, setShowAiPanel] = useState(false);
  const [aiFlowComplete, setAiFlowComplete] = useState(false);
  const nextId = useRef(1);

  const format = state.format!;
  const [showRepurpose, setShowRepurpose] = useState(false);

  const handleRepurpose = useCallback((newPlatformName: string, newFormatId: string) => {
    const newPlatform = platformConfigs[newPlatformName];
    if (!newPlatform) return;
    const newFormat = newPlatform.formats.find(f => f.id === newFormatId);
    if (!newFormat) return;

    const scaleX = newFormat.canvasW / format.canvasW;
    const scaleY = newFormat.canvasH / format.canvasH;

    const newElements = state.elements.map(el => ({
      ...el,
      x: el.x * scaleX,
      y: el.y * scaleY,
      w: el.w * scaleX,
      h: el.h * scaleY,
      fontSize: el.fontSize ? el.fontSize * scaleX : undefined,
    }));

    onStateChange({
      platform: newPlatformName,
      format: newFormat,
      elements: newElements
    });
    setShowRepurpose(false);
  }, [format, state.elements, onStateChange]);

  const handleAiFlowComplete = useCallback((result: AIResult) => {
    // Apply AI result to the canvas state
    const newElements: CanvasElement[] = result.elements.map((el, i) => ({
      ...el,
      id: `el-${nextId.current++}`,
      zIndex: i + 1,
    }));
    onStateChange({
      caption: result.caption,
      title: result.title,
      hashtags: result.hashtags,
      elements: newElements,
    });
    setAiFlowComplete(true);
  }, [onStateChange]);

  const handleAiFlowSkip = useCallback(() => {
    setAiFlowComplete(true);
  }, []);

  const addElement = useCallback((el: Omit<CanvasElement, 'id' | 'zIndex'>) => {
    const newEl: CanvasElement = {
      ...el,
      id: `el-${nextId.current++}`,
      zIndex: state.elements.length + 1,
    };
    onStateChange({ elements: [...state.elements, newEl] });
  }, [state.elements, onStateChange]);

  const updateElement = useCallback((id: string, updates: Partial<CanvasElement>) => {
    onStateChange({
      elements: state.elements.map(el => el.id === id ? { ...el, ...updates } : el)
    });
  }, [state.elements, onStateChange]);

  const deleteElement = useCallback((id: string) => {
    onStateChange({
      elements: state.elements.filter(el => el.id !== id),
      selectedElementId: state.selectedElementId === id ? null : state.selectedElementId,
    });
  }, [state.elements, state.selectedElementId, onStateChange]);

  const handleAddText = () => {
    addElement({
      type: 'text',
      x: 60,
      y: 60,
      w: 280,
      h: 60,
      content: 'Your text here',
      fontSize: 28,
      color: '#ffffff',
      fontWeight: '700',
      textAlign: 'left',
    });
    setActiveTool('select');
  };

  const handleAddShape = (shape: 'rect' | 'circle') => {
    addElement({
      type: 'shape',
      x: 80,
      y: 80,
      w: 120,
      h: 120,
      backgroundColor: platformConfig.accentColor + 'cc',
      borderRadius: shape === 'circle' ? 60 : 12,
    });
    setActiveTool('select');
  };

  const handleAiGenerate = async () => {
    if (!aiPrompt.trim()) return;
    setIsAiLoading(true);
    // Simulate AI — generate a caption and title
    await new Promise(res => setTimeout(res, 1800));
    const generatedCaption = `🚀 ${aiPrompt}\n\nThis is your AI-generated caption crafted for ${platformConfig.name}. Tailored to your audience and optimised for maximum engagement.\n\n${state.hashtags.length === 0 ? '#content #socialmedia #creatorstudio' : state.hashtags.join(' ')}`;
    onStateChange({ caption: generatedCaption });
    if (state.elements.length === 0) {
      addElement({ type: 'text', x: 40, y: 40, w: format.canvasW - 80, h: 80, content: aiPrompt, fontSize: 32, color: '#ffffff', fontWeight: '800', textAlign: 'center' });
    }
    setIsAiLoading(false);
    setShowAiPanel(false);
    setAiPrompt('');
  };

  const selectedElement = state.elements.find(el => el.id === state.selectedElementId) || null;

  return (
    <div className={styles.workspace}>
      {/* AI Creation Flow — shown on first entry until completed or skipped */}
      {!aiFlowComplete && (
        <AICreationFlow
          platformConfig={platformConfig}
          format={format}
          state={state}
          onComplete={handleAiFlowComplete}
          onSkip={handleAiFlowSkip}
          onBack={onBack}
        />
      )}

      {/* Top Bar */}
      <header className={styles.topBar}>
        <div className={styles.topBarLeft}>
          <button className={styles.backBtn} onClick={onBack}>
            <ArrowLeft size={16} />
            <span>Change Platform</span>
          </button>
          <div className={styles.divider} />
          <div className={styles.platformInfo} style={{ '--accent': platformConfig.accentColor } as any}>
            <span className={styles.platformInfoIcon}><img src={getPlatformLogoUrl(platformConfig.name)} alt={platformConfig.name} style={{ width: 24, height: 24, objectFit: 'contain' }} /></span>
            <span className={styles.platformInfoName}>{platformConfig.name}</span>
            <ChevronDown size={14} className={styles.chevron} />
            <span className={styles.formatBadge}>{format.icon} {format.label}</span>
            <span className={styles.ratioBadge}>{format.aspectRatio}</span>
          </div>
        </div>

        <div className={styles.topBarCenter}>
          <div className={styles.viewToggle}>
            <button className={`${styles.viewBtn} ${viewMode === 'edit' ? styles.viewBtnActive : ''}`} onClick={() => setViewMode('edit')}>Edit</button>
            <button className={`${styles.viewBtn} ${viewMode === 'preview' ? styles.viewBtnActive : ''}`} onClick={() => setViewMode('preview')}>
              <Eye size={14} />
              Preview
            </button>
          </div>
        </div>

        <div className={styles.topBarRight}>
          <div style={{ position: 'relative' }}>
            <button className={styles.repurposeBtn} onClick={() => setShowRepurpose(p => !p)}>
              <Wand2 size={15} />
              <span>Magic Repurpose</span>
            </button>
            {showRepurpose && (
              <div className={styles.repurposeDropdown}>
                <div className={styles.repurposeHeader}>Auto-resize for...</div>
                <div className={styles.repurposeList}>
                  {Object.values(platformConfigs).map(plat => (
                    <div key={plat.id} className={styles.repurposePlatformGroup}>
                      <div className={styles.repurposePlatformName}>
                        <img src={getPlatformLogoUrl(plat.name)} alt="" style={{ width: 14, height: 14, objectFit: 'contain' }} />
                        {plat.name}
                      </div>
                      <div className={styles.repurposeFormats}>
                        {plat.formats.map(f => (
                          <button key={f.id} className={styles.repurposeFormatBtn} onClick={() => handleRepurpose(plat.name, f.id)}>
                            <span>{f.icon}</span> {f.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <button className={`${styles.aiBtn} ${showAiPanel ? styles.aiBtnActive : ''}`} onClick={() => setShowAiPanel(p => !p)}>
            <Sparkles size={15} />
            AI Assist
          </button>
          <button className={styles.actionBtn}><Save size={15} /><span>Save</span></button>
          <button className={styles.publishBtn}><Share2 size={15} /><span>Publish</span></button>
        </div>
      </header>

      {/* AI Panel dropdown */}
      {showAiPanel && (
        <div className={styles.aiPanel}>
          <div className={styles.aiPanelInner}>
            <div className={styles.aiPanelHeader}>
              <Zap size={16} className={styles.aiPanelIcon} />
              <span>AI Content Generator</span>
              <span className={styles.aiPlatformTag}>{platformConfig.name} · {format.label}</span>
            </div>
            <div className={styles.aiInputRow}>
              <input
                className={styles.aiInput}
                placeholder={`What's this ${format.label.toLowerCase()} about? e.g. "Summer sale, 50% off all products"`}
                value={aiPrompt}
                onChange={e => setAiPrompt(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAiGenerate()}
              />
              <button className={styles.aiGenerateBtn} onClick={handleAiGenerate} disabled={isAiLoading || !aiPrompt.trim()}>
                {isAiLoading ? <span className={styles.spinner} /> : <Sparkles size={14} />}
                {isAiLoading ? 'Generating…' : 'Generate'}
              </button>
            </div>
            <div className={styles.aiSuggestions}>
              {['Write a hook', 'Add hashtags', 'Generate caption', 'Make it shorter', 'Make it punchier'].map(s => (
                <button key={s} className={styles.aiSuggestionPill} onClick={() => setAiPrompt(s)}>{s}</button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Layout */}
      <div className={styles.mainLayout}>
        {/* Left Tool Sidebar */}
        <ToolSidebar
          activeTool={activeTool}
          onSelectTool={setActiveTool}
          onAddText={handleAddText}
          onAddShape={handleAddShape}
          platformConfig={platformConfig}
          format={format}
        />

        {/* Canvas & Preview Area */}
        <div className={styles.centerArea}>
          {viewMode === 'edit' ? (
            <CanvasArea
              state={state}
              format={format}
              platformConfig={platformConfig}
              activeTool={activeTool}
              onSelectElement={(id) => onStateChange({ selectedElementId: id })}
              onUpdateElement={updateElement}
              onDeleteElement={deleteElement}
              onAddText={handleAddText}
            />
          ) : (
            <PlatformPreview
              state={state}
              platformConfig={platformConfig}
              format={format}
            />
          )}
        </div>

        {/* Right: Properties or Live Preview */}
        <div className={styles.rightColumn}>
          <PropertiesPanel
            selectedElement={selectedElement}
            state={state}
            platformConfig={platformConfig}
            format={format}
            onUpdateElement={updateElement}
            onDeleteElement={deleteElement}
            onStateChange={onStateChange}
          />
        </div>
      </div>
    </div>
  );
}
