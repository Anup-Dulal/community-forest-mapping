/**
 * Unit tests for VerifyBoundaryStep component
 * Tests boundary display, auto-zoom, area calculation, and success notification
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import VerifyBoundaryStep from '../VerifyBoundaryStep';

// Mock Leaflet
vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => ({
      fitBounds: vi.fn(),
      getCenter: vi.fn(() => ({ lat: 0, lng: 0 })),
      getZoom: vi.fn(() => 2),
      addLayer: vi.fn(),
      removeLayer: vi.fn(),
      on: vi.fn(),
      off: vi.fn(),
    })),
    tileLayer: vi.fn(() => ({
      addTo: vi.fn(),
    })),
    geoJSON: vi.fn((data, options) => ({
      addTo: vi.fn(),
      getBounds: vi.fn(() => ({
        isValid: vi.fn(() => true),
      })),
      bindPopup: vi.fn(),
    })),
    control: {
      layers: vi.fn(() => ({
        addTo: vi.fn(),
      })),
      zoom: vi.fn(() => ({
        addTo: vi.fn(),
      })),
    },
    Icon: {
      Default: {
        prototype: {},
        mergeOptions: vi.fn(),
      },
    },
  },
}));

// Mock the app store
vi.mock('../store/appStore', () => ({
  useAppStore: vi.fn((selector) => {
    const store = {
      setMapCenter: vi.fn(),
      setMapZoom: vi.fn(),
      setLayerVisibility: vi.fn(),
    };
    return selector(store);
  }),
}));

describe('VerifyBoundaryStep', () => {
  const mockOnComplete = vi.fn();
  const mockShapefileId = '550e8400-e29b-41d4-a716-446655440000';

  const mockBoundaryData = {
    geometry: {
      type: 'Feature',
      geometry: {
        type: 'Polygon',
        coordinates: [
          [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
            [0, 0],
          ],
        ],
      },
      properties: { name: 'Test Boundary' },
    },
    area: 12321,
    boundingBox: {
      minLat: 0,
      maxLat: 1,
      minLon: 0,
      maxLon: 1,
    },
  };

  beforeEach(() => {
    // Setup window mock for map instance
    (window as any).__mapInstance = {
      fitBounds: vi.fn(),
      getCenter: vi.fn(() => ({ lat: 0, lng: 0 })),
      getZoom: vi.fn(() => 2),
      addLayer: vi.fn(),
      removeLayer: vi.fn(),
    };
    (window as any).__mapReady = true;
    (window as any).__mapAPI = {
      addLayer: vi.fn(),
      removeLayer: vi.fn(),
      fitBounds: vi.fn(),
      getMap: vi.fn(() => (window as any).__mapInstance),
    };

    // Mock fetch
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should render loading state initially', () => {
    (global.fetch as any).mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => mockBoundaryData,
              }),
            100
          )
        )
    );

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    expect(screen.getByText('Loading boundary geometry...')).toBeInTheDocument();
  });

  it('should fetch boundary geometry on mount', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundaryData,
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `/api/shapefile/${mockShapefileId}/boundary`
      );
    });
  });

  it('should display boundary statistics after loading', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundaryData,
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('Boundary Statistics')).toBeInTheDocument();
      expect(screen.getByText(/12321\.00 km²/)).toBeInTheDocument();
    });
  });

  it('should show success notification', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundaryData,
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('Boundary loaded successfully')).toBeInTheDocument();
    });
  });

  it('should display error message on fetch failure', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Not found' }),
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch boundary geometry')).toBeInTheDocument();
    });
  });

  it('should call onComplete when proceeding', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundaryData,
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('Proceed to Next Step')).toBeInTheDocument();
    });

    const proceedButton = screen.getByText('Proceed to Next Step');
    fireEvent.click(proceedButton);

    expect(mockOnComplete).toHaveBeenCalled();
  });

  it('should disable proceed button when loading', () => {
    (global.fetch as any).mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => mockBoundaryData,
              }),
            1000
          )
        )
    );

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    const proceedButton = screen.getByText('Proceed to Next Step');
    expect(proceedButton).toBeDisabled();
  });

  it('should disable proceed button on error', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Not found' }),
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      const proceedButton = screen.getByText('Proceed to Next Step');
      expect(proceedButton).toBeDisabled();
    });
  });

  it('should display bounding box information', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundaryData,
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('Bounding Box')).toBeInTheDocument();
      expect(screen.getByText(/0\.0000° to 1\.0000°N/)).toBeInTheDocument();
    });
  });

  it('should have re-upload button', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoundaryData,
    });

    render(
      <VerifyBoundaryStep shapefileId={mockShapefileId} onComplete={mockOnComplete} />
    );

    await waitFor(() => {
      expect(screen.getByText('Re-upload')).toBeInTheDocument();
    });
  });
});
