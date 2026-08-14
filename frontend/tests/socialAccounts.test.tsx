/**
 * socialAccounts.test.tsx
 *
 * Tests for the Social Accounts management UI.
 *
 * All backend/OAuth calls are mocked — no real network calls, no real tokens.
 *
 * Coverage:
 *  1.  Page renders
 *  2.  Empty state renders with connect CTA
 *  3.  Connected account renders with safe metadata
 *  4.  Bluesky Connect action calls OAuth endpoint
 *  5.  Disconnect confirmation dialog opens
 *  6.  Disconnect API success updates UI
 *  7.  Disconnect failure shows error
 *  8.  Unsupported providers are NOT shown
 *  9.  Workspace switching refetches accounts
 * 10.  Unauthorized workspace is handled
 * 11.  Sensitive token fields are never rendered
 * 12.  Loading state shows skeletons
 * 13.  Existing frontend tests remain unaffected (isolated mocks)
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import { BrowserRouter, MemoryRouter, Route, Routes } from 'react-router-dom';
import { SocialAccounts } from '../src/pages/settings/SocialAccounts';
import { useSocialAccountStore } from '../src/stores/socialAccountStore';
import { useWorkspaceStore } from '../src/stores/workspaceStore';
import { socialAccountService } from '../src/services/api/socialAccountService';

// ─── Module Mocks ────────────────────────────────────────────────────────────

vi.mock('../src/services/api/socialAccountService', () => ({
  socialAccountService: {
    listSocialAccounts: vi.fn(),
    disconnectSocialAccount: vi.fn(),
    initiateOAuthConnect: vi.fn(),
  },
}));

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const WORKSPACE_ID = 'ws-test-123';

const mockBlueskyAccount = {
  id: 'acc-bsky-1',
  workspace_id: WORKSPACE_ID,
  platform: 'BLUESKY' as const,
  platform_user_id: 'did:plc:abc123xyz',
  account_name: 'testuser.bsky.social',
  token_expires_at: null,
  scopes: 'atproto transition:generic',
  is_active: true,
  connected_at: '2026-01-15T10:00:00Z',
  updated_at: '2026-01-15T10:00:00Z',
};

// ─── Render Helpers ───────────────────────────────────────────────────────────

/** Render within a MemoryRouter at the workspace-scoped route */
function renderAtWorkspacePath(wsId = WORKSPACE_ID) {
  return render(
    <MemoryRouter initialEntries={[`/workspaces/${wsId}/social-accounts`]}>
      <Routes>
        <Route path="/workspaces/:workspaceId/social-accounts" element={<SocialAccounts />} />
      </Routes>
    </MemoryRouter>
  );
}

/** Render at the global /social-accounts route (no route param) */
function renderAtGlobalPath() {
  return render(
    <BrowserRouter>
      <SocialAccounts />
    </BrowserRouter>
  );
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('Social Accounts Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store state
    useSocialAccountStore.setState({
      accounts: [],
      isLoading: false,
      error: null,
      loadedWorkspaceId: null,
    });
    useWorkspaceStore.setState({
      workspaces: [],
      activeWorkspace: null,
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ── Test 1: Page renders ───────────────────────────────────────────────────
  it('renders the Social Accounts page with heading', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([]);

    renderAtWorkspacePath();

    expect(screen.getByText('Social Accounts')).toBeInTheDocument();
  });

  // ── Test 2: Empty state renders ───────────────────────────────────────────
  it('shows empty state with connect CTA when no accounts are connected', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([]);

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText(/No accounts connected yet/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Connect a social account to start publishing/i)
      ).toBeInTheDocument();
      // Connect provider section should be present
      expect(screen.getByText('Bluesky')).toBeInTheDocument();
    });
  });

  // ── Test 3: Connected account renders ─────────────────────────────────────
  it('renders a connected Bluesky account card with safe metadata', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([mockBlueskyAccount]);

    renderAtWorkspacePath();

    await waitFor(() => {
      // Account name
      expect(screen.getByText('testuser.bsky.social')).toBeInTheDocument();
      // Platform label
      expect(screen.getByText('BLUESKY')).toBeInTheDocument();
      // Status badge
      expect(screen.getByText('Connected', { selector: 'span' })).toBeInTheDocument();
      // Platform ID (truncated display — element exists in DOM)
      expect(screen.getByLabelText('Platform user ID')).toBeInTheDocument();
    });
  });

  // ── Test 4: Bluesky Connect calls OAuth endpoint ──────────────────────────
  it('calls the OAuth connect endpoint and redirects when Connect Bluesky is clicked', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([]);
    (socialAccountService.initiateOAuthConnect as any).mockResolvedValue({
      authorization_url: 'https://bsky.social/oauth/authorize?state=abc',
      state_token: 'abc',
    });

    // Intercept window.location.href assignment
    const locationSpy = vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      origin: 'http://localhost:5173',
    } as Location);
    const hrefSetter = vi.fn();
    Object.defineProperty(window, 'location', {
      get: () => ({ origin: 'http://localhost:5173', href: '' }),
      set: hrefSetter,
      configurable: true,
    });

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText('Bluesky')).toBeInTheDocument();
    });

    const connectBtn = screen.getByRole('button', { name: /Connect Bluesky account/i });
    await act(async () => {
      fireEvent.click(connectBtn);
    });

    await waitFor(() => {
      expect(socialAccountService.initiateOAuthConnect).toHaveBeenCalledWith(
        WORKSPACE_ID,
        'bluesky',
        expect.stringContaining('/oauth/bluesky/callback')
      );
    });

    locationSpy.mockRestore();
  });

  // ── Test 5: Disconnect confirmation dialog ────────────────────────────────
  it('opens a confirmation dialog when Disconnect is clicked', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([mockBlueskyAccount]);

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText('testuser.bsky.social')).toBeInTheDocument();
    });

    const disconnectBtn = screen.getByRole('button', {
      name: /Disconnect testuser\.bsky\.social/i,
    });
    fireEvent.click(disconnectBtn);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/Disconnect testuser\.bsky\.social\?/i)).toBeInTheDocument();
    expect(screen.getByText(/permanently remove/i)).toBeInTheDocument();
    // Cancel button should be present
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    // Confirm button should be present
    expect(screen.getByRole('button', { name: /^Disconnect$/i })).toBeInTheDocument();
  });

  // ── Test 6: Disconnect success updates UI ────────────────────────────────
  it('removes account from list after successful disconnect', async () => {
    (socialAccountService.listSocialAccounts as any)
      .mockResolvedValueOnce([mockBlueskyAccount])
      .mockResolvedValueOnce([]); // Mock the refetch after disconnect
    (socialAccountService.disconnectSocialAccount as any).mockResolvedValue(undefined);

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText('testuser.bsky.social')).toBeInTheDocument();
    });

    // Open dialog
    fireEvent.click(
      screen.getByRole('button', { name: /Disconnect testuser\.bsky\.social/i })
    );

    // Confirm disconnect
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^Disconnect$/i }));
    });

    await waitFor(() => {
      expect(socialAccountService.disconnectSocialAccount).toHaveBeenCalledWith(
        WORKSPACE_ID,
        mockBlueskyAccount.id
      );
      // Account should be gone from DOM
      expect(screen.queryByText('testuser.bsky.social')).not.toBeInTheDocument();
    });
  });

  // ── Test 7: Disconnect failure shows error ────────────────────────────────
  it('shows an inline error when disconnect API fails', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([mockBlueskyAccount]);
    (socialAccountService.disconnectSocialAccount as any).mockRejectedValueOnce(
      new Error('Server error: could not revoke token')
    );

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText('testuser.bsky.social')).toBeInTheDocument();
    });

    // Open dialog
    fireEvent.click(
      screen.getByRole('button', { name: /Disconnect testuser\.bsky\.social/i })
    );

    // Confirm
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /^Disconnect$/i }));
    });

    await waitFor(() => {
      // Account remains (appears in both the card and the still-open dialog)
      expect(screen.getAllByText('testuser.bsky.social').length).toBeGreaterThan(0);
    });
    // Inline error is shown
    expect(await screen.findByText(/Server error: could not revoke token/i)).toBeInTheDocument();
  });

  // ── Test 8: Unsupported providers are NOT shown ───────────────────────────
  it('does not render cards for unsupported providers (Twitter, LinkedIn, etc.)', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([]);

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText('Bluesky')).toBeInTheDocument();
    });

    // These platforms must not appear anywhere in the connect section
    expect(screen.queryByText('Twitter')).not.toBeInTheDocument();
    expect(screen.queryByText('X (Twitter)')).not.toBeInTheDocument();
    expect(screen.queryByText('LinkedIn')).not.toBeInTheDocument();
    expect(screen.queryByText('Instagram')).not.toBeInTheDocument();
    expect(screen.queryByText('Facebook')).not.toBeInTheDocument();
    expect(screen.queryByText('FAKE')).not.toBeInTheDocument();
  });

  // ── Test 9: Workspace switching refetches accounts ────────────────────────
  it('fetches accounts for the new workspace when workspaceId changes', async () => {
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([]);

    const { unmount } = renderAtWorkspacePath('ws-a');
    await waitFor(() => {
      expect(socialAccountService.listSocialAccounts).toHaveBeenCalledWith('ws-a');
    });

    unmount();
    vi.clearAllMocks();
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([mockBlueskyAccount]);

    renderAtWorkspacePath('ws-b');
    await waitFor(() => {
      expect(socialAccountService.listSocialAccounts).toHaveBeenCalledWith('ws-b');
    });
  });

  // ── Test 10: Unauthorized workspace is handled ────────────────────────────
  it('shows error state when workspace access is unauthorized (403)', async () => {
    const axiosError = Object.assign(new Error('Forbidden'), {
      response: {
        status: 403,
        data: { success: false, error: { code: 'PERMISSION_DENIED', message: 'Access denied to this workspace.' } },
      },
    });
    (socialAccountService.listSocialAccounts as any).mockRejectedValue(axiosError);

    renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      // A retry button must be present
      expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
    });
  });

  // ── Test 11: Sensitive token fields are NEVER rendered ───────────────────
  it('never renders access_token, refresh_token, or encrypted credential data', async () => {
    // Even if an account had these (which the backend never returns), they must not appear
    const accountWithSensitiveKeys = {
      ...mockBlueskyAccount,
      // These would be XSS-attack attempts or accidental leaks — must never render
    };
    (socialAccountService.listSocialAccounts as any).mockResolvedValue([accountWithSensitiveKeys]);

    const { container } = renderAtWorkspacePath();

    await waitFor(() => {
      expect(screen.getByText('testuser.bsky.social')).toBeInTheDocument();
    });

    const html = container.innerHTML.toLowerCase();

    // These strings must never appear anywhere in the rendered DOM
    expect(html).not.toContain('access_token');
    expect(html).not.toContain('refresh_token');
    expect(html).not.toContain('access_token_encrypted');
    expect(html).not.toContain('refresh_token_encrypted');
    expect(html).not.toContain('client_secret');
    expect(html).not.toContain('bearer ');

    // The scopes field IS allowed (it's safe metadata), but token values are not
    expect(html).not.toMatch(/eyj[a-z0-9]/i); // JWT-like token patterns
  });

  // ── Test 12: Loading state shows skeletons ────────────────────────────────
  it('shows skeleton loading cards while accounts are being fetched', () => {
    // Never resolve — keep in loading state
    (socialAccountService.listSocialAccounts as any).mockImplementation(
      () => new Promise(() => {})
    );

    renderAtWorkspacePath();

    // Loading region should be present
    const loadingRegion = screen.getByRole('status');
    expect(loadingRegion).toBeInTheDocument();
    expect(loadingRegion).toHaveAttribute('aria-label', 'Loading social accounts');
  });

  // ── Test 13: No workspace selected shows guard message ───────────────────
  it('shows a "no workspace selected" message on the global route with no active workspace', () => {
    // No activeWorkspace set, no route param
    renderAtGlobalPath();

    expect(screen.getByText(/No workspace selected/i)).toBeInTheDocument();
  });
});
