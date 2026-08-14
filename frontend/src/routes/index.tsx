import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';

import { Login } from '../pages/auth/Login';
import { Register } from '../pages/auth/Register';
import { Dashboard } from '../pages/dashboard/Dashboard';
import { Workspaces } from '../pages/workspaces/Workspaces';
import { Projects } from '../pages/projects/Projects';
import { Posts } from '../pages/posts/Posts';
import { Analytics } from '../pages/analytics/Analytics';
import { SocialAccounts } from '../pages/settings/SocialAccounts';
import { Settings } from '../pages/settings/Settings';

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workspaces" element={<Workspaces />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/posts" element={<Posts />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/social-accounts" element={<SocialAccounts />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
