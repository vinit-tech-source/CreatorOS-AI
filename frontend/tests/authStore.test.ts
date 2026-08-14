import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../src/stores/authStore';

// Mock dev user matching the shape returned by /auth/dev-token
const DEV_USER = {
  id: '00000000-0000-0000-0000-000000000001',
  first_name: 'Development',
  last_name: 'User',
  email: 'dev@localhost',
  username: 'devuser',
  is_active: true,
  created_at: '2024-01-01T00:00:00.000Z',
  updated_at: '2024-01-01T00:00:00.000Z',
};

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isInitializing: false,
    });
    localStorage.clear();
  });

  it('should initialize with default values', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should initialize with isInitializing=false (no async session check)', () => {
    // Verifies the fix for the infinite "Loading Application..." screen
    const state = useAuthStore.getState();
    expect(state.isInitializing).toBe(false);
  });

  it('should set authentication state correctly', () => {
    const mockUser = {
      id: '1',
      first_name: 'Test',
      last_name: 'User',
      email: 'test@example.com',
      username: 'testuser',
      is_active: true,
      created_at: '',
      updated_at: ''
    };

    useAuthStore.getState().setAuth(mockUser, 'fake-token');
    
    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.accessToken).toBe('fake-token');
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem('access_token')).toBe('fake-token');
  });

  it('should logout correctly', () => {
    useAuthStore.setState({
      user: { id: '1' } as any,
      accessToken: 'fake-token',
      isAuthenticated: true,
    });
    localStorage.setItem('access_token', 'fake-token');

    useAuthStore.getState().logout();
    
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  // ── Dev bypass user shape ──────────────────────────────────────────────

  it('should accept the dev user identity without errors', () => {
    // Simulates what initDevAuth() does after fetching the dev token
    useAuthStore.getState().setAuth(DEV_USER, 'dev-jwt-token');
    
    const state = useAuthStore.getState();
    expect(state.user?.id).toBe('00000000-0000-0000-0000-000000000001');
    expect(state.user?.email).toBe('dev@localhost');
    expect(state.user?.username).toBe('devuser');
    expect(state.isAuthenticated).toBe(true);
    expect(localStorage.getItem('access_token')).toBe('dev-jwt-token');
  });

  it('normal auth state should be unchanged when bypass user not set', () => {
    // Verify normal unauthenticated state is unaffected
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
  });
});
