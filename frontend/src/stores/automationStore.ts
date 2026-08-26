import { create } from 'zustand';
import { automationService, AutomationRule, AutomationRuleCreate } from '../services/api/automationService';

interface AutomationState {
  rules: AutomationRule[];
  isLoading: boolean;
  error: string | null;
  fetchRules: (workspaceId: string) => Promise<void>;
  createRule: (workspaceId: string, data: AutomationRuleCreate) => Promise<void>;
  deleteRule: (workspaceId: string, ruleId: string) => Promise<void>;
}

export const useAutomationStore = create<AutomationState>((set) => ({
  rules: [],
  isLoading: false,
  error: null,

  fetchRules: async (workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await automationService.getRules(workspaceId);
      set({ rules: data, isLoading: false });
    } catch (error: any) {
      set({ error: error.message || 'Failed to fetch automation rules', isLoading: false });
    }
  },

  createRule: async (workspaceId: string, data: AutomationRuleCreate) => {
    set({ isLoading: true, error: null });
    try {
      const newRule = await automationService.createRule(workspaceId, data);
      set((state) => ({ 
        rules: [newRule, ...state.rules],
        isLoading: false 
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to create automation rule', isLoading: false });
      throw error;
    }
  },

  deleteRule: async (workspaceId: string, ruleId: string) => {
    try {
      await automationService.deleteRule(workspaceId, ruleId);
      set((state) => ({
        rules: state.rules.filter(r => r.id !== ruleId)
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete rule' });
      throw error;
    }
  }
}));
