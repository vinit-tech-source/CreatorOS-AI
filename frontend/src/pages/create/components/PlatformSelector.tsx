import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { countryPlatforms, regions, getRegionForCountry } from '../../../constants/countryPlatforms';
import { platformConfigs, getPlatformConfig, ContentFormat, getPlatformLogoUrl } from '../../../constants/platformConfigs';
import { Globe, ChevronRight, Sparkles, Zap, ArrowLeft, Settings } from 'lucide-react';
import { useAuthStore } from '../../../stores/authStore';
import { userService } from '../../../services/api/userService';
import styles from './PlatformSelector.module.css';

interface PlatformSelectorProps {
  initialCountry: string;
  initialPlatform: string;
  onEnterStudio: (country: string, platform: string, format: ContentFormat) => void;
}

export function PlatformSelector({ initialCountry, initialPlatform, onEnterStudio }: PlatformSelectorProps) {
  const navigate = useNavigate();
  const { user, updateUser } = useAuthStore();

  const savedCountry = user?.country || localStorage.getItem('creatoros_default_country');
  const effectiveCountry = initialCountry || savedCountry || 'India';
  const hasSavedPreference = Boolean(user?.country || localStorage.getItem('creatoros_default_country'));

  const [country, setCountry] = useState(effectiveCountry);
  const [platform, setPlatform] = useState(initialPlatform);
  const [selectedFormat, setSelectedFormat] = useState<ContentFormat | null>(null);
  const [activeRegion, setActiveRegion] = useState<string | null>(getRegionForCountry(effectiveCountry) || 'South Asia');
  
  // If user already has a saved country preference, start on 'platform' step. Otherwise 'country'.
  const [step, setStep] = useState<'country' | 'platform' | 'format'>(
    hasSavedPreference ? 'platform' : 'country'
  );

  useEffect(() => {
    if (savedCountry && savedCountry !== country) {
      setCountry(savedCountry);
      const cData = countryPlatforms.find(x => x.country === savedCountry);
      const firstSupportedPlatform = cData?.platforms.find(p => platformConfigs[p]);
      if (firstSupportedPlatform) setPlatform(firstSupportedPlatform);
    }
  }, [savedCountry]);

  const countryData = countryPlatforms.find(c => c.country === country);
  const platformConfig = getPlatformConfig(platform);

  const handleSelectCountry = async (c: string) => {
    setCountry(c);
    const reg = getRegionForCountry(c) || 'Global';
    
    // Save to localStorage
    localStorage.setItem('creatoros_default_country', c);
    localStorage.setItem('creatoros_default_region', reg);
    
    // Update auth store
    updateUser({ region: reg, country: c });

    // Persist to backend user profile
    try {
      await userService.updateCurrentUser({ region: reg, country: c });
    } catch (e) {
      console.warn('Failed to persist country preference to backend profile', e);
    }

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
    onEnterStudio(country, platform, f);
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

      <div className={styles.inner}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerBadge}>
            <Sparkles size={13} />
            <span>Content Creation Studio</span>
          </div>
          <h1 className={styles.headerTitle}>Where will you publish?</h1>
          <p className={styles.headerSub}>
            {hasSavedPreference ? (
              <span>Publishing for target market <strong>{country}</strong>. Select your platform and format.</span>
            ) : (
              <span>Choose your target market once. We'll configure your publishing studio automatically.</span>
            )}
          </p>
        </div>

        {/* Breadcrumb */}
        <div className={styles.breadcrumb}>
          <button 
            className={`${styles.crumb} ${step === 'country' ? styles.crumbActive : ''}`} 
            onClick={() => {
              if (hasSavedPreference) {
                navigate('/settings');
              } else {
                setStep('country');
              }
            }}
            title={hasSavedPreference ? "Target country saved. Click to change in Settings." : "Select Country"}
          >
            <Globe size={13} /> Country
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
          <button 
            className={`${styles.crumb} ${step === 'platform' ? styles.crumbActive : ''} ${step === 'country' ? styles.crumbDisabled : ''}`} 
            onClick={() => step !== 'country' && setStep('platform')}
          >
            <span>
               {platform ? <img src={getPlatformLogoUrl(platform)} className={styles.breadcrumbImg} alt=""/> : <Globe size={13} />}
            </span> Platform
            {platform && step === 'format' && <span className={styles.crumbValue}>{platform}</span>}
          </button>
          <ChevronRight size={14} className={styles.crumbArrow} />
          <button 
            className={`${styles.crumb} ${step === 'format' ? styles.crumbActive : ''} ${step !== 'format' ? styles.crumbDisabled : ''}`} 
            onClick={() => step === 'format' && setStep('format')}
          >
            <Zap size={13} /> Format
          </button>
        </div>

        {/* Step: Country (First-time selection) */}
        {step === 'country' && (
          <div className={styles.stepPanel}>
            <div style={{ textAlign: 'center', marginBottom: '1.5rem', color: 'rgba(255,255,255,0.4)', fontSize: '0.875rem' }}>
              Select your primary target market once. You can change this anytime in Settings.
            </div>
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
              <span className={styles.contextSub}>Popular platforms in this market</span>
              <button 
                className={styles.changeSettingsLink}
                onClick={() => navigate('/settings')}
                title="Change default target country in Settings"
              >
                <Settings size={13} />
                <span>Change in Settings</span>
              </button>
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
                    style={platform === p && config ? { borderColor: config.accentColor, boxShadow: `0 0 28px ${config.accentColor}50` } : {}}
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
                  style={selectedFormat?.id === fmt.id ? { borderColor: platformConfig.accentColor, boxShadow: `0 0 28px ${platformConfig.accentColor}55` } : {}}
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
          </div>
        )}
      </div>
    </div>
  );
}
