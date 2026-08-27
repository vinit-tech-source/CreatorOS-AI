import { useState, useCallback } from 'react';
import { getPlatformConfig, ContentFormat } from '../../constants/platformConfigs';
import { PlatformSelector } from './components/PlatformSelector';
import { CreationWorkspace } from './components/CreationWorkspace';

export type StudioStep = 'select' | 'create';

export interface CanvasElement {
  id: string;
  type: 'text' | 'image' | 'shape' | 'sticker';
  x: number;
  y: number;
  w: number;
  h: number;
  content?: string;
  src?: string;
  fontSize?: number;
  color?: string;
  fontWeight?: string;
  textAlign?: 'left' | 'center' | 'right';
  backgroundColor?: string;
  borderRadius?: number;
  zIndex: number;
}

export interface StudioState {
  country: string;
  platform: string;
  format: ContentFormat | null;
  elements: CanvasElement[];
  caption: string;
  title: string;
  hashtags: string[];
  selectedElementId: string | null;
}

export function CreateStudio() {
  const [step, setStep] = useState<StudioStep>('select');
  const [state, setState] = useState<StudioState>({
    country: 'India',
    platform: 'Instagram',
    format: null,
    elements: [],
    caption: '',
    title: '',
    hashtags: [],
    selectedElementId: null,
  });

  const platformConfig = getPlatformConfig(state.platform);

  const handleEnterStudio = useCallback((country: string, platform: string, format: ContentFormat) => {
    setState(prev => ({
      ...prev,
      country,
      platform,
      format,
      elements: [],
      caption: '',
      title: '',
      hashtags: [],
      selectedElementId: null,
    }));
    setStep('create');
  }, []);

  const handleBack = useCallback(() => {
    setStep('select');
  }, []);

  const handleStateChange = useCallback((updates: Partial<StudioState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  if (step === 'select') {
    return (
      <PlatformSelector
        initialCountry={state.country}
        initialPlatform={state.platform}
        onEnterStudio={handleEnterStudio}
      />
    );
  }

  return (
    <div className="studioFullBleed" style={{ height: '100%', overflow: 'hidden' }}>
      <CreationWorkspace
        state={state}
        platformConfig={platformConfig!}
        onBack={handleBack}
        onStateChange={handleStateChange}
      />
    </div>
  );
}
