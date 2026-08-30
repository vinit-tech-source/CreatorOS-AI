import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./LandingPage.css";

interface PlatformData {
  id: string;
  name: string;
  badge: string;
  aspectRatio: string;
  formatName: string;
  headline: string;
  subhead: string;
  tag: string;
  ctaText: string;
  accentColor: string;
  charLimit: string;
  hashtags: string[];
  icon: React.ReactNode;
}

const platformsData: PlatformData[] = [
  {
    id: "instagram",
    name: "Instagram",
    badge: "Feed & Carousel",
    aspectRatio: "1/1",
    formatName: "Square 1080 × 1080",
    headline: "BREAK YOUR LIMITS.",
    subhead: "Engineered for creators who never stop moving forward.",
    tag: "NEW DROP",
    ctaText: "SHOP THE DROP",
    accentColor: "linear-gradient(135deg, #f09433, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888)",
    charLimit: "2,200 chars • 30 hashtags",
    hashtags: ["#CreatorEconomy", "#BreakLimits", "#BuildInPublic", "#CreatorOS"],
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>
        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
        <line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>
      </svg>
    ),
  },
  {
    id: "shorts",
    name: "YouTube Shorts",
    badge: "Vertical Video",
    aspectRatio: "9/16",
    formatName: "Vertical 1080 × 1920",
    headline: "HOW TOP CREATORS WIN IN 2026",
    subhead: "The 3-step AI system powering 10M+ views per month.",
    tag: "TRENDING NOW",
    ctaText: "WATCH FULL BREAKDOWN",
    accentColor: "linear-gradient(135deg, #ff0000, #c40000)",
    charLimit: "60s video • High retention hook",
    hashtags: ["#Shorts", "#ContentStrategy", "#ViralGrowth", "#AItools"],
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2.5 7.1C2.6 5.8 3.6 4.8 4.9 4.7 8.3 4.4 15.7 4.4 19.1 4.7 20.4 4.8 21.4 5.8 21.5 7.1 21.8 9 21.8 15 21.5 16.9 21.4 18.2 20.4 19.2 19.1 19.3 15.7 19.6 8.3 19.6 4.9 19.3 3.6 19.2 2.6 18.2 2.5 16.9 2.2 15 2.2 9 2.5 7.1z"/>
        <path d="m10 15 5-3-5-3z"/>
      </svg>
    ),
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    badge: "Carousel & Post",
    aspectRatio: "4/5",
    formatName: "Document 1080 × 1350",
    headline: "THE FUTURE OF AI WORKFLOWS",
    subhead: "Why content teams are replacing 6 fragmented tools with 1 unified OS.",
    tag: "EXECUTIVE INSIGHTS",
    ctaText: "READ FRAMEWORK",
    accentColor: "linear-gradient(135deg, #0077b5, #004182)",
    charLimit: "3,000 chars • PDF slides ready",
    hashtags: ["#Leadership", "#Productivity", "#GenerativeAI", "#FutureOfWork"],
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
        <rect width="4" height="12" x="2" y="9"/>
        <circle cx="4" cy="4" r="2"/>
      </svg>
    ),
  },
  {
    id: "tiktok",
    name: "TikTok",
    badge: "Viral Short",
    aspectRatio: "9/16",
    formatName: "Vertical 1080 × 1920",
    headline: "DON'T POST WITHOUT THIS ⚡",
    subhead: "AI audio sync + auto captions boosted our watch time by 48%.",
    tag: "CREATOR HACK",
    ctaText: "TRY TEMPLATE",
    accentColor: "linear-gradient(135deg, #00f2fe, #4facfe)",
    charLimit: "Viral sound synced • Auto-captions",
    hashtags: ["#TikTokTips", "#ViralHacks", "#CreatorTok", "#GrowthMindset"],
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"/>
      </svg>
    ),
  },
  {
    id: "twitter",
    name: "X / Twitter",
    badge: "Viral Thread",
    aspectRatio: "16/9",
    formatName: "Landscape 1200 × 675",
    headline: "10 LAWS OF HIGH-CONVERTING CONTENT",
    subhead: "Tested across 1,000+ posts and $2.4M in pipeline generated. [Thread 🧵]",
    tag: "CASE STUDY",
    ctaText: "RETWEET & SAVE",
    accentColor: "linear-gradient(135deg, #333, #111)",
    charLimit: "280 chars • 7-part thread auto-split",
    hashtags: ["#MarketingTwitter", "#SaaS", "#BuildingInPublic"],
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 4l16 16"/>
        <path d="M4 20L20 4"/>
      </svg>
    ),
  },
];

interface CountryData {
  name: string;
  flag: string;
  primaryPlatforms: string[];
  topLanguage: string;
  peakTime: string;
  marketSize: string;
  growthRate: string;
}

const countriesData: CountryData[] = [
  {
    name: "India",
    flag: "🇮🇳",
    primaryPlatforms: ["YouTube", "Instagram", "LinkedIn", "WhatsApp"],
    topLanguage: "Hindi & English (Hinglish)",
    peakTime: "7:30 PM - 9:30 PM IST",
    marketSize: "750M+ Digital Consumers",
    growthRate: "+28% YoY Creator Growth",
  },
  {
    name: "United States",
    flag: "🇺🇸",
    primaryPlatforms: ["TikTok", "Instagram", "YouTube", "X", "LinkedIn"],
    topLanguage: "English (US)",
    peakTime: "11:00 AM & 7:00 PM EST",
    marketSize: "310M+ Online Audience",
    growthRate: "+19% Brand Spend YoY",
  },
  {
    name: "United Kingdom",
    flag: "🇬🇧",
    primaryPlatforms: ["LinkedIn", "Instagram", "TikTok", "YouTube"],
    topLanguage: "English (UK)",
    peakTime: "8:00 AM & 6:30 PM GMT",
    marketSize: "62M+ Active Users",
    growthRate: "+15% B2B Influence",
  },
  {
    name: "United Arab Emirates",
    flag: "🇦🇪",
    primaryPlatforms: ["Instagram", "TikTok", "YouTube", "Snapchat"],
    topLanguage: "Arabic & English",
    peakTime: "8:00 PM - 11:00 PM GST",
    marketSize: "High Purchasing Power",
    growthRate: "+34% Video Consumption",
  },
  {
    name: "Japan",
    flag: "🇯🇵",
    primaryPlatforms: ["X (Twitter)", "YouTube", "LINE", "Instagram"],
    topLanguage: "Japanese",
    peakTime: "12:00 PM & 9:00 PM JST",
    marketSize: "100M+ Social Users",
    growthRate: "High Text & Visual Affinity",
  },
  {
    name: "Singapore",
    flag: "🇸🇬",
    primaryPlatforms: ["LinkedIn", "Instagram", "TikTok", "YouTube"],
    topLanguage: "English & Mandarin",
    peakTime: "12:30 PM & 8:00 PM SGT",
    marketSize: "Global APAC Hub",
    growthRate: "+22% Cross-Border Reach",
  },
];

const studioFeatures = [
  {
    id: "ai-copy",
    title: "AI Prompt & Copy Engine",
    desc: "Generate viral hooks, captions, scripts, and multi-lingual translations in 1 click.",
    pill: "Instant Copy",
    icon: "✦",
    codeSnippet: "Prompt: 'Make this headline punchier and optimize for high click-through on LinkedIn'",
    result: "Generated: 'Stop Posting Blindly: The 3 Metrics Top 1% Creators Track'",
  },
  {
    id: "visual-canvas",
    title: "Dynamic Smart Canvas",
    desc: "Layer management, typography styles, brand palettes, and instant asset library.",
    pill: "Smart Studio",
    icon: "◈",
    codeSnippet: "Applied: Brand Kit #060914 + Vivid Violet Gradients + Inter Font System",
    result: "Status: 100% On-Brand typography and color hierarchy auto-applied",
  },
  {
    id: "adapt-engine",
    title: "1-Click Multi-Platform Adapt",
    desc: "Turn a single master creative into 6 platform-optimized formats in under 3 seconds.",
    pill: "Auto-Repurpose",
    icon: "⬡",
    codeSnippet: "Action: Auto-convert 1080x1080 master -> 9:16 Reel + 16:9 Banner + Carousel",
    result: "Output: 5 platform-ready files with customized aspect ratios and safe zones",
  },
  {
    id: "brand-brain",
    title: "Brand Brain & Voice",
    desc: "Train AI on your company tone, past high-performing posts, and design rules.",
    pill: "Tone Consistency",
    icon: "◎",
    codeSnippet: "Knowledge Base: 'Tone: Direct, energetic, data-backed, zero fluff.'",
    result: "Compliance: 99.4% tone alignment across all generated assets",
  },
];

const testimonials = [
  {
    name: "Alex Rivera",
    role: "Founder & Creator (480K Community)",
    metric: "+340% Reach Growth",
    subMetric: "In 60 days across 4 channels",
    avatar: "A",
    text: "CreatorOS solved our biggest bottleneck: repurposing. We go from 1 podcast clip to 12 platform-tailored posts in 15 minutes instead of 4 hours.",
    stars: "★★★★★",
  },
  {
    name: "Sarah Chen",
    role: "Head of Content @ HyperScale SaaS",
    metric: "18 hrs / week Saved",
    subMetric: "Across a 6-person global team",
    avatar: "S",
    text: "The country intelligence and localized formatting allowed us to launch simultaneously in the US, India, and UK with perfect tone nuance.",
    stars: "★★★★★",
  },
  {
    name: "Marcus Vance",
    role: "Director of Digital, Vance Agency",
    metric: "8.4x Content Volume",
    subMetric: "Managing 14 enterprise clients",
    avatar: "M",
    text: "Client approval cycles dropped from 4 days to 3 hours with the built-in live preview and approval workflow. An indispensable operating system.",
    stars: "★★★★★",
  },
];

const faqs = [
  {
    q: "How does CreatorOS adapt one piece of content to every platform?",
    a: "CreatorOS analyzes your master content and automatically reformats typography, safe zones, visual aspect ratios (1:1, 9:16, 16:9, 4:5), and caption lengths for Instagram, YouTube, TikTok, LinkedIn, and X without manual resizing.",
  },
  {
    q: "Can I train CreatorOS on my unique brand voice and visual style?",
    a: "Yes! With Brand Brain, you can upload brand guidelines, color palettes, fonts, and past top-performing posts. The AI will generate all future designs and copy strictly in your brand tone.",
  },
  {
    q: "Does CreatorOS support multi-language translation and localization?",
    a: "Absolutely. With Country Intelligence, you can adapt content into 40+ languages (including Hinglish, Arabic, Japanese, Spanish) with culturally tuned hooks and platform-specific peak timing recommendations.",
  },
  {
    q: "Do I need a credit card to get started?",
    a: "No credit card required. You can start with our generous Free tier, generate posts, explore the interactive studio, and export content right away.",
  },
];

function AppLogo() {
  return (
    <Link to="/" className="brand" style={{ textDecoration: "none" }}>
      <div className="brand-mark">
        <span />
        <span />
        <span />
      </div>
      <div>
        <div className="brand-name">CreatorOS</div>
        <div className="brand-tagline">Create once. Adapt everywhere.</div>
      </div>
    </Link>
  );
}

export function LandingPage() {
  const [selectedPlatform, setSelectedPlatform] = useState<PlatformData>(platformsData[0]);
  const [selectedCountry, setSelectedCountry] = useState<CountryData>(countriesData[0]);
  const [activeStudioTab, setActiveStudioTab] = useState<string>("ai-copy");
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [isGenerating, setIsGenerating] = useState(false);
  const [promptText, setPromptText] = useState("Make the hook bolder and add a call to action");

  const currentStudioFeature = studioFeatures.find((f) => f.id === activeStudioTab) || studioFeatures[0];

  const handleSimulateAI = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
    }, 900);
  };

  return (
    <div className="landing-page">
      {/* Background Ambience Orbs */}
      <div className="ambient-glow glow-1" />
      <div className="ambient-glow glow-2" />
      <div className="ambient-glow glow-3" />

      {/* Navigation */}
      <header className="nav">
        <AppLogo />
        <nav className="nav-links">
          <a href="#features">Features</a>
          <a href="#studio">Studio</a>
          <a href="#intelligence">Global Intelligence</a>
          <a href="#workflow">Workflow</a>
          <a href="#testimonials">Testimonials</a>
          <a href="#pricing">Pricing</a>
        </nav>
        <div className="nav-actions">
          <Link to="/login" className="signin">Sign In</Link>
          <Link to="/dashboard" className="primary-btn small">
            Start Creating Free →
          </Link>
        </div>
      </header>

      <main>
        {/* HERO SECTION */}
        <section className="hero section-shell">
          <div className="hero-copy">
            <div className="announcement-pill">
              <span className="pill-dot">✦</span>
              <span>CreatorOS 2.0 is Live</span>
              <span className="pill-tag">AI Multi-Platform Engine</span>
            </div>
            
            <h1>
              One Idea. Every Platform. <br />
              <span className="gradient-text">One Intelligent Workspace.</span>
            </h1>
            
            <p className="hero-description">
              Stop re-creating the same post 5 times. CreatorOS turns your ideas into 
              pixel-perfect, audience-tailored content across Instagram, YouTube, 
              LinkedIn, TikTok, and X — in seconds.
            </p>

            <div className="hero-buttons">
              <Link to="/dashboard" className="primary-btn hero-cta">
                <span>Start Creating Free</span>
                <span className="btn-arrow">→</span>
              </Link>
              <a href="#studio" className="secondary-btn">
                <span className="play-icon">▶</span>
                <span>Watch Interactive Demo</span>
              </a>
            </div>

            <div className="trusted-row">
              <div className="avatar-stack">
                <div style={{ background: "#4f46e5" }}>V</div>
                <div style={{ background: "#ec4899" }}>A</div>
                <div style={{ background: "#10b981" }}>R</div>
                <div style={{ background: "#f59e0b" }}>S</div>
              </div>
              <div className="trusted-text">
                <strong>10,000+ top creators & brands</strong>
                <span>Generated 4.2M+ high-performing posts</span>
              </div>
            </div>

            <div className="brand-strip-container">
              <div className="brand-strip-label">TRUSTED BY CONTENT TEAMS AT</div>
              <div className="brand-strip">
                <span>Notion</span>
                <span>HubSpot</span>
                <span>monday.com</span>
                <span>Revolut</span>
                <span>Deloitte.</span>
              </div>
            </div>
          </div>

          {/* HERO INTERACTIVE SHOWCASE */}
          <div className="hero-showcase-wrapper">
            <div className="showcase-glow-card">
              {/* Platform Selector Tabs */}
              <div className="showcase-platform-tabs">
                {platformsData.map((plat) => (
                  <button
                    key={plat.id}
                    className={`platform-tab-btn ${selectedPlatform.id === plat.id ? "active" : ""}`}
                    onClick={() => setSelectedPlatform(plat)}
                  >
                    <span className="tab-icon">{plat.icon}</span>
                    <span className="tab-name">{plat.name}</span>
                    {selectedPlatform.id === plat.id && <span className="tab-active-indicator" />}
                  </button>
                ))}
              </div>

              {/* Main Live Preview Canvas */}
              <div className="hero-preview-container">
                <div className="preview-topbar">
                  <div className="preview-dots">
                    <span />
                    <span />
                    <span />
                  </div>
                  <div className="preview-title-badge">
                    <span className="live-dot" />
                    <span>Live Adaptation: {selectedPlatform.name} ({selectedPlatform.formatName})</span>
                  </div>
                  <div className="preview-actions">
                    <span className="format-ratio-tag">{selectedPlatform.aspectRatio}</span>
                    <button className="preview-export-btn" onClick={handleSimulateAI}>
                      {isGenerating ? "Adapting..." : "✦ Auto-Adapt"}
                    </button>
                  </div>
                </div>

                <div className="preview-content-grid">
                  {/* Left: Dynamic Visual Mockup */}
                  <div className="canvas-frame">
                    <div
                      className="canvas-artwork"
                      style={{
                        aspectRatio: selectedPlatform.aspectRatio === "9/16" ? "9/14" : selectedPlatform.aspectRatio,
                      }}
                    >
                      <div className="artwork-overlay" />
                      <div className="artwork-content">
                        <span className="artwork-tag">{selectedPlatform.tag}</span>
                        <h2 className="artwork-headline">{selectedPlatform.headline}</h2>
                        <p className="artwork-subhead">{selectedPlatform.subhead}</p>
                        <div className="artwork-cta-badge">{selectedPlatform.ctaText}</div>
                      </div>
                      <div className="artwork-watermark">CreatorOS Studio</div>
                    </div>
                  </div>

                  {/* Right: Live Meta & AI Assistant */}
                  <div className="preview-meta-panel">
                    <div className="meta-block">
                      <div className="meta-label">TARGET PLATFORM</div>
                      <div className="meta-value-row">
                        <span className="meta-platform-name">{selectedPlatform.name}</span>
                        <span className="meta-pill">{selectedPlatform.badge}</span>
                      </div>
                      <div className="meta-specs">{selectedPlatform.charLimit}</div>
                    </div>

                    <div className="meta-block">
                      <div className="meta-label">SUGGESTED HASHTAGS</div>
                      <div className="meta-hashtags">
                        {selectedPlatform.hashtags.map((tag) => (
                          <span key={tag} className="hashtag-chip">{tag}</span>
                        ))}
                      </div>
                    </div>

                    {/* Interactive AI Prompt Trigger */}
                    <div className="ai-command-box">
                      <div className="ai-command-header">
                        <span className="spark-icon">✨</span>
                        <strong>AI Studio Copilot</strong>
                      </div>
                      <div className="ai-input-wrapper">
                        <input
                          type="text"
                          value={promptText}
                          onChange={(e) => setPromptText(e.target.value)}
                          placeholder="Tell AI to modify headline, tone, or style..."
                          className="ai-prompt-input"
                        />
                        <button
                          className="ai-send-btn"
                          onClick={handleSimulateAI}
                          disabled={isGenerating}
                        >
                          {isGenerating ? "..." : "→"}
                        </button>
                      </div>
                      <div className="ai-chips">
                        <span onClick={() => setPromptText("Make it punchier for high engagement")}>⚡ Punchier</span>
                        <span onClick={() => setPromptText("Translate into localized Hindi")}>🌐 Localize</span>
                        <span onClick={() => setPromptText("Add 3 viral curiosity hooks")}>🎯 Viral Hooks</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Multi-Platform Indicator Badge */}
              <div className="floating-repurpose-pill">
                <span className="repurpose-icon">⚡</span>
                <div className="repurpose-text">
                  <strong>One Master Input</strong>
                  <span>Instant sync to 5 platform safe zones</span>
                </div>
                <span className="repurpose-count">5 Formats Ready</span>
              </div>
            </div>
          </div>
        </section>

        {/* FEATURE STATS BAR */}
        <section className="stats-ticker section-shell">
          <div className="stat-card">
            <span className="stat-number">10x</span>
            <span className="stat-label">Faster Content Creation</span>
            <span className="stat-sub">From concept to publish</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">100%</span>
            <span className="stat-label">Brand Consistency</span>
            <span className="stat-sub">Automated voice & colors</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">40+</span>
            <span className="stat-label">Languages & Markets</span>
            <span className="stat-sub">Localized intelligence</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">3.8x</span>
            <span className="stat-label">Higher Engagement</span>
            <span className="stat-sub">Platform-native formatting</span>
          </div>
        </section>

        {/* WORKFLOW SECTION */}
        <section id="workflow" className="section section-shell">
          <div className="section-heading centered">
            <div className="eyebrow">SEAMLESS CREATIVE WORKFLOW</div>
            <h2>How CreatorOS Replaces 6 Disconnected Tools</h2>
            <p>From initial brainstorming to multi-channel scheduling, manage everything inside one high-speed OS.</p>
          </div>

          <div className="workflow-bento-grid">
            <div className="bento-step">
              <div className="step-badge">STEP 01</div>
              <div className="step-icon">💡</div>
              <h3>Choose & Brainstorm</h3>
              <p>Select target country, audience personas, format, and core objective in seconds.</p>
            </div>

            <div className="bento-step">
              <div className="step-badge">STEP 02</div>
              <div className="step-icon">✦</div>
              <h3>AI-Powered Creation</h3>
              <p>Generate high-converting headlines, design templates, and tailored scripts with 1 click.</p>
            </div>

            <div className="bento-step highlight-step">
              <div className="step-badge highlight-badge">STEP 03 • CORE POWER</div>
              <div className="step-icon">⚡</div>
              <h3>Adapt & Repurpose</h3>
              <p>One master file automatically resizes and formats for IG, YouTube, LinkedIn, X, and TikTok.</p>
            </div>

            <div className="bento-step">
              <div className="step-badge">STEP 04</div>
              <div className="step-icon">◎</div>
              <h3>Localize & Translate</h3>
              <p>Culturally tune your hooks, languages, and posting schedules for international markets.</p>
            </div>

            <div className="bento-step">
              <div className="step-badge">STEP 05</div>
              <div className="step-icon">▣</div>
              <h3>Team Approvals</h3>
              <p>Collaborate with clients and marketing managers with real-time feedback and approval gates.</p>
            </div>

            <div className="bento-step">
              <div className="step-badge">STEP 06</div>
              <div className="step-icon">📈</div>
              <h3>Schedule & Learn</h3>
              <p>Automate multi-channel publishing and track cross-platform performance metrics in one hub.</p>
            </div>
          </div>
        </section>

        {/* INTERACTIVE CREATION STUDIO SHOWCASE */}
        <section id="studio" className="section section-shell studio-feature-section">
          <div className="section-heading">
            <div className="eyebrow">THE CREATION STUDIO</div>
            <h2>Built For Creators Who Care About Quality</h2>
            <p>Not just generic text generation. A complete visual canvas with layer control, AI redesign, and multi-format preview.</p>
          </div>

          <div className="studio-tabs-row">
            {studioFeatures.map((feat) => (
              <button
                key={feat.id}
                className={`studio-tab-btn ${activeStudioTab === feat.id ? "active" : ""}`}
                onClick={() => setActiveStudioTab(feat.id)}
              >
                <span className="studio-tab-icon">{feat.icon}</span>
                <span className="studio-tab-title">{feat.title}</span>
                <span className="studio-tab-pill">{feat.pill}</span>
              </button>
            ))}
          </div>

          <div className="interactive-studio-board">
            <div className="studio-board-info">
              <span className="feature-pill-active">{currentStudioFeature.pill}</span>
              <h3>{currentStudioFeature.title}</h3>
              <p>{currentStudioFeature.desc}</p>
              
              <div className="interactive-console-card">
                <div className="console-header">
                  <span className="console-dot" />
                  <span>AI Engine Command</span>
                </div>
                <div className="console-code">{currentStudioFeature.codeSnippet}</div>
                <div className="console-output">
                  <span className="output-tag">✓ Result</span>
                  <span>{currentStudioFeature.result}</span>
                </div>
              </div>

              <div className="studio-actions-group">
                <Link to="/create" className="primary-btn">
                  <span>Open Creation Studio</span>
                  <span>→</span>
                </Link>
              </div>
            </div>

            <div className="studio-board-preview">
              <div className="mock-studio-frame">
                <div className="mock-studio-top">
                  <div className="mock-dots"><span /><span /><span /></div>
                  <span className="mock-file-name">Master_Campaign_2026.cros</span>
                  <span className="mock-badge-ready">● AI Synced</span>
                </div>

                <div className="mock-studio-body">
                  <div className="mock-sidebar-tools">
                    <span className="tool-icon active">✦</span>
                    <span className="tool-icon">Aa</span>
                    <span className="tool-icon">🖼</span>
                    <span className="tool-icon">🎨</span>
                    <span className="tool-icon">🌐</span>
                  </div>

                  <div className="mock-canvas-center">
                    <div className="mock-canvas-art">
                      <div className="art-gradient-bg" />
                      <div className="art-layer-badge">ACTIVE CANVAS • 1080 × 1080</div>
                      <h4>THE FUTURE OF AI WORKFLOWS</h4>
                      <p>Create Once. Adapt Everywhere.</p>
                      <button className="art-btn">EXPLORE NOW</button>
                    </div>
                  </div>

                  <div className="mock-right-inspector">
                    <div className="inspector-title">AI Toolset</div>
                    <button className="inspector-btn">⚡ Rewrite Tone</button>
                    <button className="inspector-btn">🎯 Enhance Hook</button>
                    <button className="inspector-btn">🌐 Localize Text</button>
                    <div className="inspector-title" style={{ marginTop: "12px" }}>Active Layers</div>
                    <div className="layer-item"><span>Headline Text</span><span>👁</span></div>
                    <div className="layer-item"><span>Brand Backdrop</span><span>👁</span></div>
                    <div className="layer-item"><span>CTA Button</span><span>👁</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* COUNTRY & GLOBAL INTELLIGENCE SECTION */}
        <section id="intelligence" className="section section-shell intelligence-section-wrapper">
          <div className="section-heading centered">
            <div className="eyebrow">GLOBAL INTELLIGENCE</div>
            <h2>Create for Every Market with Cultural Accuracy</h2>
            <p>Select any region to automatically discover peak posting windows, trending platform nuances, and localized tone suggestions.</p>
          </div>

          <div className="intelligence-interactive-container">
            {/* Country Selector Column */}
            <div className="country-selector-panel">
              <div className="country-panel-header">
                <strong>Select Target Market</strong>
                <span>Instant regional data</span>
              </div>
              <div className="country-btn-list">
                {countriesData.map((country) => (
                  <button
                    key={country.name}
                    className={`country-select-btn ${selectedCountry.name === country.name ? "active" : ""}`}
                    onClick={() => setSelectedCountry(country)}
                  >
                    <span className="c-flag">{country.flag}</span>
                    <span className="c-name">{country.name}</span>
                    <span className="c-arrow">→</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Middle: Glowing Radar Visual */}
            <div className="radar-globe-wrapper">
              <div className="radar-orbit-ring">
                <div className="radar-sweep" />
                <div className="radar-center-core">
                  <span className="core-flag">{selectedCountry.flag}</span>
                  <span className="core-country">{selectedCountry.name}</span>
                </div>
                <div className="radar-ping p1" />
                <div className="radar-ping p2" />
                <div className="radar-ping p3" />
              </div>
            </div>

            {/* Right: Real-Time Intelligence Card */}
            <div className="regional-insights-card">
              <div className="insights-header">
                <span className="insights-flag">{selectedCountry.flag}</span>
                <div>
                  <h4>{selectedCountry.name} Market Intelligence</h4>
                  <span className="insights-sub">{selectedCountry.growthRate}</span>
                </div>
              </div>

              <div className="insights-data-grid">
                <div className="insight-item">
                  <span className="item-label">PRIMARY PLATFORMS</span>
                  <div className="platform-badges-row">
                    {selectedCountry.primaryPlatforms.map((p) => (
                      <span key={p} className="p-badge">{p}</span>
                    ))}
                  </div>
                </div>

                <div className="insight-item">
                  <span className="item-label">PREFERRED LANGUAGE / DIALECT</span>
                  <span className="item-value highlight-val">{selectedCountry.topLanguage}</span>
                </div>

                <div className="insight-item">
                  <span className="item-label">PEAK AUDIENCE ENGAGEMENT TIME</span>
                  <span className="item-value">{selectedCountry.peakTime}</span>
                </div>

                <div className="insight-item">
                  <span className="item-label">ESTIMATED MARKET REACH</span>
                  <span className="item-value">{selectedCountry.marketSize}</span>
                </div>
              </div>

              <button className="primary-btn full-width" onClick={() => setSelectedPlatform(platformsData[0])}>
                <span>Create Content for {selectedCountry.name}</span>
                <span>→</span>
              </button>
            </div>
          </div>
        </section>

        {/* AUDIENCE PROFILES (FIXED DARK THEME) */}
        <section className="section section-shell audience-section">
          <div className="section-heading centered">
            <div className="eyebrow">WHO CREATOROS IS BUILT FOR</div>
            <h2>Tailored for Every Stage of Creative Growth</h2>
            <p>From solo power creators to multi-million dollar agencies and enterprises.</p>
          </div>

          <div className="audience-cards-grid">
            <div className="audience-box">
              <div className="audience-icon-badge" style={{ background: "rgba(94, 82, 246, 0.15)", color: "#a599ff" }}>✦</div>
              <h3>Solo Creators & Influencers</h3>
              <p>Build a multi-channel presence without burning out. Scale your output from 2 posts a week to 15+ without hiring an assistant.</p>
              <div className="audience-perk-tag">✓ 1-Click Multi-Channel Sync</div>
            </div>

            <div className="audience-box">
              <div className="audience-icon-badge" style={{ background: "rgba(239, 95, 209, 0.15)", color: "#ef5fd1" }}>◈</div>
              <h3>High-Growth Brands & Startups</h3>
              <p>Turn product updates and customer stories into consistent lead magnets across LinkedIn, X, and Instagram automatically.</p>
              <div className="audience-perk-tag">✓ High-Converting Templates</div>
            </div>

            <div className="audience-box">
              <div className="audience-icon-badge" style={{ background: "rgba(40, 184, 255, 0.15)", color: "#28b8ff" }}>⚡</div>
              <h3>Marketing Teams</h3>
              <p>Collaborate, assign approval roles, enforce brand guidelines, and schedule campaigns across global regions effortlessly.</p>
              <div className="audience-perk-tag">✓ Approval Gates & Brand Voice</div>
            </div>

            <div className="audience-box">
              <div className="audience-icon-badge" style={{ background: "rgba(130, 229, 93, 0.15)", color: "#82e55d" }}>▣</div>
              <h3>Creative Agencies</h3>
              <p>Manage multiple client workspaces with dedicated brand kits, distinct AI memory, and white-label client approval portals.</p>
              <div className="audience-perk-tag">✓ Multi-Workspace Management</div>
            </div>
          </div>
        </section>

        {/* TESTIMONIALS / PROOF */}
        <section id="testimonials" className="section section-shell testimonials-section">
          <div className="section-heading centered">
            <div className="eyebrow">CREATOR STORIES</div>
            <h2>Loved by the World's Fastest Growing Creators</h2>
            <p>See how teams are multiplying their reach while cutting production time by 80%.</p>
          </div>

          <div className="testimonials-grid">
            {testimonials.map((t) => (
              <div key={t.name} className="testimonial-card">
                <div className="t-rating">{t.stars}</div>
                <p className="t-text">"{t.text}"</p>
                <div className="t-metric-badge">
                  <strong>{t.metric}</strong>
                  <span>{t.subMetric}</span>
                </div>
                <div className="t-user">
                  <div className="t-avatar">{t.avatar}</div>
                  <div>
                    <strong className="t-name">{t.name}</strong>
                    <span className="t-role">{t.role}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* FAQ SECTION */}
        <section className="section section-shell faq-section">
          <div className="section-heading centered">
            <div className="eyebrow">FREQUENTLY ASKED QUESTIONS</div>
            <h2>Everything You Need to Know</h2>
          </div>

          <div className="faq-accordion-list">
            {faqs.map((faq, index) => (
              <div
                key={faq.q}
                className={`faq-item ${openFaq === index ? "open" : ""}`}
                onClick={() => setOpenFaq(openFaq === index ? null : index)}
              >
                <div className="faq-question">
                  <span>{faq.q}</span>
                  <span className="faq-toggle">{openFaq === index ? "−" : "+"}</span>
                </div>
                {openFaq === index && (
                  <div className="faq-answer">
                    <p>{faq.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* HIGH-IMPACT FINAL CTA */}
        <section id="pricing" className="section section-shell final-cta-wrapper">
          <div className="cta-banner-card">
            <div className="cta-glow-decor" />
            <div className="cta-inner">
              <div className="announcement-pill" style={{ margin: "0 auto 20px" }}>
                <span>✦ Start Creating In Under 60 Seconds</span>
              </div>
              <h2>Ready to Turn One Idea into Multi-Platform Reach?</h2>
              <p>Join 10,000+ creators and brands saving 15+ hours every week with CreatorOS.</p>

              <div className="cta-action-row">
                <Link to="/dashboard" className="primary-btn large-cta">
                  <span>Get Started for Free</span>
                  <span>→</span>
                </Link>
                <Link to="/login" className="secondary-btn">
                  <span>Sign In to Account</span>
                </Link>
              </div>

              <div className="cta-guarantees">
                <span>✓ Free tier available</span>
                <span>✓ No credit card required</span>
                <span>✓ Cancel anytime</span>
                <span>✓ Export in all resolutions</span>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="footer section-shell">
        <div className="footer-brand">
          <AppLogo />
          <p className="footer-tagline">
            The AI Content Operating System. Build once, adapt everywhere, connect globally.
          </p>
          <div className="footer-newsletter">
            <span>Subscribe to our Creator Intelligence dispatch</span>
            <div className="newsletter-input-row">
              <input type="email" placeholder="Enter your email" />
              <button>Subscribe</button>
            </div>
          </div>
        </div>

        <div className="footer-column">
          <h4>Product</h4>
          <Link to="/create">Creation Studio</Link>
          <Link to="/content">Content Library</Link>
          <Link to="/calendar">Calendar & Scheduling</Link>
          <Link to="/approval">Approval Center</Link>
          <Link to="/automation">AI Pipelines</Link>
          <Link to="/analytics">Insights & Analytics</Link>
        </div>

        <div className="footer-column">
          <h4>Features</h4>
          <a href="#studio">Dynamic Smart Canvas</a>
          <a href="#studio">1-Click Repurposing</a>
          <a href="#intelligence">Country Intelligence</a>
          <a href="#studio">Brand Brain</a>
          <Link to="/brand-kit">Brand Kit Assets</Link>
        </div>

        <div className="footer-column">
          <h4>Resources</h4>
          <a href="#workflow">Workflow Guide</a>
          <a href="#testimonials">Creator Case Studies</a>
          <a href="#pricing">Pricing Plans</a>
          <a href="#faq">FAQ</a>
          <Link to="/knowledge">Knowledge Base</Link>
        </div>

        <div className="footer-column">
          <h4>Company</h4>
          <a href="#company">About Us</a>
          <a href="#contact">Contact</a>
          <a href="#privacy">Privacy Policy</a>
          <a href="#terms">Terms of Service</a>
          <a href="#security">Security</a>
        </div>

        <div className="footer-bottom">
          <span>© 2026 CreatorOS AI, Inc. All rights reserved.</span>
          <div className="social-links">
            <span>LinkedIn</span>
            <span>X (Twitter)</span>
            <span>Instagram</span>
            <span>YouTube</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
