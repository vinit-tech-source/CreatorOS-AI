import { apiClient } from './client';
import { BrandKit } from '../../types';

export interface BrandKitCreate {
  brand_name?: string;
  name?: string;
  description?: string;
  website_url?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  font_family?: string;
  default_tone?: string;
  voice_tone?: string;
  target_audience?: string;
  brand_values?: string;
  preferred_language?: string;
}

export interface BrandKitUpdate {
  brand_name?: string;
  name?: string;
  description?: string | null;
  website_url?: string | null;
  logo_url?: string | null;
  primary_color?: string | null;
  secondary_color?: string | null;
  accent_color?: string | null;
  font_family?: string | null;
  default_tone?: string | null;
  voice_tone?: string | null;
  target_audience?: string | null;
  brand_values?: string | null;
  preferred_language?: string | null;
}

const normalizePayload = (data: BrandKitCreate | BrandKitUpdate) => {
  const brand_name = data.brand_name || data.name || 'My Brand';
  const default_tone = data.default_tone || data.voice_tone || undefined;

  const sanitizeHex = (color?: string | null) => {
    if (!color) return undefined;
    const clean = color.trim();
    if (/^#[0-9A-Fa-f]{6}$/.test(clean)) return clean.toUpperCase();
    return undefined;
  };

  const payload: any = {
    brand_name,
    ...(data.description !== undefined && { description: data.description || null }),
    ...(data.website_url !== undefined && { website_url: data.website_url || null }),
    ...(data.logo_url !== undefined && { logo_url: data.logo_url || null }),
    ...(data.primary_color !== undefined && { primary_color: sanitizeHex(data.primary_color) || null }),
    ...(data.secondary_color !== undefined && { secondary_color: sanitizeHex(data.secondary_color) || null }),
    ...(data.accent_color !== undefined && { accent_color: sanitizeHex(data.accent_color) || null }),
    ...(default_tone !== undefined && { default_tone: default_tone || null }),
    ...(data.target_audience !== undefined && { target_audience: data.target_audience || null }),
    ...(data.brand_values !== undefined && { brand_values: data.brand_values || null }),
    ...(data.preferred_language !== undefined && { preferred_language: data.preferred_language || 'en' }),
  };

  return payload;
};

export const brandKitService = {
  getBrandKit: async (workspaceId: string): Promise<BrandKit | null> => {
    try {
      const response = await apiClient.get(`/workspaces/${workspaceId}/brand-kit`);
      const item = response.data.data;
      if (!item) return null;
      // Guarantee both brand_name and name are set
      return {
        ...item,
        name: item.brand_name || item.name,
        voice_tone: item.default_tone || item.voice_tone,
      };
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  createBrandKit: async (workspaceId: string, data: BrandKitCreate): Promise<BrandKit> => {
    const payload = normalizePayload(data);
    const response = await apiClient.post(`/workspaces/${workspaceId}/brand-kit`, payload);
    const item = response.data.data;
    return {
      ...item,
      name: item.brand_name || item.name,
      voice_tone: item.default_tone || item.voice_tone,
    };
  },

  updateBrandKit: async (workspaceId: string, data: BrandKitUpdate): Promise<BrandKit> => {
    const payload = normalizePayload(data);
    const response = await apiClient.patch(`/workspaces/${workspaceId}/brand-kit`, payload);
    const item = response.data.data;
    return {
      ...item,
      name: item.brand_name || item.name,
      voice_tone: item.default_tone || item.voice_tone,
    };
  },

  deleteBrandKit: async (workspaceId: string): Promise<void> => {
    await apiClient.delete(`/workspaces/${workspaceId}/brand-kit`);
  }
};
