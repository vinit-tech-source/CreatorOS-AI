import { Bell, Search } from 'lucide-react';
import styles from './Topbar.module.css';
import { useAuthStore } from '../../stores/authStore';

export function Topbar() {
  const { user, logout } = useAuthStore();

  return (
    <header className={styles.topbar}>
      <div className={styles.left}>
        <div className={styles.searchContainer}>
          <Search className={styles.searchIcon} size={18} />
          <input 
            type="text" 
            placeholder="Search projects, posts..." 
            className={styles.searchInput}
          />
        </div>
      </div>
      
      <div className={styles.right}>
        <button className={styles.iconButton}>
          <Bell size={20} />
        </button>
        <div className={styles.userMenu}>
          <div className={styles.avatar}>
            {user?.first_name?.charAt(0) || 'U'}
          </div>
          <div className={styles.userInfo}>
            <span className={styles.userName}>{user?.first_name} {user?.last_name}</span>
            <span className={styles.userRole}>Owner</span>
          </div>
          <button className={styles.logoutButton} onClick={logout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
