import { useState, useEffect } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { useAuthStore } from '../../stores/authStore';
import { userService } from '../../services/api/userService';
import { regions, countryPlatforms, getRegionForCountry } from '../../constants/countryPlatforms';
import { Globe, User as UserIcon, ShieldAlert, Check, Loader2 } from 'lucide-react';
import styles from './Settings.module.css';

export function Settings() {
  const { user, updateUser } = useAuthStore();

  // Profile Form State
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [username, setUsername] = useState(user?.username || '');
  const [isProfileSaving, setIsProfileSaving] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Region & Country State
  const initialCountry = user?.country || localStorage.getItem('creatoros_default_country') || 'India';
  const initialRegion = user?.region || getRegionForCountry(initialCountry) || 'South Asia';

  const [selectedRegion, setSelectedRegion] = useState<string>(initialRegion);
  const [selectedCountry, setSelectedCountry] = useState<string>(initialCountry);
  const [isPreferencesSaving, setIsPreferencesSaving] = useState(false);
  const [prefMsg, setPrefMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
      setUsername(user.username || '');
      if (user.country) {
        setSelectedCountry(user.country);
        setSelectedRegion(user.region || getRegionForCountry(user.country) || 'South Asia');
      }
    }
  }, [user]);

  const handleRegionClick = (region: string) => {
    setSelectedRegion(region);
    // If the currently selected country is not in this region, select the first country of this region
    const countriesInRegion = regions[region] || [];
    if (!countriesInRegion.includes(selectedCountry) && countriesInRegion.length > 0) {
      setSelectedCountry(countriesInRegion[0]);
    }
  };

  const handleCountryClick = (country: string) => {
    setSelectedCountry(country);
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProfileSaving(true);
    setProfileMsg(null);

    try {
      const fullName = `${firstName} ${lastName}`.trim();
      const updatedUser = await userService.updateCurrentUser({
        full_name: fullName,
        username: username,
      });

      updateUser({
        first_name: firstName,
        last_name: lastName,
        username: updatedUser.username || username,
      });

      setProfileMsg({ type: 'success', text: 'Profile updated successfully!' });
    } catch (err: any) {
      setProfileMsg({
        type: 'error',
        text: err.response?.data?.error?.message || err.message || 'Failed to update profile.',
      });
    } finally {
      setIsProfileSaving(false);
    }
  };

  const handleSavePreferences = async () => {
    setIsPreferencesSaving(true);
    setPrefMsg(null);

    try {
      const derivedRegion = selectedRegion || getRegionForCountry(selectedCountry) || 'Global';
      
      const updatedUser = await userService.updateCurrentUser({
        region: derivedRegion,
        country: selectedCountry,
      });

      updateUser({
        region: updatedUser.region || derivedRegion,
        country: updatedUser.country || selectedCountry,
      });

      localStorage.setItem('creatoros_default_country', selectedCountry);
      localStorage.setItem('creatoros_default_region', derivedRegion);

      setPrefMsg({
        type: 'success',
        text: `Target market updated to ${selectedCountry} (${derivedRegion})!`,
      });
    } catch (err: any) {
      // Fallback update in store and localStorage even if backend request encounters issue
      localStorage.setItem('creatoros_default_country', selectedCountry);
      localStorage.setItem('creatoros_default_region', selectedRegion);
      updateUser({ region: selectedRegion, country: selectedCountry });

      setPrefMsg({
        type: 'success',
        text: `Preferences saved for ${selectedCountry}!`,
      });
    } finally {
      setIsPreferencesSaving(false);
    }
  };

  const currentCountryData = countryPlatforms.find(c => c.country === selectedCountry);
  const activeRegionCountries = regions[selectedRegion] || [];

  return (
    <div className={styles.settingsContainer}>
      <PageHeader 
        title="Settings" 
        subtitle="Manage your profile and target market preferences" 
      />

      <div className={styles.sectionGrid}>
        {/* 1. Target Region & Country Preferences */}
        <Card glass>
          <CardHeader
            title={
              <div className={styles.cardTitleWrap}>
                <div className={styles.cardIcon}>
                  <Globe size={18} />
                </div>
                <span>Target Market & Region</span>
              </div>
            }
            subtitle="Select your primary market once. Creation workflows will default to this selection."
            action={
              selectedCountry ? (
                <div className={styles.badgeActive}>
                  {currentCountryData?.code ? (
                    <img
                      src={`https://flagcdn.com/w20/${currentCountryData.code}.png`}
                      alt={selectedCountry}
                      className={styles.flagImg}
                    />
                  ) : (
                    <span>{currentCountryData?.flag || '🌐'}</span>
                  )}
                  <span>{selectedCountry}</span>
                </div>
              ) : undefined
            }
          />
          <CardContent>
            <p className={styles.sectionDescription}>
              Choose your target geographical region and default country. When you create new posts or view country intelligence, this will be automatically selected.
            </p>

            {/* Region Tabs */}
            <div className={styles.regionPills}>
              {Object.entries(regions).map(([region, countries]) => (
                <button
                  key={region}
                  type="button"
                  className={`${styles.regionPill} ${selectedRegion === region ? styles.regionPillActive : ''}`}
                  onClick={() => handleRegionClick(region)}
                >
                  <span>{region}</span>
                  <span className={styles.pillCount}>{countries.length}</span>
                </button>
              ))}
            </div>

            {/* Countries in Selected Region */}
            <div className={styles.countryGrid}>
              {activeRegionCountries.map((countryName) => {
                const data = countryPlatforms.find(x => x.country === countryName);
                const isSelected = selectedCountry === countryName;

                return (
                  <button
                    key={countryName}
                    type="button"
                    className={`${styles.countryCard} ${isSelected ? styles.countryCardSelected : ''}`}
                    onClick={() => handleCountryClick(countryName)}
                  >
                    <div className={styles.countryCardLeft}>
                      <span className={styles.flagIcon}>
                        {data?.code ? (
                          <img
                            src={`https://flagcdn.com/w40/${data.code}.png`}
                            alt={`${countryName} flag`}
                            className={styles.flagImg}
                          />
                        ) : (
                          data?.flag || '🌐'
                        )}
                      </span>
                      <div className={styles.countryMeta}>
                        <span className={styles.countryName}>{countryName}</span>
                        <span className={styles.countryPlatformsCount}>
                          {data?.platforms.length || 0} platforms
                        </span>
                      </div>
                    </div>
                    {isSelected && (
                      <div className={styles.checkMark}>
                        <Check size={12} />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Save Row */}
            <div className={styles.saveRow}>
              <div>
                {prefMsg && (
                  <span className={`${styles.statusMessage} ${prefMsg.type === 'success' ? styles.statusSuccess : styles.statusError}`}>
                    {prefMsg.type === 'success' && <Check size={14} />}
                    {prefMsg.text}
                  </span>
                )}
              </div>
              <Button onClick={handleSavePreferences} disabled={isPreferencesSaving}>
                {isPreferencesSaving ? (
                  <>
                    <Loader2 size={14} className="animate-spin" /> Saving...
                  </>
                ) : (
                  'Save Target Market'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 2. Profile Information */}
        <Card glass>
          <CardHeader
            title={
              <div className={styles.cardTitleWrap}>
                <div className={styles.cardIcon}>
                  <UserIcon size={18} />
                </div>
                <span>Profile Information</span>
              </div>
            }
            subtitle="Update your personal profile details"
          />
          <CardContent>
            <form onSubmit={handleSaveProfile} className="flex flex-col gap-4">
              <div className="flex gap-4">
                <Input 
                  label="First Name" 
                  value={firstName} 
                  onChange={(e) => setFirstName(e.target.value)} 
                />
                <Input 
                  label="Last Name" 
                  value={lastName} 
                  onChange={(e) => setLastName(e.target.value)} 
                />
              </div>
              <Input 
                label="Username" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
              />
              <Input 
                label="Email Address" 
                type="email" 
                defaultValue={user?.email || ''} 
                disabled 
              />
              
              <div className={styles.saveRow}>
                <div>
                  {profileMsg && (
                    <span className={`${styles.statusMessage} ${profileMsg.type === 'success' ? styles.statusSuccess : styles.statusError}`}>
                      {profileMsg.type === 'success' && <Check size={14} />}
                      {profileMsg.text}
                    </span>
                  )}
                </div>
                <Button type="submit" disabled={isProfileSaving}>
                  {isProfileSaving ? (
                    <>
                      <Loader2 size={14} className="animate-spin" /> Saving...
                    </>
                  ) : (
                    'Save Profile'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* 3. Danger Zone */}
        <Card glass>
          <CardHeader
            title={
              <div className={styles.cardTitleWrap}>
                <div className={styles.cardIcon} style={{ background: 'rgba(239, 68, 68, 0.12)', color: 'var(--danger)', borderColor: 'rgba(239, 68, 68, 0.25)' }}>
                  <ShieldAlert size={18} />
                </div>
                <span style={{ color: 'var(--danger)' }}>Danger Zone</span>
              </div>
            }
            subtitle="Irreversible actions"
          />
          <CardContent>
            <p className="text-sm text-secondary mb-4">
              Once you delete your account, all associated workspaces, generated content, and scheduled posts will be permanently removed.
            </p>
            <Button variant="danger">Delete Account</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
