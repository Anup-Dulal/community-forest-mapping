/**
 * ErrorNotification component - Displays error messages with troubleshooting suggestions.
 * Requirements: 12.1, 12.2, 12.3, 24.2, 24.3, 24.6
 */

import React, { useState, useEffect } from 'react';
import '../styles/ErrorNotification.css';

interface ErrorNotificationProps {
  error: string;
  errorType?: 'network' | 'validation' | 'processing' | 'export' | 'unknown';
  retryAttempt?: number;
  maxRetries?: number;
  onRetry?: () => void;
  onDismiss?: () => void;
  autoClose?: boolean;
  autoCloseDuration?: number;
}

const ErrorNotification: React.FC<ErrorNotificationProps> = ({
  error,
  errorType = 'unknown',
  retryAttempt = 0,
  maxRetries = 3,
  onRetry,
  onDismiss,
  autoClose = false,
  autoCloseDuration = 5000,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isAutoClosing, setIsAutoClosing] = useState(false);

  useEffect(() => {
    if (autoClose && isVisible) {
      setIsAutoClosing(true);
      const timer = setTimeout(() => {
        handleDismiss();
      }, autoCloseDuration);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseDuration, isVisible]);

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  const handleRetry = () => {
    onRetry?.();
  };

  if (!isVisible) return null;

  const getTroubleshootingSteps = (): string[] => {
    switch (errorType) {
      case 'network':
        return [
          'Check your internet connection',
          'Try uploading again',
          'If the problem persists, try a different network',
        ];
      case 'validation':
        return [
          'Ensure all required shapefile components are present (.shp, .shx, .dbf, .prj)',
          'Check that the shapefile is not corrupted',
          'Try uploading individual files instead of an archive',
        ];
      case 'processing':
        return [
          'The file may be too large - try a smaller shapefile',
          'Check that the shapefile geometry is valid',
          'Try uploading again',
        ];
      case 'export':
        return [
          'Check that you have sufficient disk space',
          'Try exporting in a different format',
          'Try exporting a smaller area',
        ];
      default:
        return [
          'Try the operation again',
          'Check the error message for more details',
          'Contact support if the problem persists',
        ];
    }
  };

  const canRetry = retryAttempt < maxRetries && onRetry;
  const troubleshootingSteps = getTroubleshootingSteps();

  return (
    <div className={`error-notification ${errorType} ${isAutoClosing ? 'auto-closing' : ''}`}>
      <div className="error-header">
        <span className="error-icon">❌</span>
        <div className="error-content">
          <h3 className="error-title">Error</h3>
          <p className="error-message">{error}</p>
        </div>
        <button
          className="close-button"
          onClick={handleDismiss}
          aria-label="Dismiss error"
        >
          ✕
        </button>
      </div>

      {/* Retry Attempt Counter */}
      {retryAttempt > 0 && (
        <div className="retry-info">
          <span className="retry-badge">Retry {retryAttempt} of {maxRetries}</span>
        </div>
      )}

      {/* Troubleshooting Steps */}
      <div className="troubleshooting">
        <h4 className="troubleshooting-title">Troubleshooting Steps:</h4>
        <ol className="troubleshooting-list">
          {troubleshootingSteps.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ol>
      </div>

      {/* Action Buttons */}
      <div className="error-actions">
        {canRetry && (
          <button
            className="button primary"
            onClick={handleRetry}
            aria-label={`Retry (attempt ${retryAttempt + 1} of ${maxRetries})`}
          >
            Retry
          </button>
        )}
        <button
          className="button secondary"
          onClick={handleDismiss}
          aria-label="Dismiss error"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
};

export default ErrorNotification;
