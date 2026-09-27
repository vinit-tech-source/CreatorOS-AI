import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { apiClient } from '../../services/api';
import { Sparkles, ArrowRight, Lock, Mail, User } from 'lucide-react';
import styles from './Login.module.css'; // Reusing the same auth layout styles

export function Register() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await apiClient.post('/auth/register', {
        username,
        full_name: `${firstName} ${lastName}`.trim(),
        email,
        password,
      });

      if (response.data.success) {
        navigate('/login', { state: { message: 'Registration successful! Please login.' } });
      } else {
        setError(response.data.message || 'Registration failed');
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
        'An error occurred during registration'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Animated Mesh Background (Shared with Login) */}
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
            <h1 className={styles.title}>Create Account</h1>
            <p className={styles.subtitle}>Join CreatorOS to scale your content</p>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            {error && (
              <div className={styles.errorBox}>
                {error}
              </div>
            )}

            <div className="flex gap-4 w-full">
              <div className={styles.inputGroup} style={{ flex: 1 }}>
                <label>First Name</label>
                <div className={styles.inputWrapper}>
                  <User size={18} className={styles.inputIcon} />
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="John"
                    required
                    className={styles.glassInput}
                  />
                </div>
              </div>
              <div className={styles.inputGroup} style={{ flex: 1 }}>
                <label>Last Name</label>
                <div className={styles.inputWrapper}>
                  <User size={18} className={styles.inputIcon} />
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Doe"
                    required
                    className={styles.glassInput}
                  />
                </div>
              </div>
            </div>

            <div className={styles.inputGroup}>
              <label>Username</label>
              <div className={styles.inputWrapper}>
                <span className={styles.inputIcon} style={{ fontWeight: 600, fontSize: '16px' }}>@</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe"
                  required
                  className={styles.glassInput}
                />
              </div>
            </div>

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
              {isLoading ? 'Creating account...' : 'Sign Up'}
              {!isLoading && <ArrowRight size={18} className={styles.btnArrow} />}
            </button>
          </form>

          <div className={styles.footer}>
            <Link to="/" className={styles.backLink}>
              ← Back to Home
            </Link>
            <span className={styles.footerText}>
              Already have an account?{' '}
              <Link to="/login" className={styles.signupLink}>
                Sign in
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
