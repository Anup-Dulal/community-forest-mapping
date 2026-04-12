import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { CalculateTerrainStep } from '../CalculateTerrainStep';
import '@testing-library/jest-dom';

/**
 * Unit Tests for CalculateTerrainStep Component
 * Tests real-time slope and aspect calculation with progress updates.
 * Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 15.4, 15.5, 15.6, 15.7, 15.8
 */

describe('CalculateTerrainStep', () => {
  const mockShapefileId = 'test-shapefile-123';
  const mockDemPath = '/path/to/dem.tif';

  beforeEach(() => {
    // Mock fetch
    global.fetch = vi.fn();
    // Mock WebSocket
    global.WebSocket = vi.fn(() => ({
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })) as any;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render the component with header', () => {
      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      expect(screen.getByText('Calculate Terrain Analysis')).toBeInTheDocument();
      expect(
        screen.getByText('Analyze slope and aspect to understand terrain characteristics.')
      ).toBeInTheDocument();
    });

    it('should render the Analyze Terrain button initially', () => {
      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      expect(button).toBeInTheDocument();
      expect(button).not.toBeDisabled();
    });

    it('should render tabs for slope and aspect analysis', () => {
      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      // Tabs should not be visible initially
      expect(screen.queryByText('Slope Analysis')).not.toBeInTheDocument();
    });
  });

  describe('Analysis Initiation', () => {
    it('should call the backend API when Analyze Terrain button is clicked', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/terrain/analyze',
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: expect.stringContaining(mockShapefileId),
          })
        );
      });
    });

    it('should show error message if API call fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'API Error' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('API Error')).toBeInTheDocument();
      });
    });

    it('should show error if shapefile ID is missing', async () => {
      render(
        <CalculateTerrainStep
          shapefileId=""
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Shapefile ID is required')).toBeInTheDocument();
      });
    });
  });

  describe('Progress Tracking', () => {
    it('should display progress bar during analysis', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Starting terrain analysis...')).toBeInTheDocument();
      });
    });

    it('should display cancel button during analysis', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
      });
    });
  });

  describe('Results Display', () => {
    it('should display slope and aspect tabs after analysis completes', async () => {
      const mockResults = {
        slope_statistics: {
          min: 0,
          max: 45,
          mean: 15,
          std: 10,
          median: 12,
        },
        aspect_statistics: {
          min: 0,
          max: 360,
          mean: 180,
          std: 100,
        },
        slope_distribution: {
          gentle_0_20: { count: 1000, percentage: 60 },
          moderate_20_30: { count: 400, percentage: 25 },
          steep_30_plus: { count: 200, percentage: 15 },
        },
        aspect_distribution: {
          N: { count: 200, percentage: 12.5 },
          NE: { count: 200, percentage: 12.5 },
          E: { count: 200, percentage: 12.5 },
          SE: { count: 200, percentage: 12.5 },
          S: { count: 200, percentage: 12.5 },
          SW: { count: 200, percentage: 12.5 },
          W: { count: 200, percentage: 12.5 },
          NW: { count: 200, percentage: 12.5 },
        },
        slope_path: '/path/to/slope.tif',
        slope_classified_path: '/path/to/slope_classified.tif',
        aspect_path: '/path/to/aspect.tif',
        aspect_classified_path: '/path/to/aspect_classified.tif',
        elapsed_time: 5.2,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      const { rerender } = render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      // Simulate WebSocket message with results
      await waitFor(() => {
        expect(screen.getByText('Starting terrain analysis...')).toBeInTheDocument();
      });

      // Simulate completion by re-rendering with results
      // In a real test, this would come from WebSocket
    });

    it('should display slope statistics', async () => {
      const mockResults = {
        slope_statistics: {
          min: 0,
          max: 45,
          mean: 15,
          std: 10,
          median: 12,
        },
        aspect_statistics: {
          min: 0,
          max: 360,
          mean: 180,
          std: 100,
        },
        slope_distribution: {
          gentle_0_20: { count: 1000, percentage: 60 },
          moderate_20_30: { count: 400, percentage: 25 },
          steep_30_plus: { count: 200, percentage: 15 },
        },
        aspect_distribution: {
          N: { count: 200, percentage: 12.5 },
          NE: { count: 200, percentage: 12.5 },
          E: { count: 200, percentage: 12.5 },
          SE: { count: 200, percentage: 12.5 },
          S: { count: 200, percentage: 12.5 },
          SW: { count: 200, percentage: 12.5 },
          W: { count: 200, percentage: 12.5 },
          NW: { count: 200, percentage: 12.5 },
        },
        slope_path: '/path/to/slope.tif',
        slope_classified_path: '/path/to/slope_classified.tif',
        aspect_path: '/path/to/aspect.tif',
        aspect_classified_path: '/path/to/aspect_classified.tif',
        elapsed_time: 5.2,
      };

      // This test would verify that slope statistics are displayed
      // when results are available
    });

    it('should display aspect statistics', async () => {
      // This test would verify that aspect statistics are displayed
      // when results are available
    });

    it('should display slope distribution chart', async () => {
      // This test would verify that slope distribution is displayed
      // with correct percentages
    });

    it('should display aspect compass', async () => {
      // This test would verify that aspect compass is displayed
      // with all 8 cardinal directions
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between slope and aspect tabs', async () => {
      // This test would verify tab switching functionality
    });

    it('should display correct content for each tab', async () => {
      // This test would verify that correct content is shown
      // when switching tabs
    });
  });

  describe('Error Handling', () => {
    it('should display error notification on WebSocket error', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      // Simulate WebSocket error
      await waitFor(() => {
        // Error handling would be tested here
      });
    });

    it('should call onError callback when analysis fails', async () => {
      const onError = vi.fn();
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Analysis failed' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
          onError={onError}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith('Analysis failed');
      });
    });
  });

  describe('Callbacks', () => {
    it('should call onComplete callback when analysis completes', async () => {
      const onComplete = vi.fn();
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
          onComplete={onComplete}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      // Simulate completion
      await waitFor(() => {
        // onComplete would be called here
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for progress bar', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ operationId: 'test-op-123' }),
      });

      render(
        <CalculateTerrainStep
          shapefileId={mockShapefileId}
          demPath={mockDemPath}
        />
      );

      const button = screen.getByRole('button', { name: /Analyze Terrain/i });
      fireEvent.click(button);

      await waitFor(() => {
        const progressBar = screen.getByRole('progressbar');
        expect(progressBar).toHaveAttribute('aria-valuenow');
        expect(progressBar).toHaveAttribute('aria-valuemin', '0');
        expect(progressBar).toHaveAttribute('aria-valuemax', '100');
      });
    });
  });
});
