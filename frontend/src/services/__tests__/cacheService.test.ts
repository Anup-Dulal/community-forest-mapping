/**
 * Unit tests for CacheService
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { cacheService, CacheMetadata, SyncQueueItem } from '../cacheService';

describe('CacheService', () => {
  beforeEach(async () => {
    // Clear cache before each test
    await cacheService.clearCache();
    localStorage.clear();
  });

  afterEach(async () => {
    await cacheService.clearCache();
    localStorage.clear();
  });

  describe('Metadata Caching', () => {
    it('should cache metadata in localStorage', () => {
      const testData = { id: '123', name: 'Test Boundary' };
      cacheService.cacheMetadata('boundary-1', testData, 1);

      const retrieved = cacheService.getMetadata('boundary-1');
      expect(retrieved).toEqual(testData);
    });

    it('should return null for non-existent metadata', () => {
      const retrieved = cacheService.getMetadata('non-existent');
      expect(retrieved).toBeNull();
    });

    it('should invalidate cache by version', () => {
      const testData = { id: '123', name: 'Test' };
      cacheService.cacheMetadata('boundary-1', testData, 1);

      // Invalidate with higher version
      cacheService.invalidateCacheByVersion('boundary-1', 2);

      const retrieved = cacheService.getMetadata('boundary-1');
      expect(retrieved).toBeNull();
    });

    it('should not invalidate cache with same version', () => {
      const testData = { id: '123', name: 'Test' };
      cacheService.cacheMetadata('boundary-1', testData, 1);

      // Try to invalidate with same version
      cacheService.invalidateCacheByVersion('boundary-1', 1);

      const retrieved = cacheService.getMetadata('boundary-1');
      expect(retrieved).toEqual(testData);
    });
  });

  describe('Satellite Imagery Caching', () => {
    it('should cache satellite imagery', async () => {
      const imageBlob = new Blob(['test image data'], { type: 'image/png' });
      const metadata = { source: 'GoogleEarthEngine', date: '2024-01-01' };

      await cacheService.cacheSatelliteImagery('sat-1', imageBlob, metadata);

      const retrieved = await cacheService.getSatelliteImagery('sat-1');
      expect(retrieved).not.toBeNull();
      expect(retrieved?.size).toBe(imageBlob.size);
    });

    it('should return null for non-existent satellite imagery', async () => {
      const retrieved = await cacheService.getSatelliteImagery('non-existent');
      expect(retrieved).toBeNull();
    });
  });

  describe('Raster Caching', () => {
    it('should cache raster data', async () => {
      const rasterBlob = new Blob(['raster data'], { type: 'application/octet-stream' });

      await cacheService.cacheRaster('raster-1', rasterBlob, 'slope');

      const retrieved = await cacheService.getRaster('raster-1');
      expect(retrieved).not.toBeNull();
      expect(retrieved?.size).toBe(rasterBlob.size);
    });

    it('should return null for non-existent raster', async () => {
      const retrieved = await cacheService.getRaster('non-existent');
      expect(retrieved).toBeNull();
    });
  });

  describe('Sync Queue Operations', () => {
    it('should queue operation', async () => {
      const operationData = { shapefileId: '123', type: 'compartment' };
      const id = await cacheService.queueOperation('generate', operationData);

      expect(id).toBeDefined();
      expect(typeof id).toBe('string');
    });

    it('should retrieve queued operations', async () => {
      const op1 = { shapefileId: '123', type: 'compartment' };
      const op2 = { shapefileId: '456', type: 'slope' };

      const id1 = await cacheService.queueOperation('generate', op1);
      const id2 = await cacheService.queueOperation('generate', op2);

      const queued = await cacheService.getQueuedOperations();
      expect(queued.length).toBe(2);
      expect(queued.map((q) => q.id)).toContain(id1);
      expect(queued.map((q) => q.id)).toContain(id2);
    });

    it('should update queue item status', async () => {
      const operationData = { shapefileId: '123' };
      const id = await cacheService.queueOperation('generate', operationData);

      await cacheService.updateQueueItemStatus(id, 'syncing', 1);

      const queued = await cacheService.getQueuedOperations();
      // Should not include syncing items
      expect(queued.map((q) => q.id)).not.toContain(id);
    });

    it('should remove queued operation', async () => {
      const operationData = { shapefileId: '123' };
      const id = await cacheService.queueOperation('generate', operationData);

      await cacheService.removeQueuedOperation(id);

      const queued = await cacheService.getQueuedOperations();
      expect(queued.map((q) => q.id)).not.toContain(id);
    });
  });

  describe('Cache Status', () => {
    it('should return cache status', () => {
      const status = cacheService.getCacheStatus();

      expect(status).toHaveProperty('isOnline');
      expect(status).toHaveProperty('isSyncing');
      expect(status).toHaveProperty('cacheAvailable');
      expect(typeof status.isOnline).toBe('boolean');
      expect(typeof status.isSyncing).toBe('boolean');
      expect(typeof status.cacheAvailable).toBe('boolean');
    });

    it('should notify listeners of status changes', (done) => {
      const listener = vi.fn();
      const unsubscribe = cacheService.subscribe(listener);

      // Listener should be called at least once
      setTimeout(() => {
        expect(listener).toHaveBeenCalled();
        unsubscribe();
        done();
      }, 100);
    });

    it('should unsubscribe listener', (done) => {
      const listener = vi.fn();
      const unsubscribe = cacheService.subscribe(listener);

      unsubscribe();

      setTimeout(() => {
        const callCount = listener.mock.calls.length;
        // Listener should not be called after unsubscribe
        setTimeout(() => {
          expect(listener.mock.calls.length).toBe(callCount);
          done();
        }, 100);
      }, 100);
    });
  });

  describe('Cache Size', () => {
    it('should calculate cache size', async () => {
      const imageBlob = new Blob(['test image data'], { type: 'image/png' });
      await cacheService.cacheSatelliteImagery('sat-1', imageBlob, {});

      const size = await cacheService.getCacheSize();
      expect(size).toBeGreaterThan(0);
    });

    it('should return 0 for empty cache', async () => {
      const size = await cacheService.getCacheSize();
      expect(size).toBe(0);
    });
  });

  describe('Clear Cache', () => {
    it('should clear all cache', async () => {
      const imageBlob = new Blob(['test'], { type: 'image/png' });
      await cacheService.cacheSatelliteImagery('sat-1', imageBlob, {});
      cacheService.cacheMetadata('meta-1', { test: 'data' });

      await cacheService.clearCache();

      const image = await cacheService.getSatelliteImagery('sat-1');
      const meta = cacheService.getMetadata('meta-1');

      expect(image).toBeNull();
      expect(meta).toBeNull();
    });
  });
});
