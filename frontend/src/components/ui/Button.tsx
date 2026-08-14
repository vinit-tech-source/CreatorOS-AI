import { ButtonHTMLAttributes, ReactNode } from 'react';
import styles from './Button.module.css';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  fullWidth?: boolean;
}

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  isLoading = false,
  fullWidth = false,
  className = '',
  disabled,
  ...props 
}: ButtonProps) {
  
  const classNames = [
    styles.button,
    styles[variant],
    styles[size],
    fullWidth ? styles.fullWidth : '',
    isLoading ? styles.loading : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button 
      className={classNames} 
      disabled={disabled || isLoading} 
      {...props}
    >
      {isLoading && <Loader2 className={styles.spinner} size={16} />}
      <span className={styles.content}>{children}</span>
    </button>
  );
}
