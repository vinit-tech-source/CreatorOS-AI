import { apiClient } from './client';

export interface AutomationRule {
  id: string;
  workspace_id: string;
  name: string;
  trigger_type: string;
  condition: string | null;
  action_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AutomationRuleCreate {
  name: string;
  trigger_type: string;
  condition?: string | null;
  action_type: string;
  is_active: boolean;
}

export const automationService = {
  getRules: async (workspaceId: string): Promise<AutomationRule[]> => {
    const response = await apiClient.get<{ data: AutomationRule[] }>(`/workspaces/${workspaceId}/automations`);
    return response.data.data;
  },

  createRule: async (workspaceId: string, data: AutomationRuleCreate): Promise<AutomationRule> => {
    const response = await apiClient.post<{ data: AutomationRule }>(`/workspaces/${workspaceId}/automations`, data);
    return response.data.data;
  },

  deleteRule: async (workspaceId: string, ruleId: string): Promise<void> => {
    await apiClient.delete(`/workspaces/${workspaceId}/automations/${ruleId}`);
  }
};
