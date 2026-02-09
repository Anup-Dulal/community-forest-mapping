/**
 * StatusDisplay component - Displays DEM download, analysis progress, and error messages.
 */

import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/appStore';
import '../styles/StatusDisplay.css';

const StatusDisplay: React.FC = () => {
  const uploadStatus = useAppStore((state) => state.uploadStatus);
  const demStatus = useAppStore((state) => state.demStatus);
  const analysisStatus = useAppStore((state) => state.analysisStatus);
  const [notifications, setNotifications] = useState<
    Array<{ id: string; type: 'success' | 'error' | 'info'; message: string }>
  >([]);

  // Add notifications when status changes
  useEffect(() => {
    if (uploadStatus.status === 'success' && uploadStatus.message) {
      addNotification('success', uploadStatus.message);
    } else if (uploadStatus.status === 'error' && uploadStatus.message) {
      addNotification('error', uploadStatus.message);
    }
  }, [uploadStatus]);

  useEffect(() => {
    if (demStatus.status === 'complete' && demStatus.message) {
      addNotification('success', demStatus.message);
    } else if (demStatus.status === 'error' && demStatus.message) {
      addNotification('error', demStatus.message);
    }
  }, [demStatus]);

  useEffect(() => {
    if (analysisStatus.status === 'complete' && analysisStatus.message) {
      addNotification('success', analysisStatus.message);
    } else if (analysisStatus.status === 'error' && analysisStatus.message) {
      addNotification('error', analysisStatus.message);
    }
  }, [analysisStatus]);

  const addNotification = (
    type: 'success' | 'error' | 'info',
    message: string
  ) => {
    const id = Date.now().toString();
    setNotifications((prev) => [...prev, { id, type, message }]);

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      removeNotification(id);
    }, 5000);
  };

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <div className="status-display">
      {/* Notifications */}
      <div className="notifications-container">
        {notifications.map((notification) => (
          <div
            key={notification.id}
            className={`notification notification-${notification.type}`}
          >
            <div className="notification-content">
              <span className="notification-icon">
                {notification.type === 'success' && '✓'}
                {notification.type === 'error' && '✕'}
                {notification.type === 'info' && 'ℹ'}
              </span>
              <span className="notification-message">{notification.message}</span>
            </div>
            <button
              className="notification-close"
              onClick={() => removeNotification(notification.id)}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Progress Indicators */}
      <div className="progress-indicators">
        {/* Upload Progress */}
        {uploadStatus.status === 'uploading' && uploadStatus.progress !== undefined && (
          <div className="progress-item">
            <div className="progress-label">Upload Progress</div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${uploadStatus.progress}%` }}
              ></div>
            </div>
            <div className="progress-text">{uploadStatus.progress}%</div>
          </div>
        )}

        {/* DEM Progress */}
        {(demStatus.status === 'downloading' || demStatus.status === 'clipping') &&
          demStatus.progress !== undefined && (
            <div className="progress-item">
              <div className="progress-label">
                {demStatus.status === 'downloading' ? 'DEM Download' : 'DEM Clipping'}
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${demStatus.progress}%` }}
                ></div>
              </div>
              <div className="progress-text">{demStatus.progress}%</div>
            </div>
          )}

        {/* Analysis Progress */}
        {analysisStatus.status === 'processing' &&
          analysisStatus.progress !== undefined && (
            <div className="progress-item">
              <div className="progress-label">Analysis Progress</div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${analysisStatus.progress}%` }}
                ></div>
              </div>
              <div className="progress-text">{analysisStatus.progress}%</div>
            </div>
          )}
      </div>

      {/* Status Summary */}
      <div className="status-summary">
        <div className="status-item">
          <span className="status-icon">📁</span>
          <span className="status-text">
            Upload:{' '}
            <span className={`status-value ${uploadStatus.status}`}>
              {uploadStatus.status === 'idle' && 'Ready'}
              {uploadStatus.status === 'uploading' && 'Uploading...'}
              {uploadStatus.status === 'success' && 'Complete'}
              {uploadStatus.status === 'error' && 'Error'}
            </span>
          </span>
        </div>

        <div className="status-item">
          <span className="status-icon">⛰️</span>
          <span className="status-text">
            DEM:{' '}
            <span className={`status-value ${demStatus.status}`}>
              {demStatus.status === 'idle' && 'Ready'}
              {demStatus.status === 'downloading' && 'Downloading...'}
              {demStatus.status === 'clipping' && 'Clipping...'}
              {demStatus.status === 'complete' && 'Complete'}
              {demStatus.status === 'error' && 'Error'}
            </span>
          </span>
        </div>

        <div className="status-item">
          <span className="status-icon">⚙️</span>
          <span className="status-text">
            Analysis:{' '}
            <span className={`status-value ${analysisStatus.status}`}>
              {analysisStatus.status === 'idle' && 'Ready'}
              {analysisStatus.status === 'processing' && 'Processing...'}
              {analysisStatus.status === 'complete' && 'Complete'}
              {analysisStatus.status === 'error' && 'Error'}
            </span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default StatusDisplay;
