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
  return (
    <aside className={`${styles.sidebar} ${className || ''}`}>
      <div className={styles.logoContainer}>
        <span className={styles.logoIcon}></span>
        <span className={styles.logoText}>CreatorOS AI</span>
      </div>
      
      <div className={styles.workspaceSelector}>
        {/* Placeholder for workspace selector */}
        <div className={styles.workspaceSelectorButton}>
          Default Workspace
        </div>
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
