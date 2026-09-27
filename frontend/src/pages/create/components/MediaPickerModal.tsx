import { useState, useRef, useCallback } from 'react';
import { X, Upload, Search, Image as ImageIcon, Link as LinkIcon, Plus } from 'lucide-react';
import styles from './MediaPickerModal.module.css';

interface MediaPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectImage: (imageUrl: string, title?: string) => void;
}

type TabType = 'upload' | 'search' | 'library' | 'url';

interface MediaItem {
  id: string;
  url: string;
  title: string;
  category: string;
}

// Curated high-res imagery for creator presets & search
const STOCK_COLLECTIONS: MediaItem[] = [
  // Tech & Coding
  { id: 'tech-1', title: 'Developer Workspace', category: 'Tech', url: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&auto=format&fit=crop&q=80' },
  { id: 'tech-2', title: 'Clean Code Editor', category: 'Coding', url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&auto=format&fit=crop&q=80' },
  { id: 'tech-3', title: 'Matrix Neon Tech', category: 'Coding', url: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80' },
  { id: 'tech-4', title: 'AI & Data Visuals', category: 'Tech', url: 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&auto=format&fit=crop&q=80' },
  
  // Creator & Podcast
  { id: 'creator-1', title: 'Studio Podcast Mic', category: 'Creator', url: 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&auto=format&fit=crop&q=80' },
  { id: 'creator-2', title: 'Minimalist Desk Setup', category: 'Creator', url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800&auto=format&fit=crop&q=80' },
  { id: 'creator-3', title: 'Camera & Content Gear', category: 'Creator', url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=80' },
  { id: 'creator-4', title: 'Creative Brainstorming', category: 'Creator', url: 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=800&auto=format&fit=crop&q=80' },

  // Business & Growth
  { id: 'biz-1', title: 'Growth Analytics Dashboard', category: 'Business', url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=80' },
  { id: 'biz-2', title: 'Startup Team Meeting', category: 'Business', url: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&auto=format&fit=crop&q=80' },
  { id: 'biz-3', title: 'Modern Architecture', category: 'Business', url: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop&q=80' },
  { id: 'biz-4', title: 'Financial Charts & Market', category: 'Business', url: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&auto=format&fit=crop&q=80' },

  // Abstract & Gradients
  { id: 'abs-1', title: '3D Fluid Purple Mesh', category: 'Abstract', url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80' },
  { id: 'abs-2', title: 'Cyber Neon Lights', category: 'Abstract', url: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80' },
  { id: 'abs-3', title: 'Vibrant Sunset Gradient', category: 'Abstract', url: 'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=800&auto=format&fit=crop&q=80' },
  { id: 'abs-4', title: 'Dark Holographic Wave', category: 'Abstract', url: 'https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=800&auto=format&fit=crop&q=80' },

  // Minimal
  { id: 'min-1', title: 'Clean Architecture Shadows', category: 'Minimal', url: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=80' },
  { id: 'min-2', title: 'Monochrome Plant Aesthetics', category: 'Minimal', url: 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=800&auto=format&fit=crop&q=80' },
];

const SEARCH_CATEGORIES = ['All', 'Tech', 'Creator', 'Coding', 'Business', 'Abstract', 'Minimal'];

export function MediaPickerModal({ isOpen, onClose, onSelectImage }: MediaPickerModalProps) {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [customUrl, setCustomUrl] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file (PNG, JPG, WebP, SVG, GIF)');
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      if (result) {
        onSelectImage(result, file.name);
        onClose();
      }
    };
    reader.readAsDataURL(file);
  }, [onSelectImage, onClose]);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleUrlSubmit = () => {
    if (!customUrl.trim()) return;
    onSelectImage(customUrl.trim(), 'Web Image');
    onClose();
    setCustomUrl('');
  };

  // Filtered media items
  const filteredItems = STOCK_COLLECTIONS.filter(item => {
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    const matchesSearch = !searchQuery.trim() || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      item.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerInfo}>
            <h3 className={styles.title}>Add Media to Canvas</h3>
            <p className={styles.subtitle}>Upload your own photos, search stock imagery, or choose from CreatorOS presets.</p>
          </div>
          <button className={styles.closeBtn} onClick={onClose} title="Close">
            <X size={16} />
          </button>
        </div>

        {/* Tabs Bar */}
        <div className={styles.tabsBar}>
          <button
            className={`${styles.tabBtn} ${activeTab === 'upload' ? styles.tabBtnActive : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <Upload size={15} />
            <span>Upload from Device</span>
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'search' ? styles.tabBtnActive : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <Search size={15} />
            <span>Web & Stock Search</span>
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'library' ? styles.tabBtnActive : ''}`}
            onClick={() => setActiveTab('library')}
          >
            <ImageIcon size={15} />
            <span>Platform Presets</span>
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'url' ? styles.tabBtnActive : ''}`}
            onClick={() => setActiveTab('url')}
          >
            <LinkIcon size={15} />
            <span>Paste URL</span>
          </button>
        </div>

        {/* Content Body */}
        <div className={styles.content}>
          {/* TAB 1: Upload */}
          {activeTab === 'upload' && (
            <div
              className={`${styles.uploadDropzone} ${dragOver ? styles.uploadDropzoneDragOver : ''}`}
              onDragOver={e => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                hidden
                onChange={e => {
                  if (e.target.files && e.target.files[0]) {
                    handleFile(e.target.files[0]);
                  }
                }}
              />
              <div className={styles.uploadIconWrap}>
                <Upload size={26} />
              </div>
              <div>
                <p className={styles.uploadPrompt}>Click to browse or drag & drop image here</p>
                <p className={styles.uploadHint}>Supports PNG, JPG, WebP, SVG, GIF up to 25MB</p>
              </div>
              <button type="button" className={styles.browseBtn}>
                <Upload size={14} />
                Browse Files
              </button>
            </div>
          )}

          {/* TAB 2 & 3: Search & Presets */}
          {(activeTab === 'search' || activeTab === 'library') && (
            <>
              {activeTab === 'search' && (
                <div className={styles.searchRow}>
                  <Search size={16} className={styles.searchIcon} color="var(--muted-2)" />
                  <input
                    className={styles.searchInput}
                    placeholder="Search high-res stock photos (e.g. tech, podcast, coding, growth)…"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    autoFocus
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      style={{ background: 'none', border: 'none', color: 'var(--muted-2)', cursor: 'pointer' }}
                      onClick={() => setSearchQuery('')}
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>
              )}

              {/* Category Filter Pills */}
              <div className={styles.categoryPills}>
                {SEARCH_CATEGORIES.map(cat => (
                  <button
                    key={cat}
                    type="button"
                    className={`${styles.categoryPill} ${selectedCategory === cat ? styles.categoryPillActive : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              {/* Photos Grid */}
              <div className={styles.imageGrid}>
                {filteredItems.map(item => (
                  <div
                    key={item.id}
                    className={styles.imageCard}
                    onClick={() => {
                      onSelectImage(item.url, item.title);
                      onClose();
                    }}
                    title={`Click to add "${item.title}" to canvas`}
                  >
                    <img src={item.url} alt={item.title} className={styles.imageThumb} loading="lazy" />
                    <div className={styles.imageCardOverlay}>
                      <span className={styles.imageCardLabel}>{item.title}</span>
                      <div className={styles.imageAddIcon}>
                        <Plus size={14} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* TAB 4: URL Input */}
          {activeTab === 'url' && (
            <div className={styles.urlSection}>
              <div className={styles.urlInputRow}>
                <input
                  className={styles.urlInput}
                  placeholder="Paste direct image URL from Google or browser (e.g. https://...)"
                  value={customUrl}
                  onChange={e => setCustomUrl(e.target.value)}
                  autoFocus
                />
                <button
                  type="button"
                  className={styles.browseBtn}
                  onClick={handleUrlSubmit}
                  disabled={!customUrl.trim()}
                >
                  <Plus size={14} />
                  Add to Canvas
                </button>
              </div>

              {customUrl && (
                <div className={styles.urlPreview}>
                  <img
                    src={customUrl}
                    alt="Preview"
                    onError={(e) => {
                      (e.target as HTMLElement).style.display = 'none';
                    }}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
