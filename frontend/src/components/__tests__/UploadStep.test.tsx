/**
 * Unit tests for UploadStep component
 * Tests file selection, validation, and upload functionality
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadStep from '../UploadStep';

// Mock the app store
vi.mock('../store/appStore', () => ({
  useAppStore: vi.fn((selector) => {
    const mockStore = {
      setUploadStatus: vi.fn(),
      setCurrentAnalysisId: vi.fn(),
    };
    return selector(mockStore);
  }),
}));

describe('UploadStep Component', () => {
  const mockOnComplete = vi.fn();

  beforeEach(() => {
    mockOnComplete.mockClear();
    vi.clearAllMocks();
  });

  it('renders upload interface with drag-drop area', () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    expect(screen.getByText('Step 1: Upload Boundary Shapefile')).toBeInTheDocument();
    expect(screen.getByText(/Drag and drop shapefile or archive here/)).toBeInTheDocument();
  });

  it('displays required files information', () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    expect(screen.getByText('Upload options:')).toBeInTheDocument();
    expect(screen.getByText(/ZIP or RAR archive containing all components/)).toBeInTheDocument();
    expect(screen.getByText(/.shp, .shx, .dbf, .prj files individually/)).toBeInTheDocument();
  });

  it('validates individual shapefile components', async () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    // Create mock files
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
      new File([''], 'test.prj', { type: 'application/octet-stream' }),
    ];

    // Simulate file selection
    await userEvent.upload(fileInput, files);

    // Check that all files are displayed
    await waitFor(() => {
      expect(screen.getByText('test.shp')).toBeInTheDocument();
      expect(screen.getByText('test.shx')).toBeInTheDocument();
      expect(screen.getByText('test.dbf')).toBeInTheDocument();
      expect(screen.getByText('test.prj')).toBeInTheDocument();
    });
  });

  it('shows error when required files are missing', async () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    // Create incomplete file set (missing .prj)
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
    ];

    await userEvent.upload(fileInput, files);

    await waitFor(() => {
      expect(screen.getByText(/Missing required files: .prj/)).toBeInTheDocument();
    });
  });

  it('disables upload button when no files selected', () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const uploadButton = screen.getByRole('button', { name: /Upload Shapefile/ });
    expect(uploadButton).toBeDisabled();
  });

  it('enables upload button when all required files selected', async () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
      new File([''], 'test.prj', { type: 'application/octet-stream' }),
    ];

    await userEvent.upload(fileInput, files);

    await waitFor(() => {
      const uploadButton = screen.getByRole('button', { name: /Upload Shapefile/ });
      expect(uploadButton).not.toBeDisabled();
    });
  });

  it('handles drag and drop file selection', async () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const dragDropArea = screen.getByText(/Drag and drop shapefile or archive here/).closest('.drag-drop-area');
    
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
      new File([''], 'test.prj', { type: 'application/octet-stream' }),
    ];

    // Simulate drag over
    fireEvent.dragOver(dragDropArea!);
    expect(dragDropArea).toHaveClass('drag-over');

    // Simulate drag leave
    fireEvent.dragLeave(dragDropArea!);
    expect(dragDropArea).not.toHaveClass('drag-over');

    // Simulate drop
    fireEvent.drop(dragDropArea!, {
      dataTransfer: {
        files: files,
      },
    });

    await waitFor(() => {
      expect(screen.getByText('test.shp')).toBeInTheDocument();
    });
  });

  it('shows upload progress during upload', async () => {
    // Mock fetch to simulate upload
    global.fetch = vi.fn(() =>
      new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: async () => ({ shapefileId: 'test-id-123' }),
          } as Response);
        }, 100);
      })
    );

    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
      new File([''], 'test.prj', { type: 'application/octet-stream' }),
    ];

    await userEvent.upload(fileInput, files);

    const uploadButton = screen.getByRole('button', { name: /Upload Shapefile/ });
    await userEvent.click(uploadButton);

    // Check that upload button shows uploading state
    await waitFor(() => {
      expect(uploadButton).toHaveTextContent(/Uploading/);
    });
  });

  it('calls onComplete callback after successful upload', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: async () => ({ shapefileId: 'test-id-123' }),
      } as Response)
    );

    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
      new File([''], 'test.prj', { type: 'application/octet-stream' }),
    ];

    await userEvent.upload(fileInput, files);

    const uploadButton = screen.getByRole('button', { name: /Upload Shapefile/ });
    await userEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
      expect(mockOnComplete.mock.calls[0][0]).toBeDefined();
    });
  });

  it('displays error message on upload failure', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid shapefile format' }),
      } as Response)
    );

    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    const files = [
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
      new File([''], 'test.shx', { type: 'application/octet-stream' }),
      new File([''], 'test.dbf', { type: 'application/octet-stream' }),
      new File([''], 'test.prj', { type: 'application/octet-stream' }),
    ];

    await userEvent.upload(fileInput, files);

    const uploadButton = screen.getByRole('button', { name: /Upload Shapefile/ });
    await userEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid shapefile format/)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('prevents upload of mixed archive and individual files', async () => {
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const fileInput = screen.getByLabelText('Select shapefile components or archive');
    
    const files = [
      new File([''], 'test.zip', { type: 'application/zip' }),
      new File([''], 'test.shp', { type: 'application/octet-stream' }),
    ];

    await userEvent.upload(fileInput, files);

    await waitFor(() => {
      expect(screen.getByText(/Upload either an archive file OR individual shapefile components, not both/)).toBeInTheDocument();
    });
  });
});
