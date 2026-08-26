import { create } from 'zustand';
import { Workspace } from '../types';
import { apiClient } from '../services/api';

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  isLoading: boolean;
  error: string | null;
  
  fetchWorkspaces: () => Promise<void>;
  createWorkspace: (data: { name: string; slug: string; description?: string }) => Promise<void>;
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

  createWorkspace: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.post('/workspaces', data);
      if (response.data.success) {
        const newWorkspace: Workspace = response.data.data;
        const currentWorkspaces = get().workspaces;
        
        set({
          workspaces: [...currentWorkspaces, newWorkspace],
          activeWorkspace: newWorkspace,
          isLoading: false
        });
      } else {
        set({ error: response.data.message || 'Failed to create workspace', isLoading: false });
        throw new Error(response.data.message);
      }
    } catch (err: any) {
      const errMsg = err.response?.data?.error?.message || err.message || 'An error occurred creating the workspace';
      set({ error: errMsg, isLoading: false });
      throw new Error(errMsg);
    }
  },

  setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
  
  clearWorkspaces: () => set({ workspaces: [], activeWorkspace: null, error: null }),
}));
