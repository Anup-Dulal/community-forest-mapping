/**
 * OfflineIndicator - Displays offline status and sync information
 */

import React, { useState, useEffect } from 'react';
import { cacheService, CacheStatus } from '../services/cacheService';
import '../styles/OfflineIndicator.css';

export const OfflineIndicator: React.FC = () => {
  const [cacheStatus, setCacheStatus] = useState<CacheStatus>({
    isOnline: navigator.onLine,
    isSyncing: false,
    cacheAvailable: false,
  });

  useEffect(() => {
    const unsubscribe = cacheService.subscribe((status) => {
      setCacheStatus(status);
    });

    return unsubscribe;
  }, []);

  if (cacheStatus.isOnline && !cacheStatus.isSyncing) {
    return null;
  }

  return (
    <div className="offline-indicator">
      {!cacheStatus.isOnline && (
        <div className="offline-status">
          <span className="offline-icon">📡</span>
          <span className="offline-text">Offline Mode</span>
          {cacheStatus.cacheAvailable && (
            <span className="cache-available">Cached data available</span>
          )}
        </div>
      )}

      {cacheStatus.isSyncing && (
        <div className="sync-status">
          <span className="sync-icon">🔄</span>
          <span className="sync-text">Syncing...</span>
        </div>
      )}
    </div>
  );
};
