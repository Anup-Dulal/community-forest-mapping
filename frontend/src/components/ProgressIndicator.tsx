/**
 * ProgressIndicator component - Real-time progress display with WebSocket updates.
 * Shows progress bar, percentage, estimated time remaining, and cancel button.
 * Requirements: 12.4, 15.1, 15.4, 15.6, 19.1, 19.2, 19.3, 19.4
 */

import React, { useEffect, useState, useRef } from 'react';
import '../styles/ProgressIndicator.css';

interface ProgressUpdate {
  operationId: string;
  operation: string;
  percentage: number;
  estimatedTimeRemaining: number;
  statusMessage: string;
  currentStep: string;
  timestamp: string;
}

interface ProgressIndicatorProps {
  operationId: string;
  operation: string;
  onComplete?: (summary?: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
  showCancelButton?: boolean;
}

/**
 * ProgressIndicator component - Display real-time progress updates.
 * Features:
 * - Real-time progress bar with percentage
 * - Estimated time remaining
 * - Status message updates
 * - Cancel button
 * - WebSocket connection for live updates
 */
const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  operationId,
  operation,
  onComplete,
  onError,
  onCancel,
  showCancelButton = true,
}) => {
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const stompClientRef = useRef<any>(null);
  const subscriptionRef = useRef<any>(null);

  // Format time remaining
  const formatTimeRemaining = (seconds: number): string => {
    if (seconds < 0) return 'Calculating...';
    if (seconds < 60) return `${Math.ceil(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.ceil(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Connect to WebSocket
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        // Use native WebSocket API
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/progress`;

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);

          // Subscribe to progress updates for this operation
          const subscribeMessage = JSON.stringify({
            id: `sub-${operationId}`,
            destination: `/topic/progress/${operationId}`,
          });

          ws.send(subscribeMessage);
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            // Handle error messages
            if (message.status === 'error') {
              if (onError) {
                onError(message.errorMessage);
              }
              return;
            }

            // Handle progress updates
            if (message.percentage !== undefined) {
              setProgress(message);

              // Check for completion
              if (message.percentage >= 100 || message.status === 'completed') {
                if (onComplete) {
                  onComplete(message.summary);
                }
              }
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
          if (onError) {
            onError('WebSocket connection error');
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
        };

        stompClientRef.current = ws;
      } catch (err) {
        console.error('Error connecting to WebSocket:', err);
        setIsConnected(false);
      }
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (stompClientRef.current) {
        stompClientRef.current.close();
      }
    };
  }, [operationId, onComplete, onError]);

  // Handle cancel button
  const handleCancel = async () => {
    setIsCancelling(true);
    try {
      const response = await fetch(`/api/operations/${operationId}/cancel`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to cancel operation');
      }

      if (onCancel) {
        onCancel();
      }
    } catch (err) {
      console.error('Error cancelling operation:', err);
      if (onError) {
        onError('Failed to cancel operation');
      }
    } finally {
      setIsCancelling(false);
    }
  };

  // Show placeholder if no progress yet
  if (!progress) {
    return (
      <div className="progress-indicator">
        <div className="progress-header">
          <h3>{operation}</h3>
          <span className="connection-status" title={isConnected ? 'Connected' : 'Connecting...'}>
            {isConnected ? '🟢' : '🟡'}
          </span>
        </div>
        <div className="progress-bar-container">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '0%' }} />
          </div>
          <span className="progress-percentage">0%</span>
        </div>
        <p className="progress-message">Initializing...</p>
      </div>
    );
  }

  return (
    <div className="progress-indicator">
      {/* Header */}
      <div className="progress-header">
        <h3>{operation}</h3>
        <span className="connection-status" title={isConnected ? 'Connected' : 'Connecting...'}>
          {isConnected ? '🟢' : '🟡'}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress.percentage}%` }}
            role="progressbar"
            aria-valuenow={progress.percentage}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
        <span className="progress-percentage">{progress.percentage}%</span>
      </div>

      {/* Status Message */}
      <p className="progress-message">{progress.statusMessage}</p>

      {/* Current Step */}
      {progress.currentStep && (
        <p className="progress-step">
          <strong>Current Step:</strong> {progress.currentStep}
        </p>
      )}

      {/* Time Remaining */}
      <div className="progress-info">
        <span className="time-remaining">
          <strong>Time Remaining:</strong> {formatTimeRemaining(progress.estimatedTimeRemaining)}
        </span>
      </div>

      {/* Cancel Button */}
      {showCancelButton && progress.percentage < 100 && (
        <div className="progress-actions">
          <button
            className="button secondary"
            onClick={handleCancel}
            disabled={isCancelling}
          >
            {isCancelling ? 'Cancelling...' : 'Cancel'}
          </button>
        </div>
      )}

      {/* Completion Message */}
      {progress.percentage >= 100 && (
        <div className="progress-complete">
          <span className="complete-icon">✓</span>
          <p>Operation completed successfully</p>
        </div>
      )}
    </div>
  );
};

export default ProgressIndicator;
