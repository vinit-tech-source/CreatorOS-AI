import { FallbackProps } from 'react-error-boundary';
import { AlertTriangle, RefreshCcw } from 'lucide-react';
import './GlobalErrorFallback.css';

export function GlobalErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="global-error-container">
      <div className="global-error-card">
        <div className="global-error-icon-wrapper">
          <AlertTriangle className="global-error-icon" size={48} />
        </div>
        <h2 className="global-error-title">Oops! Something went wrong</h2>
        <p className="global-error-message">
          We encountered an unexpected error. Please try refreshing the page or contact support if the problem persists.
        </p>
        
        {/* Only show technical details in development or if explicitly needed */}
        {import.meta.env?.DEV && error instanceof Error && error.message && (
          <div className="global-error-details">
            <p><strong>Error Details:</strong></p>
            <code>{error.message}</code>
          </div>
        )}
        
        <button 
          onClick={resetErrorBoundary}
          className="global-error-button"
        >
          <RefreshCcw size={16} />
          <span>Try Again</span>
        </button>
      </div>
    </div>
  );
}
