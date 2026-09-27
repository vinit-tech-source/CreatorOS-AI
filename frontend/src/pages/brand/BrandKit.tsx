import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { 
  Save, 
  AlertCircle, 
  RefreshCw, 
  Sparkles, 
  Palette, 
  Type, 
  MessageSquare, 
  Target, 
  ExternalLink,
  Copy,
  Check,
  Share2,
  Heart,
  MessageCircle
} from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { useBrandKitStore } from '../../stores/brandKitStore';
import styles from './BrandKit.module.css';

interface PresetPalette {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
}

const PALETTE_PRESETS: PresetPalette[] = [
  { name: 'Obsidian Indigo', primary: '#6366F1', secondary: 'var(--panel-2)', accent: '#EC4899' },
  { name: 'Emerald Growth', primary: 'var(--panel-2)', secondary: 'var(--panel-2)', accent: '#34D399' },
  { name: 'Cyber Neon', primary: 'var(--panel-2)', secondary: 'var(--panel-2)', accent: '#8B5CF6' },
  { name: 'Sunset Creator', primary: '#F97316', secondary: '#451A03', accent: '#F59E0B' },
  { name: 'Monochrome Luxe', primary: '#F8FAFC', secondary: 'var(--panel-2)', accent: '#64748B' },
];

const TONE_PRESETS = [
  'Visionary & Bold',
  'Authority & Educational',
  'Conversational & Witty',
  'Minimal & Precise',
  'Empathetic & Warm',
  'High Energy & Viral',
];

const AUDIENCE_PRESETS = [
  'Tech Founders',
  'Content Creators',
  'Software Engineers',
  'B2B Executives',
  'Growth Marketers',
  'Gen-Z Creators',
];

const VALUE_PRESETS = [
  'Relentless Innovation',
  'Extreme Clarity',
  'Radical Transparency',
  'High Aesthetic Bar',
  'Authenticity First',
];

const FONT_OPTIONS = [
  'Inter',
  'Plus Jakarta Sans',
  'Outfit',
  'Poppins',
  'Space Grotesk',
  'Playfair Display',
  'Fira Code',
];

export function BrandKit() {
  const { activeWorkspace } = useWorkspaceStore();
  const { brandKit, isLoading, isSaving, error, fetchBrandKit, saveBrandKit } = useBrandKitStore();

  const [formData, setFormData] = useState({
    brand_name: 'CreatorOS Official',
    description: 'Empowering digital creators with autonomous multi-channel distribution.',
    website_url: 'https://creatoros.ai',
    logo_url: '',
    primary_color: '#6366F1',
    secondary_color: 'var(--panel-2)',
    accent_color: '#EC4899',
    font_family: 'Inter',
    default_tone: 'Visionary & Bold',
    target_audience: 'Tech founders, growth marketers, and elite content creators',
    brand_values: 'Relentless Innovation, Extreme Clarity, High Aesthetic Bar',
    preferred_language: 'en',
  });

  const [copiedTokens, setCopiedTokens] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState(false);

  useEffect(() => {
    if (activeWorkspace) {
      fetchBrandKit(activeWorkspace.id);
    }
  }, [activeWorkspace, fetchBrandKit]);

  useEffect(() => {
    if (brandKit) {
      setFormData({
        brand_name: brandKit.brand_name || brandKit.name || 'CreatorOS Official',
        description: brandKit.description || '',
        website_url: brandKit.website_url || '',
        logo_url: brandKit.logo_url || '',
        primary_color: brandKit.primary_color || '#6366F1',
        secondary_color: brandKit.secondary_color || 'var(--panel-2)',
        accent_color: brandKit.accent_color || '#EC4899',
        font_family: brandKit.font_family || 'Inter',
        default_tone: brandKit.default_tone || brandKit.voice_tone || 'Visionary & Bold',
        target_audience: brandKit.target_audience || '',
        brand_values: brandKit.brand_values || '',
        preferred_language: brandKit.preferred_language || 'en',
      });
    }
  }, [brandKit]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleColorChange = (field: 'primary_color' | 'secondary_color' | 'accent_color', value: string) => {
    setFormData(prev => ({ ...prev, [field]: value.toUpperCase() }));
  };

  const applyPalettePreset = (p: PresetPalette) => {
    setFormData(prev => ({
      ...prev,
      primary_color: p.primary,
      secondary_color: p.secondary,
      accent_color: p.accent,
    }));
  };

  const handleToneToggle = (tone: string) => {
    setFormData(prev => ({
      ...prev,
      default_tone: prev.default_tone ? `${prev.default_tone}, ${tone}` : tone,
    }));
  };

  const handleAudienceAdd = (aud: string) => {
    if (formData.target_audience.includes(aud)) return;
    setFormData(prev => ({
      ...prev,
      target_audience: prev.target_audience ? `${prev.target_audience}, ${aud}` : aud,
    }));
  };

  const handleValueAdd = (val: string) => {
    if (formData.brand_values.includes(val)) return;
    setFormData(prev => ({
      ...prev,
      brand_values: prev.brand_values ? `${prev.brand_values}, ${val}` : val,
    }));
  };

  const handleCopyTokens = () => {
    const cssString = `:root {
  --brand-primary: ${formData.primary_color};
  --brand-secondary: ${formData.secondary_color};
  --brand-accent: ${formData.accent_color};
  --brand-font: '${formData.font_family}', sans-serif;
}`;
    navigator.clipboard.writeText(cssString);
    setCopiedTokens(true);
    setTimeout(() => setCopiedTokens(false), 2000);
  };

  const handleSave = async () => {
    if (!activeWorkspace) return;
    setSaveSuccessMsg(false);
    try {
      await saveBrandKit(activeWorkspace.id, formData);
      setSaveSuccessMsg(true);
      setTimeout(() => setSaveSuccessMsg(false), 3000);
    } catch (err) {
      // Error handled in store
    }
  };

  if (!activeWorkspace) {
    return (
      <div className={styles.container}>
        <PageHeader title="Brand Kit" subtitle="Manage your brand voice, tone, and visual design system." />
        <div className={styles.sectionCard}>
          <div className={styles.errorState}>
            <AlertCircle size={36} className="mb-3 text-rose-400" />
            <h3 className="font-semibold text-lg text-white">No workspace selected</h3>
            <p className="mt-2 text-slate-400">Please select an active workspace from the sidebar to configure its Brand Kit.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <PageHeader 
        title="Brand Kit & Design System" 
        subtitle="Define colors, typography, logos, and AI persona guidelines to keep all multi-platform content 100% on-brand."
        action={
          <Button onClick={handleSave} disabled={isLoading || isSaving} isLoading={isSaving}>
            <Save size={15} /> Save Brand Kit
          </Button>
        }
      />

      {saveSuccessMsg && (
        <div className={styles.alertSuccess}>
          <Check size={16} />
          <span>Brand Kit saved successfully! Autonomous agents and Studio will now use these brand tokens.</span>
        </div>
      )}

      {error && (
        <div className={styles.alertError}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className={styles.sectionCard}>
          <div className={styles.loadingState}>
            <RefreshCw size={32} className={styles.spinner} />
            <p className="mt-3 text-slate-300">Loading Brand Kit configuration...</p>
          </div>
        </div>
      ) : (
        <div className={styles.brandKitGrid}>
          {/* Left Column: Configuration Cards */}
          <div className={styles.configColumn}>
            {/* Card 1: Brand Identity */}
            <div className={styles.sectionCard}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionTitleGroup}>
                  <div className={styles.sectionIconWrapper}>
                    <Sparkles size={16} />
                  </div>
                  <div>
                    <h3 className={styles.sectionTitle}>Brand Identity</h3>
                    <p className={styles.sectionSubtitle}>Core brand name, messaging, and logo asset</p>
                  </div>
                </div>
              </div>

              <div className={styles.fieldRow}>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>
                    Brand Name <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    name="brand_name"
                    className={styles.textInput}
                    value={formData.brand_name}
                    onChange={handleChange}
                    placeholder="e.g. Acme Studio"
                  />
                </div>

                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>
                    Official Website URL
                    {formData.website_url && (
                      <a 
                        href={formData.website_url.startsWith('http') ? formData.website_url : `https://${formData.website_url}`} 
                        target="_blank" 
                        rel="noreferrer"
                        className="text-indigo-400 hover:underline flex items-center gap-1 font-normal text-xs"
                      >
                        Visit <ExternalLink size={10} />
                      </a>
                    )}
                  </label>
                  <input
                    type="text"
                    name="website_url"
                    className={styles.textInput}
                    value={formData.website_url}
                    onChange={handleChange}
                    placeholder="https://yourbrand.com"
                  />
                </div>
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Brand Tagline / Pitch</label>
                <input
                  type="text"
                  name="description"
                  className={styles.textInput}
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="e.g. Next-generation workflows for modern creators."
                />
              </div>

              {/* Logo Manager */}
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Brand Logo</label>
                <div className={styles.logoManagerRow}>
                  <div 
                    className={styles.logoPreviewBox}
                    style={{ background: formData.secondary_color || 'var(--panel-2)' }}
                  >
                    {formData.logo_url ? (
                      <img src={formData.logo_url} alt="Logo" className={styles.logoImg} />
                    ) : (
                      <span 
                        className={styles.logoMonogram}
                        style={{ color: formData.primary_color || '#ffffff' }}
                      >
                        {formData.brand_name.charAt(0).toUpperCase()}
                      </span>
                    )}
                  </div>

                  <div className={styles.logoInputWrapper}>
                    <input
                      type="url"
                      name="logo_url"
                      className={styles.textInput}
                      value={formData.logo_url}
                      onChange={handleChange}
                      placeholder="Paste image URL (PNG, SVG, JPG)..."
                    />
                    <span className={styles.fieldHint}>
                      Enter a transparent PNG or vector SVG link for clean rendering across all social headers.
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 2: Palette Studio */}
            <div className={styles.sectionCard}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionTitleGroup}>
                  <div className={styles.sectionIconWrapper} style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' }}>
                    <Palette size={16} />
                  </div>
                  <div>
                    <h3 className={styles.sectionTitle}>Color Palette Studio</h3>
                    <p className={styles.sectionSubtitle}>Primary, secondary, and accent colors for graphics and posts</p>
                  </div>
                </div>
              </div>

              {/* Curated Presets Ribbon */}
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Curated Palette Presets</label>
                <div className={styles.presetPalettesStrip}>
                  {PALETTE_PRESETS.map(p => (
                    <button
                      type="button"
                      key={p.name}
                      className={styles.presetPaletteBtn}
                      onClick={() => applyPalettePreset(p)}
                      title={`Apply ${p.name}`}
                    >
                      <div className={styles.presetColorDots}>
                        <span className={styles.presetDot} style={{ background: p.primary }} />
                        <span className={styles.presetDot} style={{ background: p.secondary }} />
                        <span className={styles.presetDot} style={{ background: p.accent }} />
                      </div>
                      <span className={styles.presetName}>{p.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* 3 Color Pickers */}
              <div className={styles.colorPickersGrid}>
                {/* Primary */}
                <div className={styles.colorPickerCard}>
                  <div className={styles.colorPickerTop}>
                    <span className={styles.colorRoleLabel}>Primary Brand</span>
                    <span className={styles.fieldHint}>Main buttons & heroes</span>
                  </div>
                  <div className={styles.colorInputRow}>
                    <input
                      type="color"
                      className={styles.nativeColorInput}
                      value={formData.primary_color}
                      onChange={(e) => handleColorChange('primary_color', e.target.value)}
                    />
                    <input
                      type="text"
                      className={styles.hexCodeInput}
                      value={formData.primary_color}
                      onChange={(e) => handleColorChange('primary_color', e.target.value)}
                      maxLength={7}
                    />
                  </div>
                  <p className={styles.colorDescText}>Dominant brand color used for action states.</p>
                </div>

                {/* Secondary */}
                <div className={styles.colorPickerCard}>
                  <div className={styles.colorPickerTop}>
                    <span className={styles.colorRoleLabel}>Secondary</span>
                    <span className={styles.fieldHint}>Card backgrounds</span>
                  </div>
                  <div className={styles.colorInputRow}>
                    <input
                      type="color"
                      className={styles.nativeColorInput}
                      value={formData.secondary_color}
                      onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                    />
                    <input
                      type="text"
                      className={styles.hexCodeInput}
                      value={formData.secondary_color}
                      onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                      maxLength={7}
                    />
                  </div>
                  <p className={styles.colorDescText}>Supporting dark tone for backgrounds & borders.</p>
                </div>

                {/* Accent */}
                <div className={styles.colorPickerCard}>
                  <div className={styles.colorPickerTop}>
                    <span className={styles.colorRoleLabel}>Accent Highlight</span>
                    <span className={styles.fieldHint}>Badges & tags</span>
                  </div>
                  <div className={styles.colorInputRow}>
                    <input
                      type="color"
                      className={styles.nativeColorInput}
                      value={formData.accent_color}
                      onChange={(e) => handleColorChange('accent_color', e.target.value)}
                    />
                    <input
                      type="text"
                      className={styles.hexCodeInput}
                      value={formData.accent_color}
                      onChange={(e) => handleColorChange('accent_color', e.target.value)}
                      maxLength={7}
                    />
                  </div>
                  <p className={styles.colorDescText}>High-contrast neon/bright tone for callouts.</p>
                </div>
              </div>
            </div>

            {/* Card 3: Typography */}
            <div className={styles.sectionCard}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionTitleGroup}>
                  <div className={styles.sectionIconWrapper} style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                    <Type size={16} />
                  </div>
                  <div>
                    <h3 className={styles.sectionTitle}>Typography & Fonts</h3>
                    <p className={styles.sectionSubtitle}>Primary brand font family for graphics and canvas rendering</p>
                  </div>
                </div>
              </div>

              <div className={styles.fieldRow}>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Primary Font Family</label>
                  <select
                    name="font_family"
                    className={styles.selectInput}
                    value={formData.font_family}
                    onChange={handleChange}
                  >
                    {FONT_OPTIONS.map(font => (
                      <option key={font} value={font}>{font}</option>
                    ))}
                  </select>
                </div>

                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Preferred Content Language</label>
                  <select
                    name="preferred_language"
                    className={styles.selectInput}
                    value={formData.preferred_language}
                    onChange={handleChange}
                  >
                    <option value="en">English (US / Global)</option>
                    <option value="en-gb">English (UK)</option>
                    <option value="es">Spanish (Español)</option>
                    <option value="fr">French (Français)</option>
                    <option value="de">German (Deutsch)</option>
                    <option value="hi">Hindi (हिंदी)</option>
                    <option value="ja">Japanese (日本語)</option>
                  </select>
                </div>
              </div>

              <div 
                className="p-3.5 rounded-lg border border-white/10 bg-black/40 mt-1"
                style={{ fontFamily: formData.font_family }}
              >
                <p className="text-xs text-slate-400 mb-1">Live Typography Specimen:</p>
                <h4 className="text-lg font-bold text-white">
                  The quick brown fox jumps over the lazy dog. 0123456789
                </h4>
                <p className="text-sm text-slate-300 mt-1">
                  Empowering digital creators with autonomous multi-channel distribution.
                </p>
              </div>
            </div>

            {/* Card 4: AI Voice & Tone */}
            <div className={styles.sectionCard}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionTitleGroup}>
                  <div className={styles.sectionIconWrapper} style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
                    <MessageSquare size={16} />
                  </div>
                  <div>
                    <h3 className={styles.sectionTitle}>AI Voice & Persona Guidelines</h3>
                    <p className={styles.sectionSubtitle}>Instruct autonomous agents how to sound across all channels</p>
                  </div>
                </div>
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Tone Preset Pills (Click to append)</label>
                <div className={styles.chipsWrapRow}>
                  {TONE_PRESETS.map(tone => {
                    const isSelected = formData.default_tone.includes(tone);
                    return (
                      <button
                        type="button"
                        key={tone}
                        className={`${styles.presetChip} ${isSelected ? styles.presetChipActive : ''}`}
                        onClick={() => handleToneToggle(tone)}
                      >
                        {isSelected && <Check size={11} />}
                        <span>{tone}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Brand Voice Instructions for AI</label>
                <textarea
                  name="default_tone"
                  className={styles.textareaInput}
                  rows={3}
                  value={formData.default_tone}
                  onChange={handleChange}
                  placeholder="Describe your tone. E.g. 'Punchy, visionary, and data-backed. Never use passive voice, fluff, or generic motivational quotes.'"
                />
              </div>
            </div>

            {/* Card 5: Target Audience & Values */}
            <div className={styles.sectionCard}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionTitleGroup}>
                  <div className={styles.sectionIconWrapper} style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
                    <Target size={16} />
                  </div>
                  <div>
                    <h3 className={styles.sectionTitle}>Audience & Core Values</h3>
                    <p className={styles.sectionSubtitle}>Context injected into AI content generators for relevance</p>
                  </div>
                </div>
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Target Audience Presets</label>
                <div className={styles.chipsWrapRow}>
                  {AUDIENCE_PRESETS.map(aud => (
                    <button
                      type="button"
                      key={aud}
                      className={styles.presetChip}
                      onClick={() => handleAudienceAdd(aud)}
                    >
                      <span>+ {aud}</span>
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  name="target_audience"
                  className={styles.textInput}
                  value={formData.target_audience}
                  onChange={handleChange}
                  placeholder="e.g. Founders, technical operators, and creative directors."
                />
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Core Brand Values</label>
                <div className={styles.chipsWrapRow}>
                  {VALUE_PRESETS.map(val => (
                    <button
                      type="button"
                      key={val}
                      className={styles.presetChip}
                      onClick={() => handleValueAdd(val)}
                    >
                      <span>+ {val}</span>
                    </button>
                  ))}
                </div>
                <input
                  type="text"
                  name="brand_values"
                  className={styles.textInput}
                  value={formData.brand_values}
                  onChange={handleChange}
                  placeholder="e.g. Radical transparency, high aesthetic bar, speed of execution."
                />
              </div>
            </div>
          </div>

          {/* Right Column: Sticky Live Showcase Card */}
          <div className={styles.showcaseColumn}>
            <div className={styles.showcaseCard}>
              <div className={styles.showcaseBadgeHeader}>
                <div className={styles.liveBadge}>
                  <span className={styles.liveBadgePulse} />
                  Live Brand Preview
                </div>
                <span className="text-xs text-slate-400">Real-time simulation</span>
              </div>

              {/* Brand Hero Banner */}
              <div 
                className={styles.brandHeroBanner}
                style={{
                  background: `linear-gradient(135deg, ${formData.secondary_color} 0%, ${formData.primary_color} 100%)`,
                }}
              >
                <div className={styles.brandHeroLogo}>
                  {formData.logo_url ? (
                    <img src={formData.logo_url} alt="Brand Logo" />
                  ) : (
                    <span>{formData.brand_name.charAt(0).toUpperCase()}</span>
                  )}
                </div>
                <div className={styles.brandHeroInfo}>
                  <h4 className={styles.brandHeroName} style={{ fontFamily: formData.font_family }}>
                    {formData.brand_name}
                  </h4>
                  <p className={styles.brandHeroTagline}>
                    {formData.description || 'Brand identity in action'}
                  </p>
                </div>
              </div>

              {/* Live Social Post Simulation */}
              <div className={styles.mockSocialCard}>
                <div className={styles.mockPostAuthorRow}>
                  <div 
                    className={styles.mockAuthorAvatar}
                    style={{ background: formData.primary_color }}
                  >
                    {formData.logo_url ? (
                      <img src={formData.logo_url} alt="Logo" />
                    ) : (
                      formData.brand_name.charAt(0).toUpperCase()
                    )}
                  </div>
                  <div className={styles.mockAuthorMeta}>
                    <span className={styles.mockAuthorName}>{formData.brand_name}</span>
                    <span className={styles.mockAuthorTime}>Sponsored • Just now</span>
                  </div>
                </div>

                <p 
                  className={styles.mockCaption}
                  style={{ fontFamily: formData.font_family }}
                >
                  🚀 Here is how <strong>{formData.brand_name}</strong> delivers high-converting content with zero manual friction.
                  <br /><br />
                  Tone: <em>{formData.default_tone || 'Professional & Engaging'}</em>
                </p>

                <div className={styles.mockPostActions}>
                  <span className={styles.mockActionItem} style={{ color: formData.accent_color }}>
                    <Heart size={14} fill={formData.accent_color} /> 1.4k
                  </span>
                  <span className={styles.mockActionItem}>
                    <MessageCircle size={14} /> 128
                  </span>
                  <span className={styles.mockActionItem}>
                    <Share2 size={14} /> Share
                  </span>
                </div>
              </div>

              {/* UI Sampler (Buttons & Badges with Brand Tokens) */}
              <div className={styles.uiSamplerSection}>
                <h5 className={styles.samplerTitle}>Design System Tokens</h5>
                <div className={styles.samplerRow}>
                  <button 
                    type="button" 
                    className={styles.samplePrimaryBtn}
                    style={{
                      background: formData.primary_color,
                      color: '#ffffff',
                      fontFamily: formData.font_family,
                    }}
                  >
                    Primary Action
                  </button>

                  <button 
                    type="button" 
                    className={styles.sampleSecondaryBtn}
                    style={{
                      background: formData.secondary_color,
                      color: '#ffffff',
                      border: `1px solid ${formData.primary_color}40`,
                      fontFamily: formData.font_family,
                    }}
                  >
                    Secondary
                  </button>

                  <span 
                    className={styles.sampleAccentBadge}
                    style={{
                      background: `${formData.accent_color}25`,
                      color: formData.accent_color,
                      border: `1px solid ${formData.accent_color}50`,
                      fontFamily: formData.font_family,
                    }}
                  >
                    Accent Tag
                  </span>
                </div>
              </div>

              {/* CSS Variables Export */}
              <div className={styles.tokensBox}>
                <span className={styles.tokensSnippet}>
                  --brand-primary: {formData.primary_color};
                </span>
                <button
                  type="button"
                  className={styles.copyTokensBtn}
                  onClick={handleCopyTokens}
                >
                  {copiedTokens ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                  <span>{copiedTokens ? 'Copied!' : 'Copy CSS'}</span>
                </button>
              </div>

              {/* Floating Save Button inside showcase */}
              <Button 
                onClick={handleSave} 
                disabled={isLoading || isSaving} 
                isLoading={isSaving}
                className="w-full mt-1"
              >
                <Save size={15} /> Save All Changes
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
