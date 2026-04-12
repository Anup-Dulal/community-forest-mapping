/**
 * Unit tests for OfflineIndicator component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OfflineIndicator } from '../OfflineIndicator';
import { cacheService } from '../../services/cacheService';

describe('OfflineIndicator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should not render when online and not syncing', () => {
    const { container } = render(<OfflineIndicator />);
    const indicator = container.querySelector('.offline-indicator');

    // Should either not exist or be empty
    if (indicator) {
      expect(indicator.children.length).toBe(0);
    }
  });

  it('should render offline status when offline', () => {
    // Mock offline status
    vi.spyOn(cacheService, 'getCacheStatus').mockReturnValue({
      isOnline: false,
      isSyncing: false,
      cacheAvailable: true,
    });

    render(<OfflineIndicator />);

    expect(screen.getByText('Offline Mode')).toBeInTheDocument();
    expect(screen.getByText('Cached data available')).toBeInTheDocument();
  });

  it('should render sync status when syncing', () => {
    vi.spyOn(cacheService, 'getCacheStatus').mockReturnValue({
      isOnline: true,
      isSyncing: true,
      cacheAvailable: true,
    });

    render(<OfflineIndicator />);

    expect(screen.getByText('Syncing...')).toBeInTheDocument();
  });

  it('should have correct CSS classes', () => {
    vi.spyOn(cacheService, 'getCacheStatus').mockReturnValue({
      isOnline: false,
      isSyncing: false,
      cacheAvailable: true,
    });

    const { container } = render(<OfflineIndicator />);

    expect(container.querySelector('.offline-indicator')).toBeInTheDocument();
    expect(container.querySelector('.offline-status')).toBeInTheDocument();
  });

  it('should update when cache status changes', () => {
    const { rerender } = render(<OfflineIndicator />);

    // Initially online
    expect(screen.queryByText('Offline Mode')).not.toBeInTheDocument();

    // Mock offline status
    vi.spyOn(cacheService, 'getCacheStatus').mockReturnValue({
      isOnline: false,
      isSyncing: false,
      cacheAvailable: true,
    });

    rerender(<OfflineIndicator />);

    expect(screen.getByText('Offline Mode')).toBeInTheDocument();
  });
});
