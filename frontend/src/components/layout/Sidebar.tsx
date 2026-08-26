import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  BarChart3, 
  Palette, 
  Share2, 
  Settings,
  Building2,
  Sparkles,
  Calendar,
  FolderOpen,
  Bot,
  Database,
  CheckSquare
} from 'lucide-react';
import styles from './Sidebar.module.css';
import { useWorkspaceStore } from '../../stores/workspaceStore';

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const { workspaces, activeWorkspace, setActiveWorkspace } = useWorkspaceStore();

  const primaryNav = [
    { name: 'Home', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Create', path: '/create', icon: Sparkles },
    { name: 'Calendar', path: '/calendar', icon: Calendar },
    { name: 'Content', path: '/content', icon: FolderOpen },
    { name: 'Approval', path: '/approval', icon: CheckSquare },
    { name: 'Automation', path: '/automation', icon: Bot },
    { name: 'Insights', path: '/analytics', icon: BarChart3 },
  ];

  const secondaryNav = [
    {
      name: 'Social Accounts',
      path: activeWorkspace ? `/workspaces/${activeWorkspace.id}/social-accounts` : '/social-accounts',
      icon: Share2,
    },
    { name: 'Brand Kit', path: '/brand-kit', icon: Palette },
    { name: 'Knowledge', path: '/knowledge', icon: Database },
    { name: 'Projects', path: '/projects', icon: FolderKanban },
    { name: 'Workspaces', path: '/workspaces', icon: Building2 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const renderNavGroup = (items: typeof primaryNav) => (
    items.map((item) => {
      const Icon = item.icon;
      return (
        <NavLink
          key={item.name}
          to={item.path}
          className={({ isActive }) => 
            isActive ? `${styles.navItem} ${styles.active}` : styles.navItem
          }
        >
          <Icon className={styles.navIcon} size={18} />
          <span>{item.name}</span>
        </NavLink>
      );
    })
  );

  return (
    <aside className={`${styles.sidebar} ${className || ''}`}>
      <div className={styles.logoContainer}>
        <span className={styles.logoIcon}></span>
        <span className={styles.logoText}>CreatorOS AI</span>
      </div>
      
      <div className={styles.workspaceSelector}>
        <select 
          className={styles.workspaceSelect}
          value={activeWorkspace?.id || ''}
          onChange={(e) => {
            const ws = workspaces.find(w => w.id === e.target.value);
            if (ws) setActiveWorkspace(ws);
          }}
          disabled={workspaces.length === 0}
        >
          {useWorkspaceStore(state => state.isLoading) ? (
            <option value="">Loading...</option>
          ) : workspaces.length === 0 ? (
            <option value="">No workspaces found</option>
          ) : (
            workspaces.map(ws => (
              <option key={ws.id} value={ws.id}>{ws.name}</option>
            ))
          )}
        </select>
      </div>

      <nav className={styles.navigation}>
        <div className="mb-6">
          {renderNavGroup(primaryNav)}
        </div>
        
        <div>
          <div className="text-xs font-semibold text-secondary/50 uppercase tracking-wider mb-2 px-3">
            Configuration
          </div>
          {renderNavGroup(secondaryNav)}
        </div>
      </nav>
    </aside>
  );
}
