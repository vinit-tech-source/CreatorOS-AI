// Platform config: content formats per platform, with metadata
export interface ContentFormat {
  id: string;
  label: string;
  icon: string;
  aspectRatio: string; // e.g., "9:16", "1:1", "16:9"
  canvasW: number; // px representation
  canvasH: number;
  charLimit: number;
  titleLimit?: number;
  descLimit?: number;
  maxHashtags?: number;
  supportsMedia: boolean;
  supportsText: boolean;
  supportsCarousel: boolean;
  description: string;
}

export interface PlatformConfig {
  id: string;
  name: string;
  color: string;
  gradient: string;
  formats: ContentFormat[];
  primaryFont: string;
  accentColor: string;
}

export const platformDomains: Record<string, string> = {
  'X / Twitter': 'x.com',
  'twitter': 'x.com',
  'x': 'x.com',
  'LinkedIn': 'linkedin.com',
  'Instagram': 'instagram.com',
  'Facebook': 'facebook.com',
  'TikTok': 'tiktok.com',
  'YouTube': 'youtube.com',
  'Threads': 'threads.net',
  'Bluesky': 'bsky.app',
  'WhatsApp': 'whatsapp.com',
  'Snapchat': 'snapchat.com',
  'Telegram': 'telegram.org',
  'ShareChat': 'sharechat.com',
  'Moj': 'mojapp.in',
  'Josh': 'myjosh.in',
  'Discord': 'discord.com',
  'Reddit': 'reddit.com',
  'Pinterest': 'pinterest.com',
  'WeChat': 'wechat.com',
  'Douyin': 'douyin.com',
  'Xiaohongshu': 'xiaohongshu.com',
  'Kuaishou': 'kuaishou.com',
  'Weibo': 'weibo.com',
  'Bilibili': 'bilibili.com',
  'QQ': 'qq.com',
  'Zhihu': 'zhihu.com',
  'Baidu Tieba': 'tieba.baidu.com',
  'Douban': 'douban.com',
  'Kwai': 'kwai.com',
  'VK': 'vk.com',
  'Odnoklassniki': 'ok.ru',
  'Rutube': 'rutube.ru',
  'Dzen': 'dzen.ru',
  'Pikabu': 'pikabu.ru',
  'LINE': 'line.me',
  'Niconico': 'nicovideo.jp',
  'Pixiv': 'pixiv.net',
  'Messenger': 'messenger.com',
  'Zalo': 'zalo.me',
  'KakaoTalk': 'kakaocorp.com',
  'Naver': 'naver.com',
  'BAND': 'band.us',
  'SOOP': 'sooplive.co.kr',
  'Dcard': 'dcard.tw',
  'Viber': 'viber.com'
};

export function getPlatformLogoUrl(name: string): string {
  if (!name) return 'https://icon.horse/icon/creatoros.com';
  const domain = platformDomains[name] || platformDomains[Object.keys(platformDomains).find(k => name.toLowerCase().includes(k.toLowerCase())) || ''] || 'creatoros.com';
  return `https://icon.horse/icon/${domain}`;
}

const FeedPost: ContentFormat = {
  id: 'feed-post',
  label: 'Feed Post',
  icon: '🖼️',
  aspectRatio: '1:1',
  canvasW: 480,
  canvasH: 480,
  charLimit: 2200,
  maxHashtags: 30,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Standard square post for the Instagram feed.',
};

const Story: ContentFormat = {
  id: 'story',
  label: 'Story',
  icon: '⬆️',
  aspectRatio: '9:16',
  canvasW: 270,
  canvasH: 480,
  charLimit: 250,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Full-screen vertical story that disappears in 24h.',
};

const Reel: ContentFormat = {
  id: 'reel',
  label: 'Reel',
  icon: '🎬',
  aspectRatio: '9:16',
  canvasW: 270,
  canvasH: 480,
  charLimit: 2200,
  maxHashtags: 30,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Short vertical video designed for maximum reach.',
};

const Carousel: ContentFormat = {
  id: 'carousel',
  label: 'Carousel',
  icon: '🎠',
  aspectRatio: '1:1',
  canvasW: 480,
  canvasH: 480,
  charLimit: 2200,
  maxHashtags: 30,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: true,
  description: 'Swipeable multi-image or video post.',
};

const Tweet: ContentFormat = {
  id: 'tweet',
  label: 'Post',
  icon: '💬',
  aspectRatio: '16:9',
  canvasW: 480,
  canvasH: 270,
  charLimit: 280,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'A standard post on X (up to 280 characters).',
};

const Thread: ContentFormat = {
  id: 'thread',
  label: 'Thread',
  icon: '🧵',
  aspectRatio: '16:9',
  canvasW: 480,
  canvasH: 270,
  charLimit: 280,
  supportsMedia: false,
  supportsText: true,
  supportsCarousel: false,
  description: 'A series of connected posts for storytelling.',
};

const LinkedInPost: ContentFormat = {
  id: 'linkedin-post',
  label: 'Post',
  icon: '📝',
  aspectRatio: '1.91:1',
  canvasW: 480,
  canvasH: 252,
  charLimit: 3000,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Professional post visible to your LinkedIn network.',
};

const Article: ContentFormat = {
  id: 'article',
  label: 'Article',
  icon: '📰',
  aspectRatio: '16:9',
  canvasW: 480,
  canvasH: 270,
  charLimit: 120000,
  titleLimit: 150,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Long-form professional content with a cover image.',
};

const TikTokVideo: ContentFormat = {
  id: 'tiktok-video',
  label: 'Video',
  icon: '🎵',
  aspectRatio: '9:16',
  canvasW: 270,
  canvasH: 480,
  charLimit: 2200,
  maxHashtags: 100,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Short-form vertical video for the TikTok For You Page.',
};

const YTVideo: ContentFormat = {
  id: 'yt-video',
  label: 'Video',
  icon: '▶️',
  aspectRatio: '16:9',
  canvasW: 480,
  canvasH: 270,
  charLimit: 5000,
  titleLimit: 100,
  descLimit: 5000,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Long-form or short video for YouTube.',
};

const YTShort: ContentFormat = {
  id: 'yt-short',
  label: 'Short',
  icon: '⚡',
  aspectRatio: '9:16',
  canvasW: 270,
  canvasH: 480,
  charLimit: 100,
  titleLimit: 100,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Vertical short video (< 60s) for the Shorts feed.',
};

const YTThumbnail: ContentFormat = {
  id: 'yt-thumbnail',
  label: 'Thumbnail',
  icon: '🖼️',
  aspectRatio: '16:9',
  canvasW: 480,
  canvasH: 270,
  charLimit: 0,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Eye-catching custom thumbnail for your video.',
};

const FacebookPost: ContentFormat = {
  id: 'fb-post',
  label: 'Post',
  icon: '📣',
  aspectRatio: '1.91:1',
  canvasW: 480,
  canvasH: 252,
  charLimit: 63206,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Standard Facebook feed post.',
};

const FBStory: ContentFormat = {
  id: 'fb-story',
  label: 'Story',
  icon: '⬆️',
  aspectRatio: '9:16',
  canvasW: 270,
  canvasH: 480,
  charLimit: 500,
  supportsMedia: true,
  supportsText: true,
  supportsCarousel: false,
  description: 'Full-screen vertical story.',
};

export const platformConfigs: Record<string, PlatformConfig> = {
  'X / Twitter': {
    id: 'twitter',
    name: 'X (Twitter)',
    color: '#000000',
    gradient: 'linear-gradient(135deg, #000000, #222222)',
    accentColor: '#1d9bf0',
    primaryFont: 'Inter',
    formats: [Tweet, Thread, Story],
  },
  'Instagram': {
    id: 'instagram',
    name: 'Instagram',
    color: '#E1306C',
    gradient: 'linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045)',
    accentColor: '#E1306C',
    primaryFont: 'Inter',
    formats: [FeedPost, Story, Reel, Carousel],
  },
  'LinkedIn': {
    id: 'linkedin',
    name: 'LinkedIn',
    color: '#0A66C2',
    gradient: 'linear-gradient(135deg, #0a66c2, #0077b5)',
    accentColor: '#0A66C2',
    primaryFont: 'Inter',
    formats: [LinkedInPost, Article, Carousel],
  },
  'TikTok': {
    id: 'tiktok',
    name: 'TikTok',
    color: '#010101',
    gradient: 'linear-gradient(135deg, #010101, #fe2c55)',
    accentColor: '#fe2c55',
    primaryFont: 'Inter',
    formats: [TikTokVideo, Story],
  },
  'YouTube': {
    id: 'youtube',
    name: 'YouTube',
    color: '#FF0000',
    gradient: 'linear-gradient(135deg, #282828, #FF0000)',
    accentColor: '#FF0000',
    primaryFont: 'Inter',
    formats: [YTVideo, YTShort, YTThumbnail],
  },
  'Facebook': {
    id: 'facebook',
    name: 'Facebook',
    color: '#1877F2',
    gradient: 'linear-gradient(135deg, #1877F2, #0d47a1)',
    accentColor: '#1877F2',
    primaryFont: 'Inter',
    formats: [FacebookPost, FBStory, Carousel],
  },
};

export function getPlatformConfig(platformName: string): PlatformConfig | null {
  return platformConfigs[platformName] || null;
}
