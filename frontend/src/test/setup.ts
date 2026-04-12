import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IndexedDB
class MockIDBDatabase {
  objectStoreNames = { contains: () => false };
  transaction() {
    return new MockIDBTransaction();
  }
}

class MockIDBTransaction {
  oncomplete: (() => void) | null = null;
  onerror: (() => void) | null = null;

  objectStore() {
    return new MockIDBObjectStore();
  }
}

class MockIDBObjectStore {
  put() {
    return new MockIDBRequest();
  }
  get() {
    return new MockIDBRequest();
  }
  getAll() {
    return new MockIDBRequest();
  }
  delete() {
    return new MockIDBRequest();
  }
  clear() {
    return new MockIDBRequest();
  }
}

class MockIDBRequest {
  onsuccess: ((event: any) => void) | null = null;
  onerror: (() => void) | null = null;
  result: any = null;

  constructor() {
    setTimeout(() => {
      if (this.onsuccess) {
        this.onsuccess({ target: this });
      }
    }, 0);
  }
}

class MockIDBOpenDBRequest extends MockIDBRequest {
  onupgradeneeded: ((event: any) => void) | null = null;

  constructor() {
    super();
    this.result = new MockIDBDatabase();
  }
}

Object.defineProperty(window, 'indexedDB', {
  writable: true,
  value: {
    open: vi.fn(() => new MockIDBOpenDBRequest()),
  },
});
