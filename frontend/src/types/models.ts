export interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  avatar_url?: string;
  region?: string | null;
  country?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface BrandKit {
  id: string;
  workspace_id: string;
  name: string;
  primary_color?: string;
  secondary_color?: string;
  font_family?: string;
  logo_url?: string;
  voice_tone?: string;
  created_at: string;
  updated_at: string;
}

export interface SocialAccount {
  id: string;
  workspace_id: string;
  /** Social media platform identifier */
  platform: 'X' | 'LINKEDIN' | 'INSTAGRAM' | 'FACEBOOK' | 'BLUESKY';
  /** Platform-assigned user identifier (e.g. DID for Bluesky) */
  platform_user_id: string;
  /** Display name for the connected account */
  account_name: string;
  /** UTC timestamp when access token expires; null means no expiry info */
  token_expires_at: string | null;
  /** Space-separated OAuth scopes granted */
  scopes: string | null;
  /** Whether this account connection is currently active */
  is_active: boolean;
  /** When this account was first connected */
  connected_at: string;
  updated_at: string;
}

/** Response returned by the OAuth connect initiation endpoint */
export interface OAuthAuthorizationResponse {
  authorization_url: string;
  state_token: string;
}

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Post {
  id: string;
  project_id: string;
  title?: string;
  content: string;
  platform: string;
  status: 'DRAFT' | 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED' | 'SCHEDULED' | 'PUBLISHED';
  rejection_reason?: string;
  scheduled_for?: string;
  published_at?: string;
  external_post_id?: string;
  post_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AnalyticsSnapshot {
  impressions?: number;
  views?: number;
  likes?: number;
  comments?: number;
  shares?: number;
  saves?: number;
  clicks?: number;
  followers_at_time?: number;
  engagement_rate?: number;
}

export interface PostAnalyticsResponse extends AnalyticsSnapshot {
  id: string;
  post_id: string;
  workspace_id: string;
  social_account_id: string;
  platform: string;
  external_post_id: string;
  collected_at: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_impressions: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_saves: number;
  total_clicks: number;
  average_engagement_rate: number;
  post_count: number;
}
