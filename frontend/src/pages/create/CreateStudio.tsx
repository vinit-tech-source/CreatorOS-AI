import { useState, useCallback, useEffect } from 'react';
import { getPlatformConfig, ContentFormat } from '../../constants/platformConfigs';
import { PlatformSelector } from './components/PlatformSelector';
import { CreationWorkspace } from './components/CreationWorkspace';
import { useAuthStore } from '../../stores/authStore';

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
  const { user } = useAuthStore();
  const savedCountry = user?.country || localStorage.getItem('creatoros_default_country') || 'India';

  const [step, setStep] = useState<StudioStep>('select');
  const [state, setState] = useState<StudioState>({
    country: savedCountry,
    platform: 'Instagram',
    format: null,
    elements: [],
    caption: '',
    title: '',
    hashtags: [],
    selectedElementId: null,
  });

  useEffect(() => {
    if (savedCountry && state.country !== savedCountry) {
      setState(prev => ({ ...prev, country: savedCountry }));
    }
  }, [savedCountry]);

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
    <div style={{ position: 'fixed', inset: 0, overflow: 'hidden', background: 'var(--background, #07070c)' }}>
      <CreationWorkspace
        state={state}
        platformConfig={platformConfig!}
        onBack={handleBack}
        onStateChange={handleStateChange}
      />
    </div>
  );
}
