/**
 * socialAccountStore.ts
 *
 * Zustand store for Social Account state management.
 *
 * Workspace isolation guarantee:
 *   - Every call to `fetchAccounts` clears existing accounts BEFORE fetching,
 *     so stale accounts from a previous workspace can never appear.
 *   - `clearAccounts` is also exposed for explicit teardown on workspace change.
 *
 * SECURITY:
 *   - This store never holds or exposes any OAuth token, refresh token, or secret.
 *   - Token handling is entirely server-side.
 */
import { create } from 'zustand';
import { SocialAccount } from '../types';
import { socialAccountService } from '../services/api/socialAccountService';

interface SocialAccountState {
  accounts: SocialAccount[];
  isLoading: boolean;
  error: string | null;
  /** The workspaceId for which accounts are currently loaded (used for stale-check) */
  loadedWorkspaceId: string | null;

  /** Fetch accounts for a workspace; clears stale state immediately */
  fetchAccounts: (workspaceId: string) => Promise<void>;
  /** Disconnect an account by ID and refresh the list */
  disconnectAccount: (workspaceId: string, accountId: string) => Promise<void>;
  /** Clear all account state (call on workspace change / logout) */
  clearAccounts: () => void;
}

export const useSocialAccountStore = create<SocialAccountState>((set, get) => ({
  accounts: [],
  isLoading: false,
  error: null,
  loadedWorkspaceId: null,

  fetchAccounts: async (workspaceId: string) => {
    // Clear stale data immediately so the previous workspace's accounts never flash
    set({ accounts: [], isLoading: true, error: null, loadedWorkspaceId: null });
    try {
      const accounts = await socialAccountService.listSocialAccounts(workspaceId);
      set({ accounts, isLoading: false, loadedWorkspaceId: workspaceId });
    } catch (err: any) {
      const message =
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to load social accounts. Please try again.';
      set({ error: message, isLoading: false });
    }
  },

  disconnectAccount: async (workspaceId: string, accountId: string) => {
    try {
      await socialAccountService.disconnectSocialAccount(workspaceId, accountId);
      // Wait for success, then we don't necessarily need to remove it here if the page calls `loadAccounts()` 
      // but let's remove it from the store to be safe and consistent.
      const previous = get().accounts;
      set({ accounts: previous.filter(a => a.id !== accountId), error: null });
    } catch (err: any) {
      throw err;
    }
  },

  clearAccounts: () =>
    set({ accounts: [], isLoading: false, error: null, loadedWorkspaceId: null }),
}));
