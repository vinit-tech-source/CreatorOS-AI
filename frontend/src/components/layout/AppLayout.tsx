import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import styles from './AppLayout.module.css';

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className={styles.layout}>
      <Sidebar className={styles.sidebar} />
      <div className={styles.mainWrapper}>
        <Topbar />
        <main className={styles.mainContent}>
          {children}
        </main>
      </div>
    </div>
  );
}
