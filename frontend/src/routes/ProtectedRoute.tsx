import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { AppLayout } from '../components/layout/AppLayout';

/**
 * ProtectedRoute — guards all authenticated pages.
 *
 * Normal flow (bypass disabled):
 *   - If isInitializing: show loading screen
 *   - If not authenticated: redirect to /login
 *   - If authenticated: render AppLayout + child route
 *
 * Dev bypass flow (VITE_DEV_AUTH_BYPASS=true, DEV build only):
 *   - main.tsx calls initDevAuth() BEFORE React mounts.
 *   - By the time this component renders, authStore already has a real JWT.
 *   - isAuthenticated is true → normal render path (no special casing here).
 *   - A DevBanner renders inside AppLayout to signal the bypass is active.
 */
export function ProtectedRoute() {
  const { isAuthenticated, isInitializing } = useAuthStore();
  const location = useLocation();

  if (isInitializing) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="animate-pulse text-secondary">Loading Application...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
}
