import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';

import { Login } from '../pages/auth/Login';
import { Register } from '../pages/auth/Register';
import { Dashboard } from '../pages/dashboard/Dashboard';
import { Workspaces } from '../pages/workspaces/Workspaces';
import { Projects } from '../pages/projects/Projects';
import { PostList } from '../pages/posts/PostList';
import { PostDetails } from '../pages/posts/PostDetails';
import { Analytics } from '../pages/analytics/Analytics';
import { SocialAccounts } from '../pages/settings/SocialAccounts';
import { Settings } from '../pages/settings/Settings';
import { ContentCreation } from '../pages/content-creation/ContentCreation';

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
        <Route path="/workspaces/:workspaceId/projects/:projectId/posts" element={<PostList />} />
        <Route path="/workspaces/:workspaceId/projects/:projectId/posts/:postId" element={<PostDetails />} />
        <Route path="/analytics" element={<Analytics />} />
        {/* Workspace-scoped social accounts route (preferred) */}
        <Route path="/workspaces/:workspaceId/social-accounts" element={<SocialAccounts />} />
        {/* Global social accounts route — falls back to activeWorkspace */}
        <Route path="/social-accounts" element={<SocialAccounts />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/workspaces/:workspaceId/projects/:projectId/create" element={<ContentCreation />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

