/**
 * src/components/dev/DevBanner.tsx
 *
 * Renders a small, clearly visible banner when the dev auth bypass is active.
 * NEVER renders in production (guarded by import.meta.env.DEV check at runtime
 * and eliminated by Vite's tree-shaker in production builds).
 */
import { isDevBypassEnabled } from '../../lib/devAuth';

export function DevBanner() {
  // Production builds: import.meta.env.DEV === false → early return, dead code removed.
  if (!isDevBypassEnabled()) return null;

  return (
    <div
      id="dev-auth-bypass-banner"
      style={{
        position: 'fixed',
        bottom: '12px',
        right: '12px',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '5px 10px',
        background: 'rgba(234, 179, 8, 0.15)',
        border: '1px solid rgba(234, 179, 8, 0.6)',
        borderRadius: '6px',
        fontSize: '11px',
        fontFamily: 'monospace',
        fontWeight: 600,
        color: '#fbbf24',
        backdropFilter: 'blur(6px)',
        userSelect: 'none',
        pointerEvents: 'none',
        letterSpacing: '0.05em',
      }}
      title="Development auth bypass is active. This banner never appears in production."
    >
      <span style={{ fontSize: '13px' }}>⚠</span>
      DEV AUTH BYPASS
    </div>
  );
}
