import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GenerateCompartmentsStep } from '../GenerateCompartmentsStep';

describe('GenerateCompartmentsStep', () => {
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

  it('renders the component with title and description', () => {
    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const titles = screen.getAllByText('Generate Compartments');
    expect(titles.length).toBeGreaterThan(0);
    expect(
      screen.getByText(/Divide the forest boundary into equal-area compartments/)
    ).toBeInTheDocument();
  });

  it('displays compartment count input with default value of 4', () => {
    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const input = screen.getByDisplayValue('4') as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(input.type).toBe('number');
  });

  it('allows changing compartment count', () => {
    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const input = screen.getByDisplayValue('4') as HTMLInputElement;
    fireEvent.change(input, { target: { value: '8' } });
    expect(input.value).toBe('8');
  });

  it('prevents invalid compartment count values', () => {
    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const input = screen.getByDisplayValue('4') as HTMLInputElement;
    fireEvent.change(input, { target: { value: '0' } });
    expect(input.value).toBe('4'); // Should remain unchanged
    fireEvent.change(input, { target: { value: '101' } });
    expect(input.value).toBe('4'); // Should remain unchanged
  });

  it('displays Generate Compartments button when not generating', () => {
    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const buttons = screen.getAllByText('Generate Compartments');
    const button = buttons.find(b => b.tagName === 'BUTTON');
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();
  });

  it('shows error when shapefileId is missing', async () => {
    render(<GenerateCompartmentsStep shapefileId="" />);
    const buttons = screen.getAllByText('Generate Compartments');
    const button = buttons.find(b => b.tagName === 'BUTTON');
    fireEvent.click(button!);
    await waitFor(() => {
      expect(screen.getByText('Shapefile ID is required')).toBeInTheDocument();
    });
  });

  it('calls onError callback when generation fails', async () => {
    const onError = vi.fn();
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

    render(<GenerateCompartmentsStep shapefileId="test-id" onError={onError} />);
    const buttons = screen.getAllByText('Generate Compartments');
    const button = buttons.find(b => b.tagName === 'BUTTON');
    fireEvent.click(button!);

    await waitFor(() => {
      expect(onError).toHaveBeenCalled();
    });
  });

  it('handles API error response', async () => {
    const onError = vi.fn();
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: 'API error' }),
    });

    render(<GenerateCompartmentsStep shapefileId="test-id" onError={onError} />);
    const buttons = screen.getAllByText('Generate Compartments');
    const button = buttons.find(b => b.tagName === 'BUTTON');
    fireEvent.click(button!);

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith('API error');
    });
  });

  it('displays error notification on failure', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: 'Generation failed' }),
    });

    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const buttons = screen.getAllByText('Generate Compartments');
    const button = buttons.find(b => b.tagName === 'BUTTON');
    fireEvent.click(button!);

    await waitFor(() => {
      expect(screen.getByText('Generation failed')).toBeInTheDocument();
    });
  });

  it('makes API call with correct parameters', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'processing' }),
    });

    render(<GenerateCompartmentsStep shapefileId="test-id" />);
    const buttons = screen.getAllByText('Generate Compartments');
    const button = buttons.find(b => b.tagName === 'BUTTON');
    fireEvent.click(button!);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/compartments/generate',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
  });
});
