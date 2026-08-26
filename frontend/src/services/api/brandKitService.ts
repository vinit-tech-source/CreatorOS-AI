import { apiClient } from './client';
import { BrandKit } from '../../types';

export interface BrandKitCreate {
  name: string;
  primary_color?: string;
  secondary_color?: string;
  font_family?: string;
  logo_url?: string;
  voice_tone?: string;
}

export interface BrandKitUpdate {
  name?: string;
  primary_color?: string | null;
  secondary_color?: string | null;
  font_family?: string | null;
  logo_url?: string | null;
  voice_tone?: string | null;
}

export const brandKitService = {
  getBrandKit: async (workspaceId: string): Promise<BrandKit | null> => {
    try {
      const response = await apiClient.get(`/workspaces/${workspaceId}/brand-kit`);
      return response.data.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  createBrandKit: async (workspaceId: string, data: BrandKitCreate): Promise<BrandKit> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/brand-kit`, data);
    return response.data.data;
  },

  updateBrandKit: async (workspaceId: string, data: BrandKitUpdate): Promise<BrandKit> => {
    const response = await apiClient.patch(`/workspaces/${workspaceId}/brand-kit`, data);
    return response.data.data;
  },

  deleteBrandKit: async (workspaceId: string): Promise<void> => {
    await apiClient.delete(`/workspaces/${workspaceId}/brand-kit`);
  }
};
