import { ReactNode } from 'react';
import styles from './Card.module.css';

interface CardProps {
  children: ReactNode;
  className?: string;
  glass?: boolean;
}

export function Card({ children, className = '', glass = false }: CardProps) {
  const classNames = [
    styles.card,
    glass ? 'glass-panel' : 'extruded-panel',
    className
  ].filter(Boolean).join(' ');

  return <div className={classNames}>{children}</div>;
}

interface CardHeaderProps {
  title: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
  className?: string;
}

export function CardHeader({ title, subtitle, action, className = '' }: CardHeaderProps) {
  return (
    <div className={`${styles.header} ${className}`}>
      <div>
        <h3 className={styles.title}>{title}</h3>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

export function CardContent({ children, className = '' }: { children: ReactNode, className?: string }) {
  return <div className={`${styles.content} ${className}`}>{children}</div>;
}

export function CardFooter({ children, className = '' }: { children: ReactNode, className?: string }) {
  return <div className={`${styles.footer} ${className}`}>{children}</div>;
}
