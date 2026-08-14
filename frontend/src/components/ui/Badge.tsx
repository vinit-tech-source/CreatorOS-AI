import { ReactNode } from 'react';
import styles from './Badge.module.css';

interface BadgeProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export function Badge({ children, variant = 'primary', className = '' }: BadgeProps) {
  const classNames = [
    styles.badge,
    styles[variant],
    className
  ].filter(Boolean).join(' ');

  return <span className={classNames}>{children}</span>;
}
