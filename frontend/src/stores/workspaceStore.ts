import { create } from 'zustand';
import { Workspace } from '../types';
import { apiClient } from '../services/api';

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  isLoading: boolean;
  error: string | null;
  
  fetchWorkspaces: () => Promise<void>;
  setActiveWorkspace: (workspace: Workspace | null) => void;
  clearWorkspaces: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  workspaces: [],
  activeWorkspace: null,
  isLoading: false,
  error: null,

  fetchWorkspaces: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.get('/workspaces');
      if (response.data.success) {
        const workspaces: Workspace[] = response.data.data;
        const currentActive = get().activeWorkspace;
        
        // If we don't have an active workspace, or the active workspace is no longer in the list, set it to the first one
        let newActive = currentActive;
        if (!currentActive && workspaces.length > 0) {
          newActive = workspaces[0];
        } else if (currentActive && workspaces.length > 0) {
          const stillExists = workspaces.find(w => w.id === currentActive.id);
          if (!stillExists) {
            newActive = workspaces[0];
          }
        }
        
        set({ 
          workspaces, 
          activeWorkspace: newActive,
          isLoading: false 
        });
      } else {
        set({ error: response.data.message || 'Failed to fetch workspaces', isLoading: false });
      }
    } catch (err: any) {
      set({ 
        error: err.response?.data?.error?.message || err.message || 'An error occurred fetching workspaces', 
        isLoading: false 
      });
    }
  },

  setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
  
  clearWorkspaces: () => set({ workspaces: [], activeWorkspace: null, error: null }),
}));
