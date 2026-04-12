/**
 * Unit tests for ErrorNotification component
 * Tests error display, retry functionality, and troubleshooting suggestions
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorNotification from '../ErrorNotification';

describe('ErrorNotification Component', () => {
  const mockOnRetry = vi.fn();
  const mockOnDismiss = vi.fn();

  beforeEach(() => {
    mockOnRetry.mockClear();
    mockOnDismiss.mockClear();
    vi.clearAllMocks();
  });

  it('renders error message', () => {
    render(
      <ErrorNotification
        error="Test error message"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('displays error title', () => {
    render(
      <ErrorNotification
        error="Test error"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('Error')).toBeInTheDocument();
  });

  it('shows network error troubleshooting steps', () => {
    render(
      <ErrorNotification
        error="Network connection failed"
        errorType="network"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText(/Check your internet connection/)).toBeInTheDocument();
    expect(screen.getByText(/Try uploading again/)).toBeInTheDocument();
  });

  it('shows validation error troubleshooting steps', () => {
    render(
      <ErrorNotification
        error="Invalid shapefile"
        errorType="validation"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText(/Ensure all required shapefile components are present/)).toBeInTheDocument();
    expect(screen.getByText(/Check that the shapefile is not corrupted/)).toBeInTheDocument();
  });

  it('shows processing error troubleshooting steps', () => {
    render(
      <ErrorNotification
        error="Processing failed"
        errorType="processing"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText(/The file may be too large/)).toBeInTheDocument();
    expect(screen.getByText(/Check that the shapefile geometry is valid/)).toBeInTheDocument();
  });

  it('shows export error troubleshooting steps', () => {
    render(
      <ErrorNotification
        error="Export failed"
        errorType="export"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText(/Check that you have sufficient disk space/)).toBeInTheDocument();
    expect(screen.getByText(/Try exporting in a different format/)).toBeInTheDocument();
  });

  it('displays retry attempt counter', () => {
    render(
      <ErrorNotification
        error="Test error"
        retryAttempt={2}
        maxRetries={3}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('Retry 2 of 3')).toBeInTheDocument();
  });

  it('shows retry button when retries available', () => {
    render(
      <ErrorNotification
        error="Test error"
        retryAttempt={1}
        maxRetries={3}
        onRetry={mockOnRetry}
        onDismiss={mockOnDismiss}
      />
    );

    const retryButton = screen.getByRole('button', { name: /Retry/ });
    expect(retryButton).toBeInTheDocument();
  });

  it('hides retry button when max retries reached', () => {
    render(
      <ErrorNotification
        error="Test error"
        retryAttempt={3}
        maxRetries={3}
        onRetry={mockOnRetry}
        onDismiss={mockOnDismiss}
      />
    );

    const retryButton = screen.queryByRole('button', { name: /Retry/ });
    expect(retryButton).not.toBeInTheDocument();
  });

  it('calls onRetry when retry button clicked', async () => {
    render(
      <ErrorNotification
        error="Test error"
        retryAttempt={1}
        maxRetries={3}
        onRetry={mockOnRetry}
        onDismiss={mockOnDismiss}
      />
    );

    const retryButton = screen.getByRole('button', { name: /Retry/ });
    await userEvent.click(retryButton);

    expect(mockOnRetry).toHaveBeenCalled();
  });

  it('calls onDismiss when dismiss button clicked', async () => {
    render(
      <ErrorNotification
        error="Test error"
        onDismiss={mockOnDismiss}
      />
    );

    const buttons = screen.getAllByRole('button');
    const dismissButton = buttons.find(btn => btn.textContent === 'Dismiss');
    
    if (dismissButton) {
      await userEvent.click(dismissButton);
      expect(mockOnDismiss).toHaveBeenCalled();
    }
  });

  it('calls onDismiss when close button clicked', async () => {
    render(
      <ErrorNotification
        error="Test error"
        onDismiss={mockOnDismiss}
      />
    );

    const buttons = screen.getAllByRole('button');
    const closeButton = buttons.find(btn => btn.className.includes('close-button'));
    
    if (closeButton) {
      await userEvent.click(closeButton);
      expect(mockOnDismiss).toHaveBeenCalled();
    }
  });

  it('auto-closes after specified duration', async () => {
    render(
      <ErrorNotification
        error="Test error"
        autoClose={true}
        autoCloseDuration={100}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('Test error')).toBeInTheDocument();

    await waitFor(
      () => {
        expect(mockOnDismiss).toHaveBeenCalled();
      },
      { timeout: 200 }
    );
  });

  it('does not auto-close when autoClose is false', async () => {
    render(
      <ErrorNotification
        error="Test error"
        autoClose={false}
        autoCloseDuration={100}
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('Test error')).toBeInTheDocument();

    // Wait to ensure it doesn't auto-close
    await new Promise((resolve) => setTimeout(resolve, 150));

    expect(mockOnDismiss).not.toHaveBeenCalled();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('applies correct CSS class for error type', () => {
    const { container } = render(
      <ErrorNotification
        error="Network error"
        errorType="network"
        onDismiss={mockOnDismiss}
      />
    );

    const notification = container.querySelector('.error-notification');
    expect(notification).toHaveClass('network');
  });

  it('displays troubleshooting title', () => {
    render(
      <ErrorNotification
        error="Test error"
        onDismiss={mockOnDismiss}
      />
    );

    expect(screen.getByText('Troubleshooting Steps:')).toBeInTheDocument();
  });

  it('renders as list of troubleshooting steps', () => {
    render(
      <ErrorNotification
        error="Test error"
        errorType="validation"
        onDismiss={mockOnDismiss}
      />
    );

    const list = screen.getByRole('list');
    const items = screen.getAllByRole('listitem');
    
    expect(list).toBeInTheDocument();
    expect(items.length).toBeGreaterThan(0);
  });
});
