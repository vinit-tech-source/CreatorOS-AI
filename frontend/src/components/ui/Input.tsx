import { InputHTMLAttributes, forwardRef } from 'react';
import styles from './Input.module.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, fullWidth = true, className = '', ...props }, ref) => {
    
    const wrapperClasses = [
      styles.wrapper,
      fullWidth ? styles.fullWidth : '',
      className
    ].filter(Boolean).join(' ');

    const inputClasses = [
      styles.input,
      error ? styles.hasError : ''
    ].filter(Boolean).join(' ');

    return (
      <div className={wrapperClasses}>
        {label && <label className={styles.label}>{label}</label>}
        <input ref={ref} className={inputClasses} {...props} />
        {error && <span className={styles.errorText}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
