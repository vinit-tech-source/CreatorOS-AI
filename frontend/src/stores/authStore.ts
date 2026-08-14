import { create } from 'zustand';
import { User } from '../types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  setInitializing: (status: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isInitializing: true, // Used when checking session on load

  setAuth: (user, token) => {
    localStorage.setItem('access_token', token);
    set({ user, accessToken: token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  setInitializing: (status) => set({ isInitializing: status }),
}));
