import { apiClient } from './client';
import { Project } from '../../types';

export interface ProjectCreate {
  name: string;
  description?: string;
  slug?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  slug?: string;
  is_active?: boolean;
}

export const projectService = {
  getProjects: async (workspaceId: string): Promise<Project[]> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/projects`);
    return response.data.data;
  },

  createProject: async (workspaceId: string, data: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post(`/workspaces/${workspaceId}/projects`, data);
    return response.data.data;
  },

  getProject: async (workspaceId: string, projectId: string): Promise<Project> => {
    const response = await apiClient.get(`/workspaces/${workspaceId}/projects/${projectId}`);
    return response.data.data;
  },

  updateProject: async (workspaceId: string, projectId: string, data: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.patch(`/workspaces/${workspaceId}/projects/${projectId}`, data);
    return response.data.data;
  },

  deleteProject: async (workspaceId: string, projectId: string): Promise<void> => {
    await apiClient.delete(`/workspaces/${workspaceId}/projects/${projectId}`);
  }
};
