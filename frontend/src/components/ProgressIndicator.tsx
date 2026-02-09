import React, { useEffect, useState } from 'react';
import { appStore } from '../store/appStore';
import '../styles/ProgressIndicator.css';

interface ProgressUpdate {
  operation: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  message: string;
}

/**
 * ProgressIndicator component displays progress for long-running operations.
 * Shows operation name, progress percentage, and status messages.
 */
export const ProgressIndicator: React.FC = () => {
  const [progressUpdates, setProgressUpdates] = useState<ProgressUpdate[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  // Subscribe to app store updates
  useEffect(() => {
    const unsubscribe = appStore.subscribe(
      (state) => state.analysisStatus,
      (analysisStatus) => {
        if (analysisStatus && analysisStatus.isProcessing) {
          setIsVisible(true);
          setProgressUpdates([
            {
              operation: analysisStatus.currentOperation || 'Processing',
              progress: analysisStatus.progress || 0,
              status: 'in_progress',
              message: analysisStatus.message || 'Processing...'
            }
          ]);
        } else if (analysisStatus && analysisStatus.isComplete) {
          setProgressUpdates([
            {
              operation: analysisStatus.currentOperation || 'Complete',
              progress: 100,
              status: 'completed',
              message: analysisStatus.message || 'Operation completed successfully'
            }
          ]);
          // Auto-hide after 3 seconds
          setTimeout(() => setIsVisible(false), 3000);
        } else if (analysisStatus && analysisStatus.error) {
          setProgressUpdates([
            {
              operation: analysisStatus.currentOperation || 'Error',
              progress: analysisStatus.progress || 0,
              status: 'error',
              message: analysisStatus.error
            }
          ]);
        }
      }
    );

    return () => unsubscribe();
  }, []);

  if (!isVisible || progressUpdates.length === 0) {
    return null;
  }

  const currentUpdate = progressUpdates[progressUpdates.length - 1];

  return (
    <div className={`progress-indicator progress-${currentUpdate.status}`}>
      <div className="progress-header">
        <h3 className="progress-operation">{currentUpdate.operation}</h3>
        <span className="progress-percentage">{currentUpdate.progress}%</span>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar-fill"
          style={{ width: `${currentUpdate.progress}%` }}
        />
      </div>

      <p className="progress-message">{currentUpdate.message}</p>

      {currentUpdate.status === 'in_progress' && (
        <div className="progress-spinner">
          <div className="spinner" />
        </div>
      )}

      {currentUpdate.status === 'completed' && (
        <div className="progress-icon">
          <span className="checkmark">✓</span>
        </div>
      )}

      {currentUpdate.status === 'error' && (
        <div className="progress-icon">
          <span className="error-mark">✕</span>
        </div>
      )}
    </div>
  );
};

export default ProgressIndicator;
