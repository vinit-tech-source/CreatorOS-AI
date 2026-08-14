import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, CardContent, CardHeader } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { apiClient } from '../../services/api';

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

  return (
    <div className="flex h-screen w-full items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">CreatorOS AI</h1>
          <p className="text-secondary">Create a new account.</p>
        </div>

        <Card glass>
          <CardHeader title="Register" />
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-md text-red-500 text-sm">
                  {error}
                </div>
              )}

              <div className="flex gap-4">
                <Input
                  label="First Name"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="John"
                  required
                />
                <Input
                  label="Last Name"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Doe"
                  required
                />
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

              <Button type="submit" fullWidth isLoading={isLoading} className="mt-2">
                Sign Up
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-secondary">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:underline">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
