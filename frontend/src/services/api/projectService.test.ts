import { describe, it, expect, vi, beforeEach } from 'vitest';
import { projectService } from './projectService';
import { apiClient } from './client';

vi.mock('./client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('projectService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getProjects should fetch projects for a workspace', async () => {
    const mockProjects = [
      { id: '1', name: 'Proj 1', slug: 'proj-1', status: 'DRAFT', is_active: true }
    ];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { data: mockProjects } });

    const result = await projectService.getProjects('ws-123');

    expect(apiClient.get).toHaveBeenCalledWith('/workspaces/ws-123/projects');
    expect(result).toEqual(mockProjects);
  });

  it('createProject should post payload and return created project', async () => {
    const mockPayload = { name: 'New Proj', slug: 'new-proj', status: 'DRAFT' };
    const mockCreated = { id: '2', ...mockPayload, is_active: true };
    
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { data: mockCreated } });

    const result = await projectService.createProject('ws-123', mockPayload);

    expect(apiClient.post).toHaveBeenCalledWith('/workspaces/ws-123/projects', mockPayload);
    expect(result).toEqual(mockCreated);
  });
});
