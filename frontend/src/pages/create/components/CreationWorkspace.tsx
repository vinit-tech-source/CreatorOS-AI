import { useState, useRef, useCallback } from 'react';
import { StudioState, CanvasElement } from '../CreateStudio';
import { PlatformConfig, getPlatformLogoUrl, platformConfigs } from '../../../constants/platformConfigs';
import { CanvasArea } from './CanvasArea';
import { ToolSidebar } from './ToolSidebar';
import { PropertiesPanel } from './PropertiesPanel';
import { PlatformPreview } from './PlatformPreview';
import { AICreationFlow, AIResult } from './AICreationFlow';
import { MediaPickerModal } from './MediaPickerModal';
import { apiClient } from '../../../services/api/client';
import {
  ArrowLeft, Save, Share2, Eye, Zap, ChevronDown, Sparkles, Wand2, Loader2, Check
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
  const [showMediaPicker, setShowMediaPicker] = useState(false);
  const [aiFlowComplete, setAiFlowComplete] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);
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

  const handleAddMedia = () => {
    setShowMediaPicker(true);
  };

  const handleSelectImage = useCallback((imageUrl: string) => {
    const cardW = format.canvasW;
    const cardH = format.canvasH;
    const w = Math.min(260, Math.round(cardW * 0.55));
    const h = Math.round(w * 0.65);
    const x = Math.round((cardW - w) / 2);
    const y = Math.round((cardH - h) / 2);

    addElement({
      type: 'image',
      src: imageUrl,
      content: imageUrl,
      x,
      y,
      w,
      h,
      borderRadius: 12,
    });
    setActiveTool('select');
  }, [format, addElement]);

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

  const handleApplyTemplate = useCallback((templateId: string) => {
    const cardW = format.canvasW;
    const cardH = format.canvasH;
    const padding = 32;
    const contentW = cardW - (padding * 2);

    let newElements: CanvasElement[] = [];

    if (templateId === 'quote') {
      newElements = [
        {
          id: `el-${nextId.current++}`,
          zIndex: 1,
          type: 'text',
          x: padding,
          y: 24,
          w: contentW,
          h: 40,
          content: '“',
          fontSize: 48,
          color: platformConfig.accentColor,
          fontWeight: '900',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 2,
          type: 'text',
          x: padding,
          y: 72,
          w: contentW,
          h: 95,
          content: state.title || 'Consistency beats intensity every single time.',
          fontSize: 20,
          color: '#ffffff',
          fontWeight: '800',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 3,
          type: 'text',
          x: padding,
          y: cardH - 48,
          w: contentW,
          h: 24,
          content: '— @creator · CreatorOS',
          fontSize: 12,
          color: 'rgba(255,255,255,0.6)',
          fontWeight: '600',
          textAlign: 'center',
        },
      ];
    } else if (templateId === 'tips') {
      newElements = [
        {
          id: `el-${nextId.current++}`,
          zIndex: 1,
          type: 'text',
          x: padding,
          y: 22,
          w: contentW,
          h: 22,
          content: '💡 3 GOLDEN RULES',
          fontSize: 11,
          color: platformConfig.accentColor,
          fontWeight: '800',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 2,
          type: 'text',
          x: padding,
          y: 50,
          w: contentW,
          h: 40,
          content: state.title || 'How to win on ' + platformConfig.name,
          fontSize: 17,
          color: '#ffffff',
          fontWeight: '800',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 3,
          type: 'text',
          x: padding + 10,
          y: 98,
          w: contentW - 20,
          h: 75,
          content: '1. Hook with a bold claim\n2. Deliver 80% practical value\n3. End with a clear action',
          fontSize: 13,
          color: 'rgba(255,255,255,0.85)',
          fontWeight: '600',
          textAlign: 'left',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 4,
          type: 'shape',
          x: cardW / 2 - 65,
          y: cardH - 46,
          w: 130,
          h: 26,
          backgroundColor: platformConfig.accentColor,
          borderRadius: 13,
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 5,
          type: 'text',
          x: cardW / 2 - 65,
          y: cardH - 42,
          w: 130,
          h: 20,
          content: 'Save This Post 🔖',
          fontSize: 10,
          color: '#ffffff',
          fontWeight: '700',
          textAlign: 'center',
        },
      ];
    } else if (templateId === 'stat') {
      newElements = [
        {
          id: `el-${nextId.current++}`,
          zIndex: 1,
          type: 'text',
          x: padding,
          y: 24,
          w: contentW,
          h: 22,
          content: '📊 KEY METRIC',
          fontSize: 11,
          color: platformConfig.accentColor,
          fontWeight: '800',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 2,
          type: 'text',
          x: padding,
          y: 52,
          w: contentW,
          h: 58,
          content: '0 → 10,000',
          fontSize: 34,
          color: '#ffffff',
          fontWeight: '900',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 3,
          type: 'text',
          x: padding + 15,
          y: 120,
          w: contentW - 30,
          h: 50,
          content: state.title || 'The exact playbook to scale your audience from scratch.',
          fontSize: 13,
          color: 'rgba(255,255,255,0.7)',
          fontWeight: '500',
          textAlign: 'center',
        },
      ];
    } else {
      // minimal
      newElements = [
        {
          id: `el-${nextId.current++}`,
          zIndex: 1,
          type: 'text',
          x: padding,
          y: 32,
          w: contentW,
          h: 22,
          content: `${platformConfig.name.toUpperCase()} GUIDE`,
          fontSize: 11,
          color: platformConfig.accentColor,
          fontWeight: '800',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 2,
          type: 'text',
          x: padding,
          y: 64,
          w: contentW,
          h: 75,
          content: state.title || 'Start creating with intention',
          fontSize: 21,
          color: '#ffffff',
          fontWeight: '800',
          textAlign: 'center',
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 3,
          type: 'shape',
          x: cardW / 2 - 60,
          y: cardH - 50,
          w: 120,
          h: 28,
          backgroundColor: platformConfig.accentColor,
          borderRadius: 14,
        },
        {
          id: `el-${nextId.current++}`,
          zIndex: 4,
          type: 'text',
          x: cardW / 2 - 60,
          y: cardH - 46,
          w: 120,
          h: 20,
          content: 'Read Guide 👇',
          fontSize: 11,
          color: '#ffffff',
          fontWeight: '700',
          textAlign: 'center',
        },
      ];
    }

    onStateChange({ elements: newElements });
  }, [format, platformConfig, state.title, onStateChange]);

  const handleAiGenerate = async () => {
    if (!aiPrompt.trim()) return;
    setIsAiLoading(true);
    try {
      const response = await apiClient.post('/ai/generate-caption', {
        prompt: aiPrompt,
        platform: platformConfig.name,
      });

      const apiResult = response.data;
      
      const generatedCaption = apiResult.data.caption;
      onStateChange({ caption: generatedCaption });
      if (state.elements.length === 0) {
        addElement({ type: 'text', x: 40, y: 40, w: format.canvasW - 80, h: 80, content: aiPrompt, fontSize: 32, color: '#ffffff', fontWeight: '800', textAlign: 'center' });
      }
    } catch (error) {
      console.error('Failed to generate caption:', error);
      // Fallback
      const fallbackCaption = `🚀 ${aiPrompt}\n\nThis is your fallback caption crafted for ${platformConfig.name}.`;
      onStateChange({ caption: fallbackCaption });
    }
    setIsAiLoading(false);
    setShowAiPanel(false);
    setAiPrompt('');
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate save delay
    await new Promise(r => setTimeout(r, 1000));
    setIsSaving(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2000);
  };

  const handlePublish = async () => {
    setIsPublishing(true);
    setPublishSuccess(false);
    try {
      // Connect to the standalone publisher service on port 3000
      const res = await fetch('http://localhost:3000/posts/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connectedAccountId: 1, // Dev/Local testing account
          text: state.caption
        })
      });
      
      const data = await res.json();
      if (data.success) {
        setPublishSuccess(true);
        setTimeout(() => setPublishSuccess(false), 3000);
        alert('Published successfully! View it at: ' + data.tweetUrl);
      } else {
        alert('Failed to publish: ' + (data.error || 'Unknown error'));
      }
    } catch (err) {
      alert('Network error: Could not reach publisher service on port 3000');
    } finally {
      setIsPublishing(false);
    }
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
            <button className={`${styles.viewBtn} ${viewMode === 'edit' ? styles.viewBtnActive : ''}`} onClick={() => setViewMode('edit')}>
              <span>🎨 Visual Graphic</span>
            </button>
            <button className={`${styles.viewBtn} ${viewMode === 'preview' ? styles.viewBtnActive : ''}`} onClick={() => setViewMode('preview')}>
              <Eye size={13} />
              <span>📱 Live Feed Mockup</span>
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
                          <button key={f.id} className={styles.repurposeFormatBtn} onClick={() => {
                            handleRepurpose(plat.name, f.id);
                            setShowRepurpose(false);
                          }}>
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
          <button className={styles.actionBtn} onClick={handleSave} disabled={isSaving}>
            {isSaving ? <Loader2 size={15} className={styles.spinner} /> : saveSuccess ? <Check size={15} color="#10b981" /> : <Save size={15} />}
            <span>{isSaving ? 'Saving...' : saveSuccess ? 'Saved' : 'Save'}</span>
          </button>
          <button className={styles.publishBtn} onClick={handlePublish} disabled={isPublishing}>
            {isPublishing ? <Loader2 size={15} className={styles.spinner} /> : publishSuccess ? <Check size={15} /> : <Share2 size={15} />}
            <span>{isPublishing ? 'Publishing...' : publishSuccess ? 'Published!' : 'Publish'}</span>
          </button>
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
          onSelectTool={(tool) => {
            if (tool === 'ai') {
              setShowAiPanel(true);
            } else {
              setActiveTool(tool);
            }
          }}
          onAddText={handleAddText}
          onAddShape={handleAddShape}
          onAddMedia={handleAddMedia}
          onApplyTemplate={handleApplyTemplate}
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

      {/* Media Picker Modal */}
      <MediaPickerModal
        isOpen={showMediaPicker}
        onClose={() => setShowMediaPicker(false)}
        onSelectImage={handleSelectImage}
      />
    </div>
  );
}
