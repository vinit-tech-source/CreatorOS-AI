import { create } from 'zustand';
import { BrandKit } from '../types';
import { brandKitService, BrandKitCreate, BrandKitUpdate } from '../services/api/brandKitService';

interface BrandKitState {
  brandKit: BrandKit | null;
  isLoading: boolean;
  error: string | null;
  isSaving: boolean;
  
  fetchBrandKit: (workspaceId: string) => Promise<void>;
  saveBrandKit: (workspaceId: string, data: BrandKitUpdate | BrandKitCreate) => Promise<void>;
  clearBrandKit: () => void;
}

export const useBrandKitStore = create<BrandKitState>((set, get) => ({
  brandKit: null,
  isLoading: false,
  error: null,
  isSaving: false,

  fetchBrandKit: async (workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const brandKit = await brandKitService.getBrandKit(workspaceId);
      set({ brandKit, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.error?.message || 'Failed to fetch Brand Kit', 
        isLoading: false 
      });
    }
  },

  saveBrandKit: async (workspaceId: string, data: BrandKitUpdate | BrandKitCreate) => {
    set({ isSaving: true, error: null });
    try {
      const currentBrandKit = get().brandKit;
      let updatedBrandKit: BrandKit;

      if (currentBrandKit) {
        // Update existing
        updatedBrandKit = await brandKitService.updateBrandKit(workspaceId, data as BrandKitUpdate);
      } else {
        // Create new
        updatedBrandKit = await brandKitService.createBrandKit(workspaceId, data as BrandKitCreate);
      }
      set({ brandKit: updatedBrandKit, isSaving: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.error?.message || 'Failed to save Brand Kit', 
        isSaving: false 
      });
      throw error;
    }
  },

  clearBrandKit: () => {
    set({ brandKit: null, error: null });
  }
}));
