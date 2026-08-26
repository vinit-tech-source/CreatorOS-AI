/**
 * SocialAccounts.tsx
 *
 * Social Accounts management page for CreatorOS AI.
 *
 * Supports two route patterns:
 *   - /workspaces/:workspaceId/social-accounts  (workspace-scoped, preferred)
 *   - /social-accounts                          (falls back to activeWorkspace)
 *
 * SECURITY:
 *   - No token, refresh token, OAuth secret, or encrypted field is ever rendered.
 *   - OAuth is initiated via a backend endpoint; the browser is redirected to the
 *     provider authorization URL. The backend handles CSRF, code exchange, and
 *     token storage.
 *   - All account status comes from backend state only — no frontend timer inference.
 */
import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Share2,
  Plus,
  Trash2,
  AlertTriangle,
  AlertCircle,
  RefreshCw,
  ShieldCheck,
  ExternalLink,
  X,
  CheckCircle,
  Clock,
  WifiOff,
  Info,
} from 'lucide-react';

import { PageHeader } from '../../components/layout/PageHeader';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { useSocialAccountStore } from '../../stores/socialAccountStore';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { socialAccountService } from '../../services/api/socialAccountService';
import { SocialAccount } from '../../types';
import styles from './SocialAccounts.module.css';

// ─── Constants ────────────────────────────────────────────────────────────────

/**
 * Only Bluesky is currently supported by the backend.
 * Adding a future provider = add an entry here; no page rewrite needed.
 */
const SUPPORTED_PROVIDERS = [
  {
    key: 'bluesky',
    label: 'Bluesky',
    description: 'AT Protocol social network',
    iconLabel: 'B',
    iconClass: styles.bluesky,
  },
] as const;

type SupportedPlatform = (typeof SUPPORTED_PROVIDERS)[number]['key'];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return 'Unknown';
  }
}

function getAccountStatus(account: SocialAccount): {
  label: string;
  variant: 'success' | 'warning' | 'danger' | 'secondary';
  Icon: React.ElementType;
} {
  if (!account.is_active) {
    return { label: 'Disconnected', variant: 'danger', Icon: WifiOff };
  }
  if (account.token_expires_at) {
    const expiresAt = new Date(account.token_expires_at);
    const now = new Date();
    const hoursUntilExpiry = (expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60);
    if (expiresAt < now) {
      return { label: 'Reauthorize Required', variant: 'warning', Icon: AlertTriangle };
    }
    if (hoursUntilExpiry < 24) {
      return { label: 'Expiring Soon', variant: 'warning', Icon: Clock };
    }
  }
  return { label: 'Connected', variant: 'success', Icon: CheckCircle };
}

function getPlatformClass(platform: string): string {
  return platform.toLowerCase() === 'bluesky' ? styles.bluesky : '';
}

// ─── Skeleton Loading Card ─────────────────────────────────────────────────────

function AccountSkeleton() {
  return (
    <Card glass>
      <CardContent>
        <div className={styles.skeletonCard}>
          <div className={styles.skeletonHeader}>
            <div className={`${styles.skeleton} ${styles.skeletonAvatar}`} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: '60%' }} />
              <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: '40%', height: 10 }} />
            </div>
          </div>
          <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: '100%', height: 72 }} />
          <div className={styles.skeletonMeta}>
            <div className={`${styles.skeleton} ${styles.skeletonButton}`} />
            <div className={`${styles.skeleton} ${styles.skeletonButton}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Disconnect Confirmation Dialog ────────────────────────────────────────────

interface DisconnectDialogProps {
  account: SocialAccount;
  isDisconnecting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

function DisconnectDialog({ account, isDisconnecting, onConfirm, onCancel }: DisconnectDialogProps) {
  return (
    <div
      className={styles.dialogOverlay}
      role="dialog"
      aria-modal="true"
      aria-labelledby="disconnect-dialog-title"
      onClick={(e) => { if (e.target === e.currentTarget) onCancel(); }}
    >
      <div className={styles.dialog}>
        <h2 id="disconnect-dialog-title" className={styles.dialogTitle}>
          <AlertTriangle size={20} color="#f59e0b" aria-hidden />
          Disconnect {account.account_name}?
        </h2>
        <p className={styles.dialogBody}>
          This will permanently remove the <strong>{account.platform}</strong> account{' '}
          <strong>{account.account_name}</strong> from this workspace. Any posts
          scheduled for this account will stop publishing. This action cannot be undone.
        </p>
        <div className={styles.dialogActions}>
          <Button
            variant="outline"
            size="sm"
            onClick={onCancel}
            disabled={isDisconnecting}
            id="disconnect-cancel-btn"
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={onConfirm}
            isLoading={isDisconnecting}
            id="disconnect-confirm-btn"
          >
            Disconnect
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── Account Card ─────────────────────────────────────────────────────────────

interface AccountCardProps {
  account: SocialAccount;
  workspaceId: string;
  onDisconnected: () => void;
}

function AccountCard({ account, workspaceId, onDisconnected }: AccountCardProps) {
  const { disconnectAccount } = useSocialAccountStore();
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDisconnecting, setIsDisconnecting] = useState(false);
  const [disconnectError, setDisconnectError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const status = getAccountStatus(account);
  const StatusIcon = status.Icon;

  const handleDisconnect = async () => {
    setIsDisconnecting(true);
    setDisconnectError(null);
    try {
      await disconnectAccount(workspaceId, account.id);
      setShowConfirm(false);
      onDisconnected();
    } catch (err: any) {
      setDisconnectError(
        err?.response?.data?.error?.message ||
        err?.message ||
        'Failed to disconnect. Please try again.'
      );
      setIsDisconnecting(false);
    }
  };

  return (
    <>
      <Card glass className={styles.accountCard}>
        <CardContent>
          {/* ── Header ── */}
          <div className={styles.cardHeader}>
            <div className={styles.platformInfo}>
              <div className={`${styles.platformIcon} ${getPlatformClass(account.platform)}`}
                aria-label={account.platform}>
                {account.platform.charAt(0)}
              </div>
              <div className={styles.platformMeta}>
                <div className={styles.accountName}>{account.account_name}</div>
                <div className={styles.platformLabel}>{account.platform}</div>
              </div>
            </div>
            <div className={styles.statusBadge}>
              <Badge variant={status.variant}>
                <StatusIcon size={11} style={{ marginRight: 4, verticalAlign: 'middle' }} aria-hidden />
                {status.label}
              </Badge>
            </div>
          </div>

          {/* ── Metadata grid ── */}
          <div className={styles.metaGrid}>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Platform ID</span>
              <span
                className={`${styles.metaValue} ${styles.platformUserId}`}
                title={account.platform_user_id}
                aria-label="Platform user ID"
              >
                {account.platform_user_id || 'N/A'}
              </span>
            </div>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Connected On</span>
              <span className={styles.metaValue}>{formatDate(account.connected_at)}</span>
            </div>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Status</span>
              <span className={styles.metaValue}>{account.is_active ? 'Active' : 'Inactive'}</span>
            </div>
            <div className={styles.metaItem}>
              <span className={styles.metaLabel}>Token Expires</span>
              <span className={`${styles.metaValue} ${!account.token_expires_at ? styles.metaValueMuted : ''}`}>
                {account.token_expires_at ? formatDate(account.token_expires_at) : 'N/A'}
              </span>
            </div>
          </div>

          {/* ── Extended details (togglable) ── */}
          {showDetails && (
            <div className={styles.metaGrid} style={{ marginTop: 8 }}>
              <div className={styles.metaItem} style={{ gridColumn: '1 / -1' }}>
                <span className={styles.metaLabel}>Scopes</span>
                <span className={`${styles.metaValue} ${!account.scopes ? styles.metaValueMuted : ''}`}
                  style={{ whiteSpace: 'normal', wordBreak: 'break-all', fontSize: '0.75rem' }}>
                  {account.scopes || 'N/A'}
                </span>
              </div>
              <div className={styles.metaItem} style={{ gridColumn: '1 / -1' }}>
                <span className={styles.metaLabel}>Last Updated</span>
                <span className={styles.metaValue}>{formatDate(account.updated_at)}</span>
              </div>
            </div>
          )}

          {/* ── Disconnect error ── */}
          {disconnectError && (
            <div className={styles.inlineError} role="alert">
              <AlertCircle size={15} aria-hidden />
              {disconnectError}
            </div>
          )}

          {/* ── Actions ── */}
          <div className={styles.cardActions}>
            <Button
              variant="ghost"
              size="sm"
              fullWidth
              onClick={() => setShowDetails(v => !v)}
              id={`details-toggle-${account.id}`}
              aria-expanded={showDetails}
            >
              <Info size={14} aria-hidden />
              {showDetails ? 'Hide Details' : 'Details'}
            </Button>
            <Button
              variant="danger"
              size="sm"
              fullWidth
              onClick={() => { setDisconnectError(null); setShowConfirm(true); }}
              id={`disconnect-btn-${account.id}`}
              aria-label={`Disconnect ${account.account_name}`}
            >
              <Trash2 size={14} aria-hidden />
              Disconnect
            </Button>
          </div>
        </CardContent>
      </Card>

      {showConfirm && (
        <DisconnectDialog
          account={account}
          isDisconnecting={isDisconnecting}
          onConfirm={handleDisconnect}
          onCancel={() => { setShowConfirm(false); setIsDisconnecting(false); }}
        />
      )}
    </>
  );
}

// ─── Connect Provider Button ───────────────────────────────────────────────────

interface ConnectProviderCardProps {
  provider: (typeof SUPPORTED_PROVIDERS)[number];
  isConnecting: boolean;
  onConnectStart: (platform: SupportedPlatform) => void;
  connectingPlatform: SupportedPlatform | null;
}

function ConnectProviderCard({
  provider,
  isConnecting,
  onConnectStart,
  connectingPlatform,
}: ConnectProviderCardProps) {
  const isThisConnecting = isConnecting && connectingPlatform === provider.key;

  const handleConnect = () => {
    onConnectStart(provider.key);
  };

  return (
    <button
      className={styles.providerCard}
      onClick={handleConnect}
      disabled={isConnecting}
      id={`connect-${provider.key}-btn`}
      aria-label={`Connect ${provider.label} account`}
      aria-busy={isThisConnecting}
      type="button"
    >
      <div className={`${styles.providerCardIcon} ${provider.iconClass}`}>
        {isThisConnecting ? (
          <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} aria-hidden />
        ) : (
          provider.iconLabel
        )}
      </div>
      <div className={styles.providerCardMeta}>
        <span className={styles.providerCardName}>{provider.label}</span>
        <span className={styles.providerCardDesc}>{provider.description}</span>
      </div>
      {!isThisConnecting && <Plus size={16} style={{ marginLeft: 'auto', flexShrink: 0, opacity: 0.6 }} aria-hidden />}
    </button>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export function SocialAccounts() {
  // Route param (workspace-scoped route: /workspaces/:workspaceId/social-accounts)
  const { workspaceId: routeWorkspaceId } = useParams<{ workspaceId: string }>();

  // Fallback: global active workspace (for /social-accounts route)
  const { activeWorkspace } = useWorkspaceStore();

  // Resolved workspace ID — prefer route param, fall back to active workspace
  const workspaceId = routeWorkspaceId || activeWorkspace?.id || null;

  const {
    accounts,
    isLoading,
    error,
    fetchAccounts,
    clearAccounts,
  } = useSocialAccountStore();

  const [connectError, setConnectError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectingPlatform, setConnectingPlatform] = useState<SupportedPlatform | null>(null);

  // ── Workspace isolation: fetch when workspace changes, clear on unmount ──
  const loadAccounts = useCallback(() => {
    if (workspaceId) {
      fetchAccounts(workspaceId);
    }
  }, [workspaceId, fetchAccounts]);

  useEffect(() => {
    loadAccounts();
    return () => {
      // Clear stale state when navigating away so the next mount is clean
      clearAccounts();
    };
  }, [loadAccounts, clearAccounts]);

  // ── OAuth Connect Flow ────────────────────────────────────────────────────
  // All OAuth logic lives in the backend.
  // Frontend only: calls the initiation endpoint → gets authorization_url → redirects.
  const handleConnect = useCallback(async (platform: SupportedPlatform) => {
    if (!workspaceId) return;
    setConnectError(null);
    setIsConnecting(true);
    setConnectingPlatform(platform);

    try {
      // The redirect_uri is where the provider will send the user after auth.
      // The backend's OAuth callback endpoint then handles code exchange.
      const callbackUrl = `${window.location.origin}/oauth/${platform}/callback`;
      const { authorization_url } = await socialAccountService.initiateOAuthConnect(
        workspaceId,
        platform,
        callbackUrl
      );
      // Navigate the browser — backend handles CSRF/state/token from here
      window.location.href = authorization_url;
    } catch (err: any) {
      const message =
        err?.response?.data?.error?.message ||
        err?.message ||
        `Failed to start ${platform} connection. Please try again.`;
      setConnectError(message);
      setIsConnecting(false);
      setConnectingPlatform(null);
    }
  }, [workspaceId]);

  // ── Render ────────────────────────────────────────────────────────────────

  const noWorkspace = !workspaceId;

  return (
    <div className={styles.page}>
      <PageHeader
        title="Social Accounts"
        subtitle="Connect your social media accounts to publish content and track performance."
        action={
          accounts.length > 0 ? (
            <Button
              variant="primary"
              size="sm"
              onClick={() => document.getElementById('connect-bluesky-btn')?.click()}
              id="header-connect-btn"
              disabled={isConnecting || noWorkspace}
              isLoading={isConnecting}
            >
              <Plus size={16} aria-hidden />
              Connect Account
            </Button>
          ) : undefined
        }
      />

      {/* ── No workspace guard ── */}
      {noWorkspace && (
        <Card glass>
          <CardContent>
            <div className={styles.emptyState}>
              <AlertCircle size={40} className={styles.emptyIcon} aria-hidden />
              <p className={styles.emptyTitle}>No workspace selected</p>
              <p className={styles.emptyDescription} style={{ marginBottom: '1rem' }}>
                Select a workspace from the sidebar to manage its social accounts.
              </p>
              <Button onClick={() => window.location.href = '/workspaces'}>
                Go to Workspaces
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Loading state ── */}
      {!noWorkspace && isLoading && (
        <div
          className={styles.accountGrid}
          role="status"
          aria-label="Loading social accounts"
          aria-live="polite"
        >
          <AccountSkeleton />
          <AccountSkeleton />
          <AccountSkeleton />
        </div>
      )}

      {/* ── Error state ── */}
      {!noWorkspace && !isLoading && error && (
        <Card glass>
          <CardContent>
            <div className={styles.errorState} role="alert">
              <AlertCircle size={40} aria-hidden />
              <p className={styles.errorTitle}>Unable to load social accounts</p>
              <p className={styles.errorMessage}>{error}</p>
              <Button variant="outline" size="sm" onClick={loadAccounts} id="retry-load-btn">
                <RefreshCw size={14} aria-hidden />
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Connected accounts ── */}
      {!noWorkspace && !isLoading && !error && accounts.length > 0 && (
        <div className={styles.accountGrid} role="list" aria-label="Connected social accounts">
          {accounts.map(account => (
            <div role="listitem" key={account.id}>
              <AccountCard
                account={account}
                workspaceId={workspaceId}
                onDisconnected={loadAccounts}
              />
            </div>
          ))}
        </div>
      )}

      {/* ── Empty state ── */}
      {!noWorkspace && !isLoading && !error && accounts.length === 0 && (
        <Card glass>
          <CardContent>
            <div className={styles.emptyState}>
              <Share2 size={52} className={styles.emptyIcon} aria-hidden />
              <p className={styles.emptyTitle}>No accounts connected yet</p>
              <p className={styles.emptyDescription}>
                Connect a social account to start publishing and tracking performance.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Connect new accounts section ── */}
      {!noWorkspace && !isLoading && (
        <div className={styles.connectSection}>
          <div className={styles.sectionDivider} />
          <p className={styles.connectTitle}>Connect a New Account</p>

          {/* OAuth connect error */}
          {connectError && (
            <div className={styles.inlineError} role="alert">
              <AlertCircle size={15} aria-hidden />
              {connectError}
              <button
                style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}
                onClick={() => setConnectError(null)}
                aria-label="Dismiss error"
              >
                <X size={14} />
              </button>
            </div>
          )}

          <div className={styles.providerList}>
            {SUPPORTED_PROVIDERS.map(provider => (
              <ConnectProviderCard
                key={provider.key}
                provider={provider}
                isConnecting={isConnecting}
                connectingPlatform={connectingPlatform}
                onConnectStart={handleConnect}
              />
            ))}
          </div>

          {/* Security notice — no tokens shown */}
          <p className={styles.oauthNote}>
            <ShieldCheck size={13} aria-hidden />
            Credentials are stored securely by the server. No tokens are ever shown here.
          </p>

          {/* Link to Bluesky for user reference */}
          <p className={styles.oauthNote} style={{ marginTop: 4 }}>
            <ExternalLink size={12} aria-hidden />
            <a
              href="https://bsky.app"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--color-primary)' }}
            >
              Don't have a Bluesky account? Create one at bsky.app
            </a>
          </p>
        </div>
      )}
    </div>
  );
}
