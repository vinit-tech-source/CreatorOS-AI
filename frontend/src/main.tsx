import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { isDevBypassEnabled, initDevAuth } from './lib/devAuth';
import { ThemeProvider } from './components/ThemeProvider';

async function bootstrap() {
  // Initialise dev auth BEFORE mounting React so the auth store is populated
  // by the time ProtectedRoute checks isAuthenticated.
  // In production builds, isDevBypassEnabled() is always false (dead code).
  if (isDevBypassEnabled()) {
    try {
      await initDevAuth();
    } catch (err) {
      console.error(
        '[DEV AUTH BYPASS] Could not obtain dev token. ' +
        'Make sure the backend is running with DEV_AUTH_BYPASS=true.\n',
        err
      );
      // Continue rendering — app will land on /login as normal
    }
  }

  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <ThemeProvider defaultTheme="dark">
        <App />
      </ThemeProvider>
    </React.StrictMode>,
  );
}

bootstrap();
