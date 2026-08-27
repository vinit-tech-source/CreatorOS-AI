import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { countryPlatforms } from '../../../constants/countryPlatforms';
import { platformConfigs, getPlatformConfig, ContentFormat, getPlatformLogoUrl } from '../../../constants/platformConfigs';
import { Globe, ChevronRight, Sparkles, Zap, Play, ArrowLeft } from 'lucide-react';
import styles from './PlatformSelector.module.css';

interface PlatformSelectorProps {
  initialCountry: string;
  initialPlatform: string;
  onEnterStudio: (country: string, platform: string, format: ContentFormat) => void;
}

const regions: Record<string, string[]> = {
  'South Asia': ['India', 'Pakistan', 'Bangladesh', 'Sri Lanka', 'Nepal'],
  'East Asia': ['China', 'Japan', 'South Korea', 'Taiwan', 'Mongolia'],
  'Southeast Asia': ['Indonesia', 'Philippines', 'Vietnam', 'Thailand', 'Malaysia', 'Singapore', 'Cambodia', 'Myanmar', 'Laos'],
  'North America': ['United States', 'Canada', 'Mexico'],
  'Latin America': ['Brazil', 'Colombia', 'Argentina', 'Chile', 'Peru', 'Ecuador', 'Uruguay', 'Dominican Republic', 'Panama', 'Costa Rica'],
  'Europe': ['Germany', 'United Kingdom', 'France', 'Spain', 'Italy', 'Netherlands', 'Poland', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Ireland', 'Portugal', 'Greece', 'Czechia', 'Romania', 'Hungary', 'Austria', 'Switzerland', 'Belgium', 'Serbia', 'Croatia', 'Slovenia', 'Bulgaria', 'Slovakia'],
  'Middle East': ['Saudi Arabia', 'UAE', 'Egypt', 'Israel', 'Turkey'],
  'Africa': ['Nigeria', 'South Africa', 'Kenya', 'Ghana', 'Morocco'],
  'Eastern Europe & CIS': ['Russia', 'Ukraine', 'Kazakhstan', 'Uzbekistan', 'Georgia', 'Armenia', 'Azerbaijan'],
  'Oceania': ['Australia', 'New Zealand'],
};

export function PlatformSelector({ initialCountry, initialPlatform, onEnterStudio }: PlatformSelectorProps) {
  const navigate = useNavigate();
  const [country, setCountry] = useState(initialCountry);
  const [platform, setPlatform] = useState(initialPlatform);
  const [selectedFormat, setSelectedFormat] = useState<ContentFormat | null>(null);
  const [activeRegion, setActiveRegion] = useState<string | null>(null);
  const [step, setStep] = useState<'country' | 'platform' | 'format'>('country');

  const countryData = countryPlatforms.find(c => c.country === country);
  const platformConfig = getPlatformConfig(platform);

  const handleSelectCountry = (c: string) => {
    setCountry(c);
    // Auto-select first available platform that has a config
    const cData = countryPlatforms.find(x => x.country === c);
    const firstSupportedPlatform = cData?.platforms.find(p => platformConfigs[p]);
    if (firstSupportedPlatform) setPlatform(firstSupportedPlatform);
    setSelectedFormat(null);
    setStep('platform');
  };

  const handleSelectPlatform = (p: string) => {
    if (!platformConfigs[p]) return; // Only allow configured platforms
    setPlatform(p);
    setSelectedFormat(null);
    setStep('format');
  };

  const handleSelectFormat = (f: ContentFormat) => {
    setSelectedFormat(f);
  };

  const handleEnter = () => {
    if (selectedFormat) {
      onEnterStudio(country, platform, selectedFormat);
    }
  };

  return (
    <div className={styles.container}>
      <button className={styles.exitBtn} onClick={() => navigate('/dashboard')}>
        <ArrowLeft size={16} />
        Back to Dashboard
      </button>

      {/* Animated background */}
      <div className={styles.bgGlow1} />
      <div className={styles.bgGlow2} />
      <div className={styles.bgGlow3} />

      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerBadge}>
          <Sparkles size={14} />
          <span>Content Creation Studio</span>
        </div>
        <h1 className={styles.headerTitle}>Where will you publish?</h1>
        <p className={styles.headerSub}>Choose your country, platform, and content format to enter the studio.</p>
      </div>

      {/* Breadcrumb */}
      <div className={styles.breadcrumb}>
        <button className={`${styles.crumb} ${step === 'country' ? styles.crumbActive : ''}`} onClick={() => setStep('country')}>
          <Globe size={14} /> Country
          {country && step !== 'country' && (
            <span className={styles.crumbValue}>
              {countryPlatforms.find(c => c.country === country)?.code ? (
                <img src={`https://flagcdn.com/w20/${countryPlatforms.find(c => c.country === country)?.code}.png`} className={styles.breadcrumbImg} alt=""/>
              ) : (
                countryPlatforms.find(c => c.country === country)?.flag
              )}
              {country}
            </span>
          )}
        </button>
        <ChevronRight size={14} className={styles.crumbArrow} />
        <button className={`${styles.crumb} ${step === 'platform' ? styles.crumbActive : ''} ${step === 'country' ? styles.crumbDisabled : ''}`} onClick={() => step !== 'country' && setStep('platform')}>
          <span>
             {platform ? <img src={getPlatformLogoUrl(platform)} className={styles.breadcrumbImg} alt=""/> : <Globe size={14} />}
          </span> Platform
          {platform && step === 'format' && <span className={styles.crumbValue}>{platform}</span>}
        </button>
        <ChevronRight size={14} className={styles.crumbArrow} />
        <button className={`${styles.crumb} ${step === 'format' ? styles.crumbActive : ''} ${step !== 'format' ? styles.crumbDisabled : ''}`} onClick={() => step === 'format' && setStep('format')}>
          <Zap size={14} /> Format
        </button>
      </div>

      {/* Step: Country */}
      {step === 'country' && (
        <div className={styles.stepPanel}>
          <div className={styles.regionGrid}>
            {Object.entries(regions).map(([region, countries]) => (
              <div key={region} className={styles.regionBlock}>
                <button
                  className={`${styles.regionHeader} ${activeRegion === region ? styles.regionHeaderActive : ''}`}
                  onClick={() => setActiveRegion(activeRegion === region ? null : region)}
                >
                  <span>{region}</span>
                  <span className={styles.regionCount}>{countries.length}</span>
                </button>
                {activeRegion === region && (
                  <div className={styles.countryList}>
                    {countries.map(c => {
                      const data = countryPlatforms.find(x => x.country === c);
                      return (
                        <button
                          key={c}
                          className={`${styles.countryItem} ${country === c ? styles.countryItemActive : ''}`}
                          onClick={() => handleSelectCountry(c)}
                        >
                          <span className={styles.countryFlag}>
                            {data?.code ? (
                              <img src={`https://flagcdn.com/w40/${data.code}.png`} alt={`${c} flag`} className={styles.listFlag} />
                            ) : (
                              data?.flag
                            )}
                          </span>
                          <span className={styles.countryName}>{c}</span>
                          <span className={styles.countryPlatformCount}>{data?.platforms.length || 0} platforms</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step: Platform */}
      {step === 'platform' && (
        <div className={styles.stepPanel}>
          <div className={styles.platformContext}>
            <span className={styles.contextFlag}>
              {countryData?.code ? (
                <img src={`https://flagcdn.com/w40/${countryData.code}.png`} alt={`${country} flag`} className={styles.contextFlagImg} />
              ) : (
                countryData?.flag
              )}
            </span>
            <span className={styles.contextCountry}>{country}</span>
            <span className={styles.contextSub}>Popular platforms in this region</span>
          </div>
          <div className={styles.platformGrid}>
            {countryData?.platforms.map(p => {
              const hasConfig = !!platformConfigs[p];
              const config = platformConfigs[p];
              return (
                <button
                  key={p}
                  className={`${styles.platformCard} ${platform === p ? styles.platformCardActive : ''} ${!hasConfig ? styles.platformCardDisabled : ''}`}
                  onClick={() => handleSelectPlatform(p)}
                  style={platform === p && config ? { borderColor: config.accentColor, boxShadow: `0 0 20px ${config.accentColor}40` } : {}}
                >
                  <div className={styles.platformIcon}>
                    <img src={getPlatformLogoUrl(p)} alt={p} className={styles.platformLogoImg} />
                  </div>
                  <div className={styles.platformName}>{p}</div>
                  {config && <div className={styles.platformFormatCount}>{config.formats.length} formats</div>}
                  {!hasConfig && <div className={styles.platformComingSoon}>Coming soon</div>}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Step: Format */}
      {step === 'format' && platformConfig && (
        <div className={styles.stepPanel}>
          <div className={styles.platformContext}>
            <div className={styles.platformBadge} style={{ background: platformConfig.gradient }}>
              <span className={styles.formatLogoWrap}><img src={getPlatformLogoUrl(platform)} alt={platform} className={styles.formatPlatformLogo} /></span>
              <span>{platformConfig.name}</span>
            </div>
            <span className={styles.contextSub}>Select a content format to enter the studio</span>
          </div>
          <div className={styles.formatGrid}>
            {platformConfig.formats.map(fmt => (
              <button
                key={fmt.id}
                className={`${styles.formatCard} ${selectedFormat?.id === fmt.id ? styles.formatCardActive : ''}`}
                onClick={() => handleSelectFormat(fmt)}
                style={selectedFormat?.id === fmt.id ? { borderColor: platformConfig.accentColor, boxShadow: `0 0 24px ${platformConfig.accentColor}50` } : {}}
              >
                <div className={styles.formatPreviewBox} style={{ aspectRatio: fmt.aspectRatio.replace(':', '/') }}>
                  <span className={styles.formatIcon}>{fmt.icon}</span>
                  <div className={styles.formatAspect}>{fmt.aspectRatio}</div>
                </div>
                <div className={styles.formatInfo}>
                  <div className={styles.formatLabel}>{fmt.label}</div>
                  <div className={styles.formatDesc}>{fmt.description}</div>
                  <div className={styles.formatMeta}>
                    {fmt.charLimit > 0 && <span>{fmt.charLimit.toLocaleString()} chars</span>}
                    {fmt.supportsCarousel && <span>Carousel</span>}
                    {fmt.supportsMedia && <span>Media</span>}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {selectedFormat && (
            <div className={styles.enterStudioBar}>
              <div className={styles.enterStudioInfo}>
                <span className={styles.enterStudioPlatform}>
                  <span className={styles.formatLogoWrap}><img src={getPlatformLogoUrl(platform)} alt={platform} className={styles.formatPlatformLogo} /></span> {platform}
                </span>
                <span className={styles.enterStudioSep}>→</span>
                <span className={styles.enterStudioFormat}>{selectedFormat.icon} {selectedFormat.label}</span>
                <span className={styles.enterStudioRatio}>{selectedFormat.aspectRatio}</span>
              </div>
              <button className={styles.enterStudioBtn} onClick={handleEnter}>
                <Play size={16} fill="currentColor" />
                Enter Studio
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
