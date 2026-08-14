import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../src/stores/authStore';

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
});
