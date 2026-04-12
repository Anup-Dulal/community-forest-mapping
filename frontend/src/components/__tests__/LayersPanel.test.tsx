import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import LayersPanel from '../LayersPanel';
import { useAppStore } from '../../store/appStore';

// Mock the store
vi.mock('../../store/appStore', () => ({
  useAppStore: vi.fn(),
}));

describe('LayersPanel Component', () => {
  const mockSetLayerVisibility = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useAppStore as any).mockImplementation((selector: any) => {
      const state = {
        mapState: {
          layers: {
            boundary: true,
            dem: false,
            slope: false,
            aspect: false,
            compartments: false,
            samplePlots: false,
          },
        },
        setLayerVisibility: mockSetLayerVisibility,
      };
      return selector(state);
    });
  });

  it('should render all layer checkboxes', () => {
    render(<LayersPanel />);
    expect(screen.getByLabelText(/Toggle Boundary layer/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Toggle DEM layer/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Toggle Slope layer/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Toggle Aspect layer/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Toggle Compartments layer/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Toggle Sample Plots layer/)).toBeInTheDocument();
  });

  it('should display layer descriptions', () => {
    render(<LayersPanel />);
    expect(screen.getByText('Community forest boundary')).toBeInTheDocument();
    expect(screen.getByText('Digital Elevation Model')).toBeInTheDocument();
    expect(screen.getByText(/Slope classification/)).toBeInTheDocument();
  });

  it('should toggle layer visibility when checkbox is clicked', () => {
    render(<LayersPanel />);
    const boundaryCheckbox = screen.getByLabelText(/Toggle Boundary layer/);
    fireEvent.click(boundaryCheckbox);
    expect(mockSetLayerVisibility).toHaveBeenCalledWith('boundary', false);
  });

  it('should show transparency slider only for visible layers', () => {
    render(<LayersPanel />);
    // Boundary is visible, should have transparency slider
    expect(screen.getByLabelText(/Adjust Boundary transparency/)).toBeInTheDocument();
    // DEM is not visible, should not have transparency slider
    expect(screen.queryByLabelText(/Adjust DEM transparency/)).not.toBeInTheDocument();
  });

  it('should display active layers legend', () => {
    render(<LayersPanel />);
    expect(screen.getByText('Active Layers Legend')).toBeInTheDocument();
    expect(screen.getAllByText('Boundary')).toHaveLength(2); // Once in layer list, once in legend
  });

  it('should display slope legend when slope layer is visible', () => {
    (useAppStore as any).mockImplementation((selector: any) => {
      const state = {
        mapState: {
          layers: {
            boundary: true,
            dem: false,
            slope: true,
            aspect: false,
            compartments: false,
            samplePlots: false,
          },
        },
        setLayerVisibility: mockSetLayerVisibility,
      };
      return selector(state);
    });

    render(<LayersPanel />);
    expect(screen.getByText('Slope Classification')).toBeInTheDocument();
    expect(screen.getByText('0-20° (Gentle)')).toBeInTheDocument();
    expect(screen.getByText('20-30° (Moderate)')).toBeInTheDocument();
    expect(screen.getByText('>30° (Steep)')).toBeInTheDocument();
  });

  it('should display aspect legend when aspect layer is visible', () => {
    (useAppStore as any).mockImplementation((selector: any) => {
      const state = {
        mapState: {
          layers: {
            boundary: true,
            dem: false,
            slope: false,
            aspect: true,
            compartments: false,
            samplePlots: false,
          },
        },
        setLayerVisibility: mockSetLayerVisibility,
      };
      return selector(state);
    });

    render(<LayersPanel />);
    expect(screen.getByText('Aspect Directions')).toBeInTheDocument();
    expect(screen.getByText('N')).toBeInTheDocument();
    expect(screen.getByText('NE')).toBeInTheDocument();
    expect(screen.getByText('E')).toBeInTheDocument();
  });

  it('should have responsive design with collapse button on mobile', () => {
    const { container } = render(<LayersPanel />);
    const collapseButton = screen.getByRole('button', { name: /Layers/ });
    expect(collapseButton).toHaveClass('md:hidden');
  });

  it('should update transparency slider value', () => {
    render(<LayersPanel />);
    const transparencySlider = screen.getByLabelText(/Adjust Boundary transparency/);
    fireEvent.change(transparencySlider, { target: { value: '0.5' } });
    expect(transparencySlider).toHaveValue('0.5');
  });
});
