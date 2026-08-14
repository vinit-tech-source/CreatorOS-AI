/**
 * socialAccountService.ts
 *
 * Typed API wrapper for Social Account endpoints.
 *
 * SECURITY:
 *  - No token, secret, or encrypted field is ever sent or received here.
 *  - OAuth initiation returns only `authorization_url` and `state_token`.
 *  - The backend is fully responsible for CSRF, code exchange, and token storage.
 */
import { apiClient } from './client';
import { SocialAccount, OAuthAuthorizationResponse, ApiResponse } from '../../types';

export const socialAccountService = {
  /**
   * Fetch all social accounts connected to a workspace.
   * Clears and replaces — never merges — so stale state cannot leak across workspaces.
   */
  listSocialAccounts: async (workspaceId: string): Promise<SocialAccount[]> => {
    const response = await apiClient.get<ApiResponse<SocialAccount[]>>(
      `/workspaces/${workspaceId}/social-accounts`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to load social accounts.');
  },

  /**
   * Disconnect (permanently delete) a social account from a workspace.
   * Frontend never touches any token; the backend handles revocation.
   */
  disconnectSocialAccount: async (workspaceId: string, accountId: string): Promise<void> => {
    const response = await apiClient.delete<ApiResponse<null>>(
      `/workspaces/${workspaceId}/social-accounts/${accountId}`
    );
    if (!response.data.success) {
      throw new Error(response.data.error?.message || 'Failed to disconnect account.');
    }
  },

  /**
   * Initiate the OAuth connection flow for a given platform.
   *
   * Returns `{ authorization_url, state_token }`.
   * The caller must redirect the browser to `authorization_url`.
   * The backend owns CSRF, state validation, code exchange, and token persistence.
   *
   * @param workspaceId - The workspace to associate the new account with.
   * @param platform    - Platform identifier (e.g. "bluesky").
   * @param redirectUri - The frontend callback URL that the provider will redirect back to.
   */
  initiateOAuthConnect: async (
    workspaceId: string,
    platform: string,
    redirectUri: string
  ): Promise<OAuthAuthorizationResponse> => {
    const response = await apiClient.get<OAuthAuthorizationResponse>(
      `/oauth/workspaces/${workspaceId}/social-accounts/${platform}/connect`,
      { params: { redirect_uri: redirectUri } }
    );
    // OAuth connect endpoint returns the schema directly (not wrapped in ApiResponse)
    if (!response.data.authorization_url) {
      throw new Error('OAuth connect endpoint did not return an authorization URL.');
    }
    return response.data;
  },
};
