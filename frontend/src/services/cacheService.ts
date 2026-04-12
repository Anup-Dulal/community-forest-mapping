/**
 * CacheService - Manages offline caching using IndexedDB and localStorage
 * Handles satellite imagery, rasters, and metadata caching with versioning
 */

const DB_NAME = 'cfm-cache';
const DB_VERSION = 1;
const STORES = {
  SATELLITE_IMAGERY: 'satelliteImagery',
  RASTERS: 'rasters',
  METADATA: 'metadata',
  SYNC_QUEUE: 'syncQueue',
};

export interface CacheMetadata {
  id: string;
  key: string;
  version: number;
  timestamp: number;
  size: number;
  type: 'satellite' | 'raster' | 'metadata';
}

export interface SyncQueueItem {
  id: string;
  operation: 'upload' | 'generate' | 'export';
  data: any;
  timestamp: number;
  retries: number;
  status: 'pending' | 'syncing' | 'failed';
}

class CacheService {
  private db: IDBDatabase | null = null;
  private isOnline: boolean = navigator.onLine;
  private syncInProgress: boolean = false;
  private listeners: Set<(status: CacheStatus) => void> = new Set();

  constructor() {
    this.initializeDB();
    this.setupOnlineListener();
  }

  /**
   * Initialize IndexedDB database
   */
  private async initializeDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create object stores if they don't exist
        if (!db.objectStoreNames.contains(STORES.SATELLITE_IMAGERY)) {
          db.createObjectStore(STORES.SATELLITE_IMAGERY, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.RASTERS)) {
          db.createObjectStore(STORES.RASTERS, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.METADATA)) {
          db.createObjectStore(STORES.METADATA, { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          db.createObjectStore(STORES.SYNC_QUEUE, { keyPath: 'id' });
        }
      };
    });
  }

  /**
   * Setup online/offline listener
   */
  private setupOnlineListener(): void {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.notifyListeners();
      this.syncQueuedOperations();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.notifyListeners();
    });
  }

  /**
   * Cache satellite imagery
   */
  async cacheSatelliteImagery(
    id: string,
    imageData: Blob,
    metadata: any
  ): Promise<void> {
    if (!this.db) await this.initializeDB();

    const transaction = this.db!.transaction(
      [STORES.SATELLITE_IMAGERY, STORES.METADATA],
      'readwrite'
    );

    const imageStore = transaction.objectStore(STORES.SATELLITE_IMAGERY);
    const metadataStore = transaction.objectStore(STORES.METADATA);

    const cacheEntry = {
      id,
      data: imageData,
      timestamp: Date.now(),
    };

    const metadataEntry: CacheMetadata = {
      id: `meta-${id}`,
      key: id,
      version: 1,
      timestamp: Date.now(),
      size: imageData.size,
      type: 'satellite',
    };

    return new Promise((resolve, reject) => {
      imageStore.put(cacheEntry);
      metadataStore.put(metadataEntry);

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Get cached satellite imagery
   */
  async getSatelliteImagery(id: string): Promise<Blob | null> {
    if (!this.db) await this.initializeDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(
        [STORES.SATELLITE_IMAGERY],
        'readonly'
      );
      const store = transaction.objectStore(STORES.SATELLITE_IMAGERY);
      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result?.data || null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Cache raster data
   */
  async cacheRaster(
    id: string,
    rasterData: Blob,
    type: 'slope' | 'aspect' | 'dem'
  ): Promise<void> {
    if (!this.db) await this.initializeDB();

    const transaction = this.db!.transaction(
      [STORES.RASTERS, STORES.METADATA],
      'readwrite'
    );

    const rasterStore = transaction.objectStore(STORES.RASTERS);
    const metadataStore = transaction.objectStore(STORES.METADATA);

    const cacheEntry = {
      id,
      type,
      data: rasterData,
      timestamp: Date.now(),
    };

    const metadataEntry: CacheMetadata = {
      id: `meta-${id}`,
      key: id,
      version: 1,
      timestamp: Date.now(),
      size: rasterData.size,
      type: 'raster',
    };

    return new Promise((resolve, reject) => {
      rasterStore.put(cacheEntry);
      metadataStore.put(metadataEntry);

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Get cached raster
   */
  async getRaster(id: string): Promise<Blob | null> {
    if (!this.db) await this.initializeDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORES.RASTERS], 'readonly');
      const store = transaction.objectStore(STORES.RASTERS);
      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result?.data || null);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Cache metadata in localStorage
   */
  cacheMetadata(key: string, data: any, version: number = 1): void {
    const cacheEntry = {
      data,
      version,
      timestamp: Date.now(),
    };
    localStorage.setItem(`cfm-meta-${key}`, JSON.stringify(cacheEntry));
  }

  /**
   * Get cached metadata
   */
  getMetadata(key: string): any | null {
    const cached = localStorage.getItem(`cfm-meta-${key}`);
    if (!cached) return null;

    const entry = JSON.parse(cached);
    return entry.data;
  }

  /**
   * Invalidate cache by version
   */
  invalidateCacheByVersion(key: string, currentVersion: number): void {
    const cached = localStorage.getItem(`cfm-meta-${key}`);
    if (!cached) return;

    const entry = JSON.parse(cached);
    if (entry.version < currentVersion) {
      localStorage.removeItem(`cfm-meta-${key}`);
    }
  }

  /**
   * Queue operation for sync when offline
   */
  async queueOperation(
    operation: 'upload' | 'generate' | 'export',
    data: any
  ): Promise<string> {
    if (!this.db) await this.initializeDB();

    const id = `${operation}-${Date.now()}-${Math.random()}`;
    const queueItem: SyncQueueItem = {
      id,
      operation,
      data,
      timestamp: Date.now(),
      retries: 0,
      status: 'pending',
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORES.SYNC_QUEUE], 'readwrite');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);
      store.put(queueItem);

      transaction.oncomplete = () => resolve(id);
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Get queued operations
   */
  async getQueuedOperations(): Promise<SyncQueueItem[]> {
    if (!this.db) await this.initializeDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORES.SYNC_QUEUE], 'readonly');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result.filter((item) => item.status === 'pending'));
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Update queued operation status
   */
  async updateQueueItemStatus(
    id: string,
    status: 'pending' | 'syncing' | 'failed',
    retries?: number
  ): Promise<void> {
    if (!this.db) await this.initializeDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORES.SYNC_QUEUE], 'readwrite');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);
      const getRequest = store.get(id);

      getRequest.onsuccess = () => {
        const item = getRequest.result;
        if (item) {
          item.status = status;
          if (retries !== undefined) item.retries = retries;
          store.put(item);
        }
      };

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Remove queued operation
   */
  async removeQueuedOperation(id: string): Promise<void> {
    if (!this.db) await this.initializeDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([STORES.SYNC_QUEUE], 'readwrite');
      const store = transaction.objectStore(STORES.SYNC_QUEUE);
      store.delete(id);

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Sync queued operations when online
   */
  async syncQueuedOperations(): Promise<void> {
    if (!this.isOnline || this.syncInProgress) return;

    this.syncInProgress = true;
    this.notifyListeners();

    try {
      const queuedOps = await this.getQueuedOperations();

      for (const op of queuedOps) {
        await this.updateQueueItemStatus(op.id, 'syncing');

        try {
          // Sync operation would be handled by the API service
          // For now, just mark as complete
          await this.removeQueuedOperation(op.id);
        } catch (error) {
          const newRetries = op.retries + 1;
          if (newRetries >= 3) {
            await this.updateQueueItemStatus(op.id, 'failed', newRetries);
          } else {
            await this.updateQueueItemStatus(op.id, 'pending', newRetries);
          }
        }
      }
    } finally {
      this.syncInProgress = false;
      this.notifyListeners();
    }
  }

  /**
   * Get cache status
   */
  getCacheStatus(): CacheStatus {
    return {
      isOnline: this.isOnline,
      isSyncing: this.syncInProgress,
      cacheAvailable: this.db !== null,
    };
  }

  /**
   * Subscribe to cache status changes
   */
  subscribe(listener: (status: CacheStatus) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify all listeners of status change
   */
  private notifyListeners(): void {
    const status = this.getCacheStatus();
    this.listeners.forEach((listener) => listener(status));
  }

  /**
   * Clear all cache
   */
  async clearCache(): Promise<void> {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(
        [
          STORES.SATELLITE_IMAGERY,
          STORES.RASTERS,
          STORES.METADATA,
          STORES.SYNC_QUEUE,
        ],
        'readwrite'
      );

      transaction.objectStore(STORES.SATELLITE_IMAGERY).clear();
      transaction.objectStore(STORES.RASTERS).clear();
      transaction.objectStore(STORES.METADATA).clear();
      transaction.objectStore(STORES.SYNC_QUEUE).clear();

      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  }

  /**
   * Get cache size
   */
  async getCacheSize(): Promise<number> {
    if (!this.db) return 0;

    let totalSize = 0;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(
        [STORES.SATELLITE_IMAGERY, STORES.RASTERS],
        'readonly'
      );

      const imageStore = transaction.objectStore(STORES.SATELLITE_IMAGERY);
      const rasterStore = transaction.objectStore(STORES.RASTERS);

      const imageRequest = imageStore.getAll();
      imageRequest.onsuccess = () => {
        totalSize += imageRequest.result.reduce(
          (sum, item) => sum + (item.data?.size || 0),
          0
        );
      };

      const rasterRequest = rasterStore.getAll();
      rasterRequest.onsuccess = () => {
        totalSize += rasterRequest.result.reduce(
          (sum, item) => sum + (item.data?.size || 0),
          0
        );
      };

      transaction.oncomplete = () => resolve(totalSize);
      transaction.onerror = () => reject(transaction.error);
    });
  }
}

export interface CacheStatus {
  isOnline: boolean;
  isSyncing: boolean;
  cacheAvailable: boolean;
}

// Export singleton instance
export const cacheService = new CacheService();
