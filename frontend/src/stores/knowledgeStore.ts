import { create } from 'zustand';
import { knowledgeService, KnowledgeSource, KnowledgeSourceCreate } from '../services/api/knowledgeService';

interface KnowledgeState {
  sources: KnowledgeSource[];
  isLoading: boolean;
  error: string | null;
  fetchSources: (workspaceId: string) => Promise<void>;
  createSource: (workspaceId: string, data: KnowledgeSourceCreate) => Promise<void>;
  deleteSource: (workspaceId: string, sourceId: string) => Promise<void>;
}

export const useKnowledgeStore = create<KnowledgeState>((set) => ({
  sources: [],
  isLoading: false,
  error: null,

  fetchSources: async (workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await knowledgeService.getSources(workspaceId);
      set({ sources: data, isLoading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch knowledge sources', isLoading: false });
    }
  },

  createSource: async (workspaceId: string, data: KnowledgeSourceCreate) => {
    set({ isLoading: true, error: null });
    try {
      const newSource = await knowledgeService.createSource(workspaceId, data);
      set((state) => ({ 
        sources: [newSource, ...state.sources],
        isLoading: false 
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to create knowledge source', isLoading: false });
      throw error;
    }
  },

  deleteSource: async (workspaceId: string, sourceId: string) => {
    try {
      await knowledgeService.deleteSource(workspaceId, sourceId);
      set((state) => ({
        sources: state.sources.filter(s => s.id !== sourceId)
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete knowledge source' });
      throw error;
    }
  }
}));
