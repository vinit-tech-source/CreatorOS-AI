import React, { useEffect, useState } from 'react';
import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Save, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { useBrandKitStore } from '../../stores/brandKitStore';
import styles from './BrandKit.module.css';

export function BrandKit() {
  const { activeWorkspace } = useWorkspaceStore();
  const { brandKit, isLoading, isSaving, error, fetchBrandKit, saveBrandKit } = useBrandKitStore();

  const [formData, setFormData] = useState({
    name: 'Default Brand',
    primary_color: '#000000',
    secondary_color: '#ffffff',
    font_family: 'Inter',
    logo_url: '',
    voice_tone: '',
  });

  useEffect(() => {
    if (activeWorkspace) {
      fetchBrandKit(activeWorkspace.id);
    }
  }, [activeWorkspace, fetchBrandKit]);

  useEffect(() => {
    if (brandKit) {
      setFormData({
        name: brandKit.name || 'Default Brand',
        primary_color: brandKit.primary_color || '#000000',
        secondary_color: brandKit.secondary_color || '#ffffff',
        font_family: brandKit.font_family || 'Inter',
        logo_url: brandKit.logo_url || '',
        voice_tone: brandKit.voice_tone || '',
      });
    }
  }, [brandKit]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    if (!activeWorkspace) return;
    try {
      await saveBrandKit(activeWorkspace.id, formData);
    } catch (err) {
      // Error is handled by store
    }
  };

  if (!activeWorkspace) {
    return (
      <div className={styles.container}>
        <PageHeader title="Brand Kit" subtitle="Manage your brand voice, tone, and visual identity." />
        <Card glass>
          <CardContent>
            <div className={styles.errorState}>
              <AlertCircle size={40} className="mb-4" />
              <p className="font-medium text-lg">No workspace selected</p>
              <p className={styles.errorMessage}>Select a workspace to manage its brand kit.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <PageHeader 
        title="Brand Kit" 
        subtitle="Manage your brand voice, tone, and visual identity."
        action={
          <Button onClick={handleSave} disabled={isLoading || isSaving} isLoading={isSaving}>
            <Save size={16} /> Save Changes
          </Button>
        }
      />

      {isLoading ? (
        <Card glass>
          <CardContent>
            <div className={styles.loadingState}>
              <RefreshCw size={32} className={styles.spinner} />
              <p>Loading Brand Kit...</p>
            </div>
          </CardContent>
        </Card>
      ) : error ? (
        <Card glass>
          <CardContent>
            <div className={styles.errorState}>
              <AlertCircle size={40} className="mb-4" />
              <p className="font-medium text-lg">Failed to load</p>
              <p className={styles.errorMessage}>{error}</p>
              <Button variant="outline" className="mt-4" onClick={() => fetchBrandKit(activeWorkspace.id)}>
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className={styles.content}>
          <Card glass>
            <CardContent>
              <div className={styles.formSection}>
                <div className={styles.sectionHeader}>
                  <h3 className={styles.sectionTitle}>Identity</h3>
                  <p className={styles.sectionSubtitle}>Core brand information</p>
                </div>
                
                <div className={styles.inputGroup}>
                  <label htmlFor="name" className={styles.label}>Brand Name</label>
                  <input 
                    id="name"
                    name="name"
                    type="text" 
                    className={styles.input} 
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="E.g. CreatorOS Official"
                  />
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="logo_url" className={styles.label}>Logo URL</label>
                  <input 
                    id="logo_url"
                    name="logo_url"
                    type="text" 
                    className={styles.input} 
                    value={formData.logo_url}
                    onChange={handleChange}
                    placeholder="https://example.com/logo.png"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card glass>
            <CardContent>
              <div className={styles.formSection}>
                <div className={styles.sectionHeader}>
                  <h3 className={styles.sectionTitle}>Visuals</h3>
                  <p className={styles.sectionSubtitle}>Colors and typography</p>
                </div>
                
                <div className={styles.colorPickers}>
                  <div className={styles.inputGroup}>
                    <label htmlFor="primary_color" className={styles.label}>Primary Color</label>
                    <div className={styles.colorRow}>
                      <div className={styles.colorPreview} style={{ backgroundColor: formData.primary_color }} />
                      <input 
                        id="primary_color"
                        name="primary_color"
                        type="text" 
                        className={styles.input} 
                        value={formData.primary_color}
                        onChange={handleChange}
                        placeholder="#000000"
                      />
                    </div>
                  </div>

                  <div className={styles.inputGroup}>
                    <label htmlFor="secondary_color" className={styles.label}>Secondary Color</label>
                    <div className={styles.colorRow}>
                      <div className={styles.colorPreview} style={{ backgroundColor: formData.secondary_color }} />
                      <input 
                        id="secondary_color"
                        name="secondary_color"
                        type="text" 
                        className={styles.input} 
                        value={formData.secondary_color}
                        onChange={handleChange}
                        placeholder="#ffffff"
                      />
                    </div>
                  </div>
                </div>

                <div className={styles.inputGroup}>
                  <label htmlFor="font_family" className={styles.label}>Font Family</label>
                  <input 
                    id="font_family"
                    name="font_family"
                    type="text" 
                    className={styles.input} 
                    value={formData.font_family}
                    onChange={handleChange}
                    placeholder="E.g. Inter, Roboto, sans-serif"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card glass>
            <CardContent>
              <div className={styles.formSection}>
                <div className={styles.sectionHeader}>
                  <h3 className={styles.sectionTitle}>Voice & Tone</h3>
                  <p className={styles.sectionSubtitle}>Guidelines for AI content generation</p>
                </div>
                
                <div className={styles.inputGroup}>
                  <label htmlFor="voice_tone" className={styles.label}>Brand Voice Instructions</label>
                  <textarea 
                    id="voice_tone"
                    name="voice_tone"
                    className={`${styles.input} ${styles.textarea}`} 
                    value={formData.voice_tone}
                    onChange={handleChange}
                    placeholder="Describe how the AI should sound. E.g. 'Professional, witty, and concise. Avoid emojis and jargon.'"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
