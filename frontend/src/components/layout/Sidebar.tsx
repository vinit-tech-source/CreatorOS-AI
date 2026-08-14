import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  PenTool, 
  BarChart3, 
  Palette, 
  Share2, 
  Settings 
} from 'lucide-react';
import styles from './Sidebar.module.css';
import { useWorkspaceStore } from '../../stores/workspaceStore';

interface SidebarProps {
  className?: string;
}

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', path: '/projects', icon: FolderKanban },
  { name: 'Posts', path: '/posts', icon: PenTool },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Brand Kit', path: '/brand-kit', icon: Palette },
  { name: 'Social Accounts', path: '/social-accounts', icon: Share2 },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export function Sidebar({ className }: SidebarProps) {
  const { workspaces, activeWorkspace, setActiveWorkspace } = useWorkspaceStore();

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
          {workspaces.length === 0 ? (
            <option value="">Loading...</option>
          ) : (
            workspaces.map(ws => (
              <option key={ws.id} value={ws.id}>{ws.name}</option>
            ))
          )}
        </select>
      </div>

      <nav className={styles.navigation}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                isActive ? `${styles.navItem} ${styles.active}` : styles.navItem
              }
            >
              <Icon className={styles.navIcon} size={20} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
