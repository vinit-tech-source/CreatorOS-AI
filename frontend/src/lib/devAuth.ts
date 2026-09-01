/**
 * src/lib/devAuth.ts
 *
 * Development-only authentication bypass helper.
 *
 * SAFETY CONTRACT:
 *   - isDevBypassEnabled() returns true ONLY when BOTH:
 *       1. import.meta.env.DEV === true  (Vite dev server; false in prod builds)
 *       2. VITE_DEV_AUTH_BYPASS === "true"  (explicitly set in .env.development.local)
 *   - In production builds Vite replaces import.meta.env.DEV with `false`,
 *     making the entire bypass code-path dead code that tree-shakers remove.
 *   - Never injects fake tokens. Calls the real backend /auth/dev-token endpoint,
 *     which issues a genuine signed JWT for the deterministic dev@localhost identity.
 *   - All downstream API calls use that real JWT — no mock headers, no spoofing.
 *
 * DO NOT import this module in production code paths.
 */

import { useAuthStore } from '../stores/authStore';
import { API_BASE_URL } from '../services/api/client';

/** Returns true only when running in a Vite dev build with the bypass flag set. */
export function isDevBypassEnabled(): boolean {
  return (
    import.meta.env.DEV === true &&
    import.meta.env.VITE_DEV_AUTH_BYPASS === 'true'
  );
}

/**
 * Initialise the auth store using the backend dev-token endpoint.
 *
 * Steps:
 *  1. Calls GET /api/v1/auth/dev-token (only available when backend
 *     DEV_AUTH_BYPASS=true).
 *  2. Populates useAuthStore with the returned JWT and dev user profile.
 *  3. Stores the token in localStorage so the API client interceptor picks it up.
 *
 * Throws if the backend endpoint is unavailable (e.g. backend is off or
 * DEV_AUTH_BYPASS=false on the backend).
 */
export async function initDevAuth(): Promise<void> {
  if (!isDevBypassEnabled()) {
    return; // No-op when bypass is disabled — normal auth applies.
  }

  console.warn(
    '[DEV AUTH BYPASS] Fetching development token from backend...\n' +
    'This bypass is for local development only and will NOT work in production builds.'
  );

  const response = await fetch(`${API_BASE_URL}/auth/dev-token`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `[DEV AUTH BYPASS] Failed to fetch dev token (${response.status}). ` +
      `Is DEV_AUTH_BYPASS=true set in backend/.env?\n${text}`
    );
  }

  const json = await response.json();
  const { access_token, user } = json.data as {
    access_token: string;
    user: {
      id: string;
      email: string;
      username: string;
      full_name: string;
      role: string;
      region?: string | null;
      country?: string | null;
      is_active: boolean;
      is_verified: boolean;
      created_at: string | null;
      updated_at: string | null;
    };
  };

  // Map backend full_name to frontend first_name/last_name split
  const nameParts = user.full_name.split(' ');
  const first_name = nameParts[0] ?? 'Development';
  const last_name = nameParts.slice(1).join(' ') || 'User';

  const frontendUser = {
    id: user.id,
    first_name,
    last_name,
    email: user.email,
    username: user.username,
    region: user.region,
    country: user.country,
    is_active: user.is_active,
    created_at: user.created_at ?? new Date().toISOString(),
    updated_at: user.updated_at ?? new Date().toISOString(),
  };

  // Populate auth store exactly as a normal login would
  useAuthStore.getState().setAuth(frontendUser, access_token);

  console.warn(
    `[DEV AUTH BYPASS] ✓ Authenticated as ${user.email} (id=${user.id})\n` +
    'Token stored in authStore and localStorage.'
  );
}
