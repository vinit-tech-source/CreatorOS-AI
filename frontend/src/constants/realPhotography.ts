export interface RealStockPhoto {
  id: string;
  title: string;
  category: 'Tech' | 'Creator' | 'Business' | 'Lifestyle';
  url: string;
  thumbUrl: string;
}

export const REAL_STOCK_PHOTOS: RealStockPhoto[] = [
  // Tech & Startups
  {
    id: 'tech-workspace',
    title: 'Developer Modern Workspace',
    category: 'Tech',
    url: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=240&auto=format&fit=crop&q=70',
  },
  {
    id: 'tech-coding',
    title: 'Clean Code in Dark Room',
    category: 'Tech',
    url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=240&auto=format&fit=crop&q=70',
  },
  {
    id: 'tech-analytics',
    title: 'Growth Analytics Dashboard',
    category: 'Tech',
    url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=240&auto=format&fit=crop&q=70',
  },

  // Creator & Studio
  {
    id: 'creator-mic',
    title: 'Studio Podcast Shure SM7B',
    category: 'Creator',
    url: 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=240&auto=format&fit=crop&q=70',
  },
  {
    id: 'creator-camera',
    title: 'Professional Cinema Camera Setup',
    category: 'Creator',
    url: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=240&auto=format&fit=crop&q=70',
  },
  {
    id: 'creator-desk',
    title: 'Minimal Creator Desk & Ambient Light',
    category: 'Creator',
    url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=240&auto=format&fit=crop&q=70',
  },

  // Business & Strategy
  {
    id: 'biz-team',
    title: 'Executive Team Brainstorming',
    category: 'Business',
    url: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=240&auto=format&fit=crop&q=70',
  },
  {
    id: 'biz-arch',
    title: 'Modern High-Rise Glass Architecture',
    category: 'Business',
    url: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=240&auto=format&fit=crop&q=70',
  },

  // Lifestyle & Minimal
  {
    id: 'life-minimal',
    title: 'Architectural Shadows & Clean Lines',
    category: 'Lifestyle',
    url: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=240&auto=format&fit=crop&q=70',
  },
  {
    id: 'life-urban',
    title: 'Downtown Tokyo Neon Skyline',
    category: 'Lifestyle',
    url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=1200&auto=format&fit=crop&q=80',
    thumbUrl: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=240&auto=format&fit=crop&q=70',
  },
];
