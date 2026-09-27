import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../ThemeProvider';
import './ThemeToggle.css';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <button
      className="theme-toggle-btn"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <Sun size={20} className="theme-toggle-icon text-warning" />
      ) : (
        <Moon size={20} className="theme-toggle-icon text-primary" />
      )}
    </button>
  );
}
