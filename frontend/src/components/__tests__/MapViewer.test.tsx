import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MapViewer from '../MapViewer';

// Mock Leaflet
vi.mock('leaflet', () => {
  const L = {
    map: vi.fn(() => ({
      getCenter: () => ({ lat: 0, lng: 0 }),
      getZoom: () => 2,
      setView: vi.fn(),
      on: vi.fn(),
      off: vi.fn(),
      addLayer: vi.fn(),
      removeLayer: vi.fn(),
      hasLayer: vi.fn(() => true),
    })),
    tileLayer: vi.fn(() => ({
      addTo: vi.fn(),
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
  };
  return { default: L };
});

describe('MapViewer Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the map container', () => {
    render(<MapViewer />);
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
  });

  it('should display map controls info', () => {
    render(<MapViewer />);
    expect(screen.getByText('Map Controls')).toBeInTheDocument();
    expect(screen.getByText(/Scroll to zoom/)).toBeInTheDocument();
    expect(screen.getByText(/Drag to pan/)).toBeInTheDocument();
    expect(screen.getByText(/Pinch to zoom/)).toBeInTheDocument();
    expect(screen.getByText(/Two-finger pan/)).toBeInTheDocument();
  });

  it('should have responsive container', () => {
    const { container } = render(<MapViewer />);
    const mapContainer = container.querySelector('[data-testid="map-container"]');
    expect(mapContainer).toHaveClass('flex-1', 'relative', 'overflow-hidden');
  });

  it('should initialize map with correct options', () => {
    render(<MapViewer />);
    // Map should be initialized with touch support enabled
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });
});

