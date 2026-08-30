import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { apiClient } from '../../services/api';
import { Canvas } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Stars } from '@react-three/drei';
import { Suspense } from 'react';
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
      // Handle Pydantic validation errors (array of {msg, loc}) as well as app errors
      const detail = err.response?.data?.detail;
      const validationMsg = Array.isArray(detail)
        ? detail.map((d: any) => d.msg).join(', ')
        : undefined;
      setError(validationMsg || err.response?.data?.error?.message || err.message || 'An error occurred during registration');
    } finally {
      setIsLoading(false);
    }
  };

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div className={styles.container}>
      <div className={styles.visualPane}>
        <div className={styles.canvasContainer}>
          <Canvas camera={{ position: [0, 0, 5], fov: 45 }} aria-hidden="true">
            <color attach="background" args={['#09090b']} />
            <ambientLight intensity={0.5} />
            <directionalLight position={[10, 10, 5]} intensity={1} color="#4F46E5" />
            <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#0ea5e9" />
            
            <Suspense fallback={null}>
              <Stars radius={100} depth={50} count={1500} factor={4} saturation={0} fade speed={prefersReducedMotion ? 0 : 1} />
              <Float speed={prefersReducedMotion ? 0 : 2} rotationIntensity={prefersReducedMotion ? 0 : 1} floatIntensity={prefersReducedMotion ? 0 : 2}>
                <mesh position={[2, 0, -2]}>
                  <sphereGeometry args={[1.5, 64, 64]} />
                  <MeshDistortMaterial color="#4F46E5" distort={prefersReducedMotion ? 0 : 0.4} speed={prefersReducedMotion ? 0 : 2} roughness={0.2} metalness={0.8} opacity={0.7} transparent />
                </mesh>
              </Float>
              <Float speed={prefersReducedMotion ? 0 : 1.5} rotationIntensity={prefersReducedMotion ? 0 : 0.5} floatIntensity={prefersReducedMotion ? 0 : 1.5}>
                <mesh position={[-2, -1, -3]}>
                  <sphereGeometry args={[2, 64, 64]} />
                  <MeshDistortMaterial color="#0ea5e9" distort={prefersReducedMotion ? 0 : 0.2} speed={prefersReducedMotion ? 0 : 1} roughness={0.4} metalness={0.9} opacity={0.4} transparent />
                </mesh>
              </Float>
            </Suspense>
          </Canvas>
        </div>
      </div>

      <div className={styles.formPane}>
        <div className={styles.contentWrapper}>
        <div className={styles.header}>
          <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <h1 className={styles.title} style={{ cursor: 'pointer' }}>CreatorOS AI</h1>
          </Link>
          <p className={styles.subtitle}>Create a new account.</p>
          <div style={{ marginTop: '0.5rem' }}>
            <Link to="/" style={{ color: '#818cf8', fontSize: '0.875rem', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
              ← Back to Home
            </Link>
          </div>
        </div>

        <Card glass>
          <CardHeader title="Register" />
          <CardContent>
            <form onSubmit={handleSubmit} className={styles.form}>
              {error && (
                <div className={styles.errorBox}>
                  {error}
                </div>
              )}

              <div className="flex gap-4 w-full">
                <div className="w-full">
                  <Input
                    label="First Name"
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="John"
                    required
                  />
                </div>
                <div className="w-full">
                  <Input
                    label="Last Name"
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Doe"
                    required
                  />
                </div>
              </div>

              <Input
                label="Username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="johndoe"
                required
              />

              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />

              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />

              <Button type="submit" fullWidth isLoading={isLoading} className={styles.submitBtn}>
                Sign Up
              </Button>
            </form>

            <div className={styles.footer}>
              Already have an account?{' '}
              <Link to="/login" className={styles.link}>
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>
        </div>
      </div>
    </div>
  );
}
