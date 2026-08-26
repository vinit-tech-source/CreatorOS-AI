import { apiClient } from './client';

export interface KnowledgeSource {
  id: string;
  workspace_id: string;
  name: string;
  source_type: 'TEXT' | 'URL' | 'PDF';
  content: string;
  status: 'PENDING' | 'PROCESSED' | 'FAILED';
  created_at: string;
  updated_at: string;
}

export interface KnowledgeSourceCreate {
  name: string;
  source_type: 'TEXT' | 'URL' | 'PDF';
  content: string;
}

export const knowledgeService = {
  getSources: async (workspaceId: string): Promise<KnowledgeSource[]> => {
    const response = await apiClient.get<{ data: KnowledgeSource[] }>(`/workspaces/${workspaceId}/knowledge`);
    return response.data.data;
  },

  createSource: async (workspaceId: string, data: KnowledgeSourceCreate): Promise<KnowledgeSource> => {
    const response = await apiClient.post<{ data: KnowledgeSource }>(`/workspaces/${workspaceId}/knowledge`, data);
    return response.data.data;
  },

  deleteSource: async (workspaceId: string, sourceId: string): Promise<void> => {
    await apiClient.delete(`/workspaces/${workspaceId}/knowledge/${sourceId}`);
  }
};
