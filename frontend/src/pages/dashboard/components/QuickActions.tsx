import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Bot, ArrowRight, Zap } from 'lucide-react';
import { RealBrandLogo } from '../../../components/common/BrandLogos';
import styles from './QuickActions.module.css';

const PLATFORMS = ['INSTAGRAM', 'LINKEDIN', 'YOUTUBE', 'X', 'TIKTOK'];

const FORMATS = [
  { id: 'POST', label: 'Punchy Post' },
  { id: 'CAROUSEL', label: 'Carousel' },
  { id: 'VIDEO_SCRIPT', label: 'Video Script' },
  { id: 'THREAD', label: 'Viral Thread' },
];

const SUGGESTIONS = [
  "5 contrarian takes on AI agents for LinkedIn",
  "Why consistency beats virality in 2026",
  "60-second retention hook script for Shorts",
  "Visual carousel: The modern creator tech stack",
];

export function QuickActions() {
  const [query, setQuery] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('LINKEDIN');
  const [selectedFormat, setSelectedFormat] = useState('POST');
  const navigate = useNavigate();

  const handleLaunchStudio = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.append('q', query.trim());
    if (selectedPlatform) params.append('platform', selectedPlatform);
    if (selectedFormat) params.append('format', selectedFormat);
    navigate(`/create?${params.toString()}`);
  };

  const handleLaunchPipeline = () => {
    navigate(`/automation/pipeline`);
  };

  return (
    <div className={styles.canvasCard}>
      {/* Header */}
      <div className={styles.canvasHeader}>
        <div className={styles.headerTitleWrap}>
          <div className={styles.canvasIconWrap}>
            <Sparkles size={18} />
          </div>
          <div>
            <h2 className={styles.canvasTitle}>AI Idea Canvas</h2>
            <p className={styles.canvasSubtitle}>Turn any concept into multi-platform tailored copy and visual briefs</p>
          </div>
        </div>

        {/* Format Selectors */}
        <div className={styles.formatSelectorRow}>
          {FORMATS.map(f => (
            <button
              type="button"
              key={f.id}
              className={`${styles.formatPill} ${selectedFormat === f.id ? styles.formatPillActive : ''}`}
              onClick={() => setSelectedFormat(f.id)}
            >
              <span>{f.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className={styles.promptInputRow}>
        <textarea
          className={styles.textarea}
          rows={2}
          placeholder={`Describe your hook or idea for ${selectedPlatform}...`}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              handleLaunchStudio();
            }
          }}
        />
      </div>

      {/* Controls & Triggers */}
      <div className={styles.canvasFooterRow}>
        {/* Platform Selection */}
        <div className={styles.platformsCluster}>
          {PLATFORMS.map(p => (
            <button
              type="button"
              key={p}
              className={`${styles.platformPillBtn} ${selectedPlatform === p ? styles.platformPillActive : ''}`}
              onClick={() => setSelectedPlatform(p)}
            >
              <RealBrandLogo platform={p} size={14} />
              <span>{p.charAt(0) + p.slice(1).toLowerCase()}</span>
            </button>
          ))}
        </div>

        {/* Action Triggers */}
        <div className={styles.actionButtonsGroup}>
          <button
            type="button"
            className={styles.pipelineLaunchBtn}
            onClick={handleLaunchPipeline}
            title="Execute 10-agent autonomous LangGraph workflow"
          >
            <Bot size={14} className="text-indigo-400" />
            <span>10-Agent Pipeline</span>
          </button>

          <button
            type="button"
            className={styles.studioCreateBtn}
            onClick={() => handleLaunchStudio()}
          >
            <Zap size={14} />
            <span>Draft in Studio</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* Trending Suggestions */}
      <div className={styles.suggestionsBar}>
        <span className={styles.suggestionLabel}>
          <Sparkles size={11} className="text-indigo-400" /> Trending Ideas:
        </span>
        {SUGGESTIONS.map((s, i) => (
          <button
            key={i}
            type="button"
            className={styles.suggestionPill}
            onClick={() => setQuery(s)}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
