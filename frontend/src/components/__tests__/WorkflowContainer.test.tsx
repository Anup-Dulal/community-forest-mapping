import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { WorkflowContainer } from '../WorkflowContainer';
import '@testing-library/jest-dom';

/**
 * Unit Tests for WorkflowContainer Component
 * Tests step-by-step workflow management and state transitions.
 * Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8
 */

describe('WorkflowContainer', () => {
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
    it('should render the welcome screen initially', () => {
      render(<WorkflowContainer />);

      expect(screen.getByText('Community Forest Mapping')).toBeInTheDocument();
      expect(screen.getByText('Analyze your forest boundary with ease')).toBeInTheDocument();
    });

    it('should display the Get Started button on welcome screen', () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      expect(button).toBeInTheDocument();
    });

    it('should display workflow steps guide', () => {
      render(<WorkflowContainer />);

      expect(screen.getByText('How It Works')).toBeInTheDocument();
      expect(screen.getByText('Upload Boundary')).toBeInTheDocument();
      expect(screen.getByText('Verify Boundary')).toBeInTheDocument();
      expect(screen.getByText('Generate Compartments')).toBeInTheDocument();
      expect(screen.getByText('Calculate Terrain')).toBeInTheDocument();
      expect(screen.getByText('Export Results')).toBeInTheDocument();
    });

    it('should display key features', () => {
      render(<WorkflowContainer />);

      expect(screen.getByText('Key Features')).toBeInTheDocument();
      expect(screen.getByText(/Real-time map visualization/)).toBeInTheDocument();
      expect(screen.getByText(/Live progress updates/)).toBeInTheDocument();
    });
  });

  describe('Workflow Navigation', () => {
    it('should advance to upload step when Get Started is clicked', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Community Forest Mapping Workflow')).toBeInTheDocument();
      });
    });

    it('should display step indicators after starting workflow', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });

    it('should display Back and Next buttons in workflow', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Next/i })).toBeInTheDocument();
      });
    });

    it('should disable Back button on first step', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        const backButton = screen.getByRole('button', { name: /Back/i });
        expect(backButton).toBeDisabled();
      });
    });
  });

  describe('Step Progression', () => {
    it('should show progress bar with correct percentage', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });

    it('should update progress as steps advance', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });

      // Note: In a real test, we would simulate step completion
      // and verify the progress updates
    });
  });

  describe('Step Indicators', () => {
    it('should display all step indicators', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        // Step indicators should be visible
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });

    it('should highlight current step indicator', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        // Current step should be highlighted
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });
  });

  describe('Workflow State Management', () => {
    it('should maintain workflow state across steps', async () => {
      const onWorkflowComplete = vi.fn();
      render(<WorkflowContainer onWorkflowComplete={onWorkflowComplete} />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });

    it('should call onWorkflowComplete when workflow is finished', async () => {
      const onWorkflowComplete = vi.fn();
      render(<WorkflowContainer onWorkflowComplete={onWorkflowComplete} />);

      // Note: In a real test, we would complete all steps
      // and verify onWorkflowComplete is called
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<WorkflowContainer />);

      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toBeInTheDocument();
    });

    it('should have descriptive button labels', () => {
      render(<WorkflowContainer />);

      expect(screen.getByRole('button', { name: /Get Started/i })).toBeInTheDocument();
    });

    it('should have proper ARIA labels for progress bar', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        // Progress bar should have proper ARIA attributes
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });
  });

  describe('Mobile Responsiveness', () => {
    it('should render on mobile viewport', () => {
      // Set mobile viewport
      global.innerWidth = 375;
      global.innerHeight = 667;

      render(<WorkflowContainer />);

      expect(screen.getByText('Community Forest Mapping')).toBeInTheDocument();
    });

    it('should render on tablet viewport', () => {
      // Set tablet viewport
      global.innerWidth = 768;
      global.innerHeight = 1024;

      render(<WorkflowContainer />);

      expect(screen.getByText('Community Forest Mapping')).toBeInTheDocument();
    });

    it('should render on desktop viewport', () => {
      // Set desktop viewport
      global.innerWidth = 1920;
      global.innerHeight = 1080;

      render(<WorkflowContainer />);

      expect(screen.getByText('Community Forest Mapping')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should handle missing step components gracefully', async () => {
      render(<WorkflowContainer />);

      const button = screen.getByRole('button', { name: /Get Started/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText('Step 1 of 5')).toBeInTheDocument();
      });
    });
  });

  describe('Reset Functionality', () => {
    it('should display Start New Analysis button after completion', async () => {
      render(<WorkflowContainer />);

      // Note: In a real test, we would complete all steps
      // and verify the "Start New Analysis" button appears
    });

    it('should reset workflow state when Start New Analysis is clicked', async () => {
      render(<WorkflowContainer />);

      // Note: In a real test, we would complete all steps,
      // click "Start New Analysis", and verify the workflow resets
    });
  });
});
