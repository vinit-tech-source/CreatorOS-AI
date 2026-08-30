import { ReactNode, useEffect, useState } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { DevBanner } from '../dev/DevBanner';
import { AppShell3D } from '../3d/AppShell3D';
import styles from './AppLayout.module.css';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { fetchWorkspaces } = useWorkspaceStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  return (
    <div className={styles.layout}>
      <AppShell3D />
      
      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div className={styles.mobileOverlay} onClick={closeMobileMenu} />
      )}
      
      <Sidebar className={`${styles.sidebar} ${isMobileMenuOpen ? styles.sidebarOpen : ''}`} />
      
      <div className={styles.mainWrapper}>
        <Topbar onMenuToggle={toggleMobileMenu} />
        <main className={styles.mainContent}>
          {children}
        </main>
      </div>
      {/* Renders only when VITE_DEV_AUTH_BYPASS=true in a Vite dev build */}
      <DevBanner />
    </div>
  );
}
