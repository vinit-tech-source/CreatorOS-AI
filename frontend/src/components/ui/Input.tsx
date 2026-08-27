import { InputHTMLAttributes, forwardRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import styles from './Input.module.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, fullWidth = true, className = '', type, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    const isPassword = type === 'password';
    
    const wrapperClasses = [
      styles.wrapper,
      fullWidth ? styles.fullWidth : '',
      className
    ].filter(Boolean).join(' ');

    const inputClasses = [
      styles.input,
      error ? styles.hasError : '',
      isPassword ? styles.inputWithIcon : ''
    ].filter(Boolean).join(' ');

    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

    return (
      <div className={wrapperClasses}>
        {label && <label className={styles.label}>{label}</label>}
        <div className={styles.inputContainer}>
          <input ref={ref} type={inputType} className={inputClasses} {...props} />
          {isPassword && (
            <button
              type="button"
              className={styles.toggleButton}
              onClick={() => setShowPassword(!showPassword)}
              tabIndex={-1}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          )}
        </div>
        {error && <span className={styles.errorText}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
