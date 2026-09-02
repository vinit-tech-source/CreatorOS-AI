interface LogoProps {
  size?: number;
  className?: string;
}

export function InstagramLogo({ size = 18, className }: LogoProps) {
  const gradientId = `ig-grad-${size}`;
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      style={{ flexShrink: 0 }}
    >
      <defs>
        <radialGradient id={gradientId} r="150%" cx="30%" cy="107%">
          <stop stopColor="#fdf497" offset="0%" />
          <stop stopColor="#fdf497" offset="5%" />
          <stop stopColor="#fd5949" offset="45%" />
          <stop stopColor="#d6249f" offset="60%" />
          <stop stopColor="#285AEB" offset="90%" />
        </radialGradient>
      </defs>
      <rect x="2" y="2" width="20" height="20" rx="5.5" fill={`url(#${gradientId})`} />
      <rect x="4.5" y="4.5" width="15" height="15" rx="3.8" stroke="#ffffff" strokeWidth="1.8" fill="none" />
      <circle cx="12" cy="12" r="3.7" stroke="#ffffff" strokeWidth="1.8" fill="none" />
      <circle cx="16.5" cy="7.5" r="1.15" fill="#ffffff" />
    </svg>
  );
}

export function LinkedInLogo({ size = 18, className }: LogoProps) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      style={{ flexShrink: 0 }}
    >
      <rect width="24" height="24" rx="4.5" fill="#0A66C2" />
      <path 
        d="M6.94 5.5a1.69 1.69 0 1 0 0 3.38 1.69 1.69 0 0 0 0-3.38zM3.94 9.94h3V20h-3V9.94zm5.12 0h2.88v1.38h.04c.4-.76 1.38-1.56 2.84-1.56 3.04 0 3.6 2 3.6 4.6V20h-3v-4.96c0-1.18-.02-2.7-1.64-2.7-1.65 0-1.9 1.28-1.9 2.6V20h-3V9.94z" 
        fill="#ffffff" 
      />
    </svg>
  );
}

export function YouTubeLogo({ size = 18, className }: LogoProps) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      style={{ flexShrink: 0 }}
    >
      <path 
        d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z" 
        fill="#FF0000" 
      />
      <polygon points="9.545 15.568 15.818 12 9.545 8.432 9.545 15.568" fill="#ffffff" />
    </svg>
  );
}

export function TikTokLogo({ size = 18, className }: LogoProps) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      style={{ flexShrink: 0 }}
    >
      <rect width="24" height="24" rx="5" fill="#010101" />
      <g transform="translate(1.5, 1.5)">
        <path d="M13.2 2.8v10.1a2.8 2.8 0 1 1-2.8-2.8c.35 0 .68.06.98.18V7.5a5.6 5.6 0 1 0 4.6 5.5V6.8a6.5 6.5 0 0 0 3.8 1.2V5.2a4.3 4.3 0 0 1-3.8-2.4H13.2z" fill="#25F4EE" />
        <path d="M14.2 3.8v10.1a2.8 2.8 0 1 1-2.8-2.8c.35 0 .68.06.98.18V8.5a5.6 5.6 0 1 0 4.6 5.5V7.8a6.5 6.5 0 0 0 3.8 1.2V6.2a4.3 4.3 0 0 1-3.8-2.4H14.2z" fill="#FE2C55" />
        <path d="M13.7 3.3v10.1a2.8 2.8 0 1 1-2.8-2.8c.35 0 .68.06.98.18V8a5.6 5.6 0 1 0 4.6 5.5V7.3a6.5 6.5 0 0 0 3.8 1.2V5.7a4.3 4.3 0 0 1-3.8-2.4H13.7z" fill="#ffffff" />
      </g>
    </svg>
  );
}

export function XLogo({ size = 18, className }: LogoProps) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      style={{ flexShrink: 0 }}
    >
      <rect width="24" height="24" rx="5" fill="#000000" />
      <path 
        d="M17.5 4.8h2.64l-5.77 6.6 6.79 8.98h-5.32l-4.16-5.45-4.77 5.45H4.23l6.17-7.05L3.89 4.8h5.45l3.76 4.97zm-.93 14h1.46L8.85 6.3H7.29z" 
        fill="#ffffff" 
      />
    </svg>
  );
}

export function FacebookLogo({ size = 18, className }: LogoProps) {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      className={className}
      style={{ flexShrink: 0 }}
    >
      <circle cx="12" cy="12" r="12" fill="#1877F2" />
      <path 
        d="M15.5 12h-2.5v7h-3v-7H8v-2.5h2V7.8C10 5.8 11.2 4.5 13.5 4.5c1.1 0 2 .1 2.3.1v2.5h-1.4c-1 0-1.2.5-1.2 1.2v1.2h2.7l-.4 2.5z" 
        fill="#ffffff" 
      />
    </svg>
  );
}

export function RealBrandLogo({ platform, size = 18, className }: { platform: string; size?: number; className?: string }) {
  const p = (platform || '').toUpperCase();
  if (p.includes('INSTA')) return <InstagramLogo size={size} className={className} />;
  if (p.includes('LINKED')) return <LinkedInLogo size={size} className={className} />;
  if (p.includes('YOUTUBE') || p.includes('SHORTS')) return <YouTubeLogo size={size} className={className} />;
  if (p.includes('TIKTOK')) return <TikTokLogo size={size} className={className} />;
  if (p.includes('FACEBOOK')) return <FacebookLogo size={size} className={className} />;
  if (p.includes('X') || p.includes('TWITTER')) return <XLogo size={size} className={className} />;

  // Default clean social icon
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="18" cy="5" r="3" />
      <circle cx="6" cy="12" r="3" />
      <circle cx="18" cy="19" r="3" />
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
      <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
    </svg>
  );
}

export interface PlatformMetadata {
  id: string;
  name: string;
  charLimit: number;
  bestTime: string;
  primaryColor: string;
  gradient: string;
  borderColor: string;
  accentBg: string;
}

export const PLATFORM_METAS: Record<string, PlatformMetadata> = {
  INSTAGRAM: {
    id: 'INSTAGRAM',
    name: 'Instagram',
    charLimit: 2200,
    bestTime: '11:00 AM & 6:00 PM',
    primaryColor: '#E1306C',
    gradient: 'linear-gradient(135deg, #833AB4, #FD1D1D, #FCAF45)',
    borderColor: 'rgba(225, 48, 108, 0.4)',
    accentBg: 'rgba(225, 48, 108, 0.12)',
  },
  LINKEDIN: {
    id: 'LINKEDIN',
    name: 'LinkedIn',
    charLimit: 3000,
    bestTime: '9:00 AM (Tue-Thu)',
    primaryColor: '#0A66C2',
    gradient: 'linear-gradient(135deg, #0A66C2, #0077B5)',
    borderColor: 'rgba(10, 102, 194, 0.4)',
    accentBg: 'rgba(10, 102, 194, 0.12)',
  },
  YOUTUBE: {
    id: 'YOUTUBE',
    name: 'YouTube',
    charLimit: 5000,
    bestTime: '3:00 PM - 5:00 PM',
    primaryColor: '#FF0000',
    gradient: 'linear-gradient(135deg, #FF0000, #CC0000)',
    borderColor: 'rgba(255, 0, 0, 0.4)',
    accentBg: 'rgba(255, 0, 0, 0.12)',
  },
  TIKTOK: {
    id: 'TIKTOK',
    name: 'TikTok',
    charLimit: 2200,
    bestTime: '7:00 PM - 9:00 PM',
    primaryColor: '#25F4EE',
    gradient: 'linear-gradient(135deg, #010101, #25F4EE 50%, #FE2C55)',
    borderColor: 'rgba(37, 244, 238, 0.4)',
    accentBg: 'rgba(37, 244, 238, 0.12)',
  },
  X: {
    id: 'X',
    name: 'X (Twitter)',
    charLimit: 280,
    bestTime: '12:00 PM & 5:00 PM',
    primaryColor: '#F8FAFC',
    gradient: 'linear-gradient(135deg, #1E293B, #0F172A)',
    borderColor: 'rgba(248, 250, 252, 0.3)',
    accentBg: 'rgba(255, 255, 255, 0.08)',
  },
};
