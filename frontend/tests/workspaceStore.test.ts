import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useWorkspaceStore } from '../src/stores/workspaceStore';
import { apiClient } from '../src/services/api';

vi.mock('../src/services/api', () => ({
  apiClient: {
    get: vi.fn()
  }
}));

describe('Workspace Store', () => {
  beforeEach(() => {
    useWorkspaceStore.setState({
      workspaces: [],
      activeWorkspace: null,
      isLoading: false,
      error: null,
    });
    vi.clearAllMocks();
  });

  it('should initialize with default values', () => {
    const state = useWorkspaceStore.getState();
    expect(state.workspaces).toEqual([]);
    expect(state.activeWorkspace).toBeNull();
  });

  it('should fetch workspaces and set active workspace', async () => {
    const mockWorkspaces = [
      { id: '1', name: 'Workspace 1', slug: 'ws-1' },
      { id: '2', name: 'Workspace 2', slug: 'ws-2' }
    ];
    
    (apiClient.get as any).mockResolvedValue({
      data: { success: true, data: mockWorkspaces }
    });

    await useWorkspaceStore.getState().fetchWorkspaces();
    
    const state = useWorkspaceStore.getState();
    expect(state.workspaces).toEqual(mockWorkspaces);
    expect(state.activeWorkspace).toEqual(mockWorkspaces[0]);
    expect(state.isLoading).toBe(false);
  });

  it('should handle fetch errors', async () => {
    (apiClient.get as any).mockRejectedValue(new Error('Network error'));

    await useWorkspaceStore.getState().fetchWorkspaces();
    
    const state = useWorkspaceStore.getState();
    expect(state.workspaces).toEqual([]);
    expect(state.error).toBe('Network error');
    expect(state.isLoading).toBe(false);
  });
});
