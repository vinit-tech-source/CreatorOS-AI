import { ReactNode, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useWorkspaceStore } from '../../stores/workspaceStore';
import { DevBanner } from '../dev/DevBanner';
import styles from './AppLayout.module.css';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { fetchWorkspaces } = useWorkspaceStore();

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  return (
    <div className={styles.layout}>
      <Sidebar className={styles.sidebar} />
      <div className={styles.mainWrapper}>
        <Topbar />
        <main className={styles.mainContent}>
          {children}
        </main>
      </div>
      {/* Renders only when VITE_DEV_AUTH_BYPASS=true in a Vite dev build */}
      <DevBanner />
    </div>
  );
}
