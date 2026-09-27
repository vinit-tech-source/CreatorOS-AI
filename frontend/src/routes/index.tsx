import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';

import { Login } from '../pages/auth/Login';
import { Register } from '../pages/auth/Register';
import { Dashboard } from '../pages/dashboard/Dashboard';
import { Workspaces } from '../pages/workspaces/Workspaces';
import { Projects } from '../pages/projects/Projects';
import { Analytics } from '../pages/analytics/Analytics';
import { SocialAccounts } from '../pages/settings/SocialAccounts';
import { Settings } from '../pages/settings/Settings';
import { BrandKit } from '../pages/brand/BrandKit';

// New Pages
import { CreateStudio } from '../pages/create/CreateStudio';
import { ContentLibrary } from '../pages/content/ContentLibrary';
import { ContentCalendar } from '../pages/calendar/ContentCalendar';
import { ApprovalCenter } from '../pages/approval/ApprovalCenter';
import { AutomationDashboard } from '../pages/automation/AutomationDashboard';
import { PipelineProgress } from '../pages/automation/PipelineProgress';
import { KnowledgeBase } from '../pages/knowledge/KnowledgeBase';
import { LandingPage } from '../pages/LandingPage';
import Privacy from '../pages/Privacy';
import Terms from '../pages/Terms';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/terms" element={<Terms />} />
      
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        
        {/* Core Product Routes */}
        <Route path="/content" element={<ContentLibrary />} />
        <Route path="/calendar" element={<ContentCalendar />} />
        <Route path="/approval" element={<ApprovalCenter />} />
        <Route path="/automation" element={<AutomationDashboard />} />
        <Route path="/automation/pipeline" element={<PipelineProgress />} />
        <Route path="/analytics" element={<Analytics />} />
        
        {/* Configuration Routes */}
        <Route path="/social-accounts" element={<SocialAccounts />} />
        <Route path="/brand-kit" element={<BrandKit />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/settings" element={<Settings />} />

        {/* Legacy / Workspace-Scoped Routes */}
        <Route path="/workspaces" element={<Workspaces />} />
        <Route path="/workspaces/:workspaceId/analytics" element={<Analytics />} />
        <Route path="/workspaces/:workspaceId/social-accounts" element={<SocialAccounts />} />
      </Route>

      <Route element={<ProtectedRoute noLayout />}>
        <Route path="/create" element={<CreateStudio />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

