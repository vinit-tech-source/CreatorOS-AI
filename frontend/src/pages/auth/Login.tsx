import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../../services/api';
import { useAuthStore } from '../../stores/authStore';
import { Sparkles, ArrowRight, Lock, Mail } from 'lucide-react';
import styles from './Login.module.css';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await apiClient.post('/auth/login', { email, password });
      
      if (response.data.success) {
        const token = response.data.data.tokens.access_token;
        const meResponse = await apiClient.get('/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (meResponse.data.success) {
          setAuth(meResponse.data.data, token);
          navigate('/dashboard');
        } else {
          setError('Failed to fetch user profile');
        }
      } else {
        setError(response.data.message || 'Login failed');
      }
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const validationMsg = Array.isArray(detail)
        ? detail.map((d: any) => d.msg).join(', ')
        : undefined;
      setError(
        validationMsg || 
        err.response?.data?.message || 
        err.response?.data?.error?.message || 
        err.message || 
        'An error occurred during login'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Animated Mesh Background */}
      <div className={styles.meshBackground}>
        <div className={styles.blob} id={styles.blob1}></div>
        <div className={styles.blob} id={styles.blob2}></div>
        <div className={styles.blob} id={styles.blob3}></div>
      </div>

      <div className={styles.contentWrapper}>
        <div className={styles.glassCard}>
          <div className={styles.header}>
            <div className={styles.brandBadge}>
              <Sparkles size={16} className={styles.sparkleIcon} />
              <span>CreatorOS AI</span>
            </div>
            <h1 className={styles.title}>Welcome back</h1>
            <p className={styles.subtitle}>Sign in to access your intelligent workspace</p>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            {error && (
              <div className={styles.errorBox}>
                {error}
              </div>
            )}
            
            <div className={styles.inputGroup}>
              <label>Email Address</label>
              <div className={styles.inputWrapper}>
                <Mail size={18} className={styles.inputIcon} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className={styles.glassInput}
                />
              </div>
            </div>
            
            <div className={styles.inputGroup}>
              <label>Password</label>
              <div className={styles.inputWrapper}>
                <Lock size={18} className={styles.inputIcon} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className={styles.glassInput}
                />
              </div>
            </div>
            
            <button type="submit" disabled={isLoading} className={styles.submitBtn}>
              {isLoading ? 'Signing in...' : 'Sign In'}
              {!isLoading && <ArrowRight size={18} className={styles.btnArrow} />}
            </button>
          </form>
          
          <div className={styles.footer}>
            <Link to="/" className={styles.backLink}>
              ← Back to Home
            </Link>
            <span className={styles.footerText}>
              Don't have an account?{' '}
              <Link to="/register" className={styles.signupLink}>
                Sign up
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
