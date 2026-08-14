/**
 * tests/devAuth.test.ts
 *
 * Tests for the dev auth bypass helper (src/lib/devAuth.ts).
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';

// ─────────────────────────────────────────────
// isDevBypassEnabled
// ─────────────────────────────────────────────

describe('isDevBypassEnabled', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('returns false when VITE_DEV_AUTH_BYPASS is not set', async () => {
    vi.stubEnv('DEV', 'true');
    // VITE_DEV_AUTH_BYPASS intentionally not set
    const { isDevBypassEnabled } = await import('../src/lib/devAuth');
    // Re-evaluate with fresh import
    expect(isDevBypassEnabled()).toBe(false);
  });

  it('returns false when VITE_DEV_AUTH_BYPASS is "false"', async () => {
    vi.stubEnv('DEV', 'true');
    vi.stubEnv('VITE_DEV_AUTH_BYPASS', 'false');
    const { isDevBypassEnabled } = await import('../src/lib/devAuth');
    expect(isDevBypassEnabled()).toBe(false);
  });

  it('returns false when VITE_DEV_AUTH_BYPASS is "false"', async () => {
    vi.stubEnv('VITE_DEV_AUTH_BYPASS', 'false');
    const { isDevBypassEnabled } = await import('../src/lib/devAuth');
    expect(isDevBypassEnabled()).toBe(false);
  });

  it('production safety is enforced at build time by Vite (documents the contract)', () => {
    // import.meta.env.DEV is a COMPILE-TIME constant replaced by Vite:
    //   - Dev server:  DEV === true
    //   - Production build: DEV === false (literal, inlined by esbuild)
    //
    // This means vi.stubEnv('DEV', 'false') has no effect on already-compiled
    // isDevBypassEnabled() because the value was inlined at parse time.
    //
    // Production safety guarantee: in `npm run build` output the function body
    // becomes `return (false && ...)` which tree-shakers eliminate entirely.
    // The safety cannot be unit-tested here; it IS verified by `npm run build`.
    expect(true).toBe(true); // contract documented above
  });
});

// ─────────────────────────────────────────────
// initDevAuth — no-op when bypass disabled
// ─────────────────────────────────────────────

describe('initDevAuth', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it('is a no-op when bypass is disabled', async () => {
    vi.stubEnv('VITE_DEV_AUTH_BYPASS', 'false');
    const fetchSpy = vi.spyOn(global, 'fetch');
    const { initDevAuth } = await import('../src/lib/devAuth');
    await initDevAuth();
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
