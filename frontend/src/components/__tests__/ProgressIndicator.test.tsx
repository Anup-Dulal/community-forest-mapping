/**
 * Unit tests for ProgressIndicator component
 * Tests progress bar updates, time remaining, and cancel functionality
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import ProgressIndicator from '../ProgressIndicator';

describe('ProgressIndicator', () => {
  const mockOnComplete = vi.fn();
  const mockOnError = vi.fn();
  const mockOnCancel = vi.fn();
  const operationId = '550e8400-e29b-41d4-a716-446655440000';
  const operation = 'compartment_generation';

  beforeEach(() => {
    // Mock WebSocket
    global.WebSocket = vi.fn(() => ({
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    })) as any;

    // Mock fetch
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should render initial state', () => {
    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText(operation)).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('Initializing...')).toBeInTheDocument();
  });

  it('should connect to WebSocket', async () => {
    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
      />
    );

    await waitFor(() => {
      expect(global.WebSocket).toHaveBeenCalled();
    });
  });

  it('should display progress updates', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
      />
    );

    // Simulate WebSocket connection
    await waitFor(() => {
      expect(mockWebSocket.onopen).toBeDefined();
    });

    // Simulate progress update
    const progressUpdate = {
      operationId,
      operation,
      percentage: 50,
      estimatedTimeRemaining: 30,
      statusMessage: 'Processing...',
      currentStep: 'Step 1',
      timestamp: new Date().toISOString(),
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(progressUpdate),
    } as any);

    await waitFor(() => {
      expect(screen.getByText('50%')).toBeInTheDocument();
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });
  });

  it('should format time remaining correctly', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
      />
    );

    // Simulate progress update with time remaining
    const progressUpdate = {
      operationId,
      operation,
      percentage: 50,
      estimatedTimeRemaining: 125, // 2 minutes 5 seconds
      statusMessage: 'Processing...',
      currentStep: 'Step 1',
      timestamp: new Date().toISOString(),
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(progressUpdate),
    } as any);

    await waitFor(() => {
      expect(screen.getByText(/2m/)).toBeInTheDocument();
    });
  });

  it('should call onComplete when progress reaches 100%', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
      />
    );

    // Simulate completion
    const completionUpdate = {
      operationId,
      operation,
      percentage: 100,
      estimatedTimeRemaining: 0,
      statusMessage: 'Completed',
      currentStep: 'Done',
      timestamp: new Date().toISOString(),
      summary: { compartmentCount: 10 },
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(completionUpdate),
    } as any);

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledWith({ compartmentCount: 10 });
    });
  });

  it('should call onError on error status', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onError={mockOnError}
      />
    );

    // Simulate error
    const errorUpdate = {
      operationId,
      operation,
      status: 'error',
      errorMessage: 'Operation failed',
      timestamp: new Date().toISOString(),
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(errorUpdate),
    } as any);

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith('Operation failed');
    });
  });

  it('should handle cancel button click', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'cancelled' }),
    });

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onCancel={mockOnCancel}
        showCancelButton={true}
      />
    );

    // Simulate progress update
    const progressUpdate = {
      operationId,
      operation,
      percentage: 50,
      estimatedTimeRemaining: 30,
      statusMessage: 'Processing...',
      currentStep: 'Step 1',
      timestamp: new Date().toISOString(),
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(progressUpdate),
    } as any);

    await waitFor(() => {
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `/api/operations/${operationId}/cancel`,
        { method: 'POST' }
      );
      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  it('should hide cancel button when complete', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
        showCancelButton={true}
      />
    );

    // Simulate completion
    const completionUpdate = {
      operationId,
      operation,
      percentage: 100,
      estimatedTimeRemaining: 0,
      statusMessage: 'Completed',
      currentStep: 'Done',
      timestamp: new Date().toISOString(),
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(completionUpdate),
    } as any);

    await waitFor(() => {
      expect(screen.queryByText('Cancel')).not.toBeInTheDocument();
      expect(screen.getByText('Operation completed successfully')).toBeInTheDocument();
    });
  });

  it('should display current step', async () => {
    const mockWebSocket = {
      send: vi.fn(),
      close: vi.fn(),
      onopen: null,
      onmessage: null,
      onerror: null,
      onclose: null,
    };

    (global.WebSocket as any).mockReturnValue(mockWebSocket);

    render(
      <ProgressIndicator
        operationId={operationId}
        operation={operation}
        onComplete={mockOnComplete}
      />
    );

    // Simulate progress update with current step
    const progressUpdate = {
      operationId,
      operation,
      percentage: 50,
      estimatedTimeRemaining: 30,
      statusMessage: 'Processing...',
      currentStep: 'Generating compartments',
      timestamp: new Date().toISOString(),
    };

    mockWebSocket.onmessage?.({
      data: JSON.stringify(progressUpdate),
    } as any);

    await waitFor(() => {
      expect(screen.getByText(/Generating compartments/)).toBeInTheDocument();
    });
  });
});
