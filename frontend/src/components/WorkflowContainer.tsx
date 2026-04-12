import React, { useState, useCallback } from 'react';
import UploadStep from './UploadStep';
import VerifyBoundaryStep from './VerifyBoundaryStep';
import GenerateHierarchicalCompartmentsStep from './GenerateHierarchicalCompartmentsStep';
import CalculateTerrainStep from './CalculateTerrainStep';
import { WelcomeScreen } from './WelcomeScreen';
import '../styles/WorkflowContainer.css';

/**
 * WorkflowContainer Component
 * Manages step-by-step workflow state and coordinates between step components.
 * Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8
 */

export type WorkflowStep = 'welcome' | 'upload' | 'verify' | 'generate' | 'calculate' | 'export';

interface WorkflowState {
  currentStep: WorkflowStep;
  shapefileId: string | null;
  demPath: string | null;
  compartmentAnalysisId: string | null;
  terrainAnalysisId: string | null;
  exportId: string | null;
  isComplete: boolean;
}

interface WorkflowContainerProps {
  onWorkflowComplete?: (state: WorkflowState) => void;
}

export const WorkflowContainer: React.FC<WorkflowContainerProps> = ({ onWorkflowComplete }) => {
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    currentStep: 'welcome',
    shapefileId: null,
    demPath: null,
    compartmentAnalysisId: null,
    terrainAnalysisId: null,
    exportId: null,
    isComplete: false,
  });

  const stepOrder: WorkflowStep[] = ['upload', 'verify', 'generate', 'calculate', 'export'];

  const getCurrentStepIndex = useCallback(() => {
    return stepOrder.indexOf(workflowState.currentStep as any);
  }, [workflowState.currentStep]);

  const canAdvanceToStep = useCallback((step: WorkflowStep): boolean => {
    const stepIndex = stepOrder.indexOf(step as any);
    const currentIndex = getCurrentStepIndex();

    // Can only advance to next step or go back
    if (stepIndex > currentIndex + 1) {
      return false;
    }

    // Check if current step is complete
    switch (workflowState.currentStep) {
      case 'upload':
        return workflowState.shapefileId !== null;
      case 'verify':
        return workflowState.shapefileId !== null;
      case 'generate':
        return workflowState.compartmentAnalysisId !== null;
      case 'calculate':
        return workflowState.terrainAnalysisId !== null;
      case 'export':
        return true;
      default:
        return true;
    }
  }, [workflowState, getCurrentStepIndex]);

  const advanceToStep = useCallback((step: WorkflowStep) => {
    if (canAdvanceToStep(step)) {
      setWorkflowState((prev) => ({
        ...prev,
        currentStep: step,
      }));
    }
  }, [canAdvanceToStep]);

  const goToNextStep = useCallback(() => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < stepOrder.length - 1) {
      advanceToStep(stepOrder[currentIndex + 1]);
    }
  }, [getCurrentStepIndex, advanceToStep, stepOrder]);

  const goToPreviousStep = useCallback(() => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      advanceToStep(stepOrder[currentIndex - 1]);
    }
  }, [getCurrentStepIndex, advanceToStep, stepOrder]);

  const handleUploadComplete = useCallback((shapefileId: string, demPath: string) => {
    setWorkflowState((prev) => ({
      ...prev,
      shapefileId,
      demPath,
    }));
    // Auto-advance to verify step
    setTimeout(() => {
      advanceToStep('verify');
    }, 500);
  }, [advanceToStep]);

  const handleVerifyComplete = useCallback(() => {
    // Auto-advance to generate step
    setTimeout(() => {
      advanceToStep('generate');
    }, 500);
  }, [advanceToStep]);

  const handleGenerateComplete = useCallback((analysisId: string) => {
    setWorkflowState((prev) => ({
      ...prev,
      compartmentAnalysisId: analysisId,
    }));
    // Auto-advance to calculate step
    setTimeout(() => {
      advanceToStep('calculate');
    }, 500);
  }, [advanceToStep]);

  const handleCalculateComplete = useCallback((analysisId: string) => {
    setWorkflowState((prev) => ({
      ...prev,
      terrainAnalysisId: analysisId,
    }));
    // Auto-advance to export step
    setTimeout(() => {
      advanceToStep('export');
    }, 500);
  }, [advanceToStep]);

  const handleExportComplete = useCallback((exportId: string) => {
    setWorkflowState((prev) => ({
      ...prev,
      exportId,
      isComplete: true,
    }));
    if (onWorkflowComplete) {
      onWorkflowComplete({
        ...workflowState,
        exportId,
        isComplete: true,
      });
    }
  }, [workflowState, onWorkflowComplete]);

  const handleReset = useCallback(() => {
    setWorkflowState({
      currentStep: 'welcome',
      shapefileId: null,
      demPath: null,
      compartmentAnalysisId: null,
      terrainAnalysisId: null,
      exportId: null,
      isComplete: false,
    });
  }, []);

  const getStepProgress = useCallback(() => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex === -1) return 0;
    return ((currentIndex + 1) / stepOrder.length) * 100;
  }, [getCurrentStepIndex, stepOrder.length]);

  return (
    <div className="workflow-container">
      {workflowState.currentStep === 'welcome' && (
        <WelcomeScreen onStart={() => advanceToStep('upload')} />
      )}

      {workflowState.currentStep !== 'welcome' && (
        <>
          <div className="workflow-header">
            <h1>Community Forest Mapping Workflow</h1>
            <div className="progress-bar-container">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${getStepProgress()}%` }}
                />
              </div>
              <span className="progress-text">
                Step {getCurrentStepIndex() + 1} of {stepOrder.length}
              </span>
            </div>
          </div>

          <div className="workflow-steps">
            <div className="steps-indicator">
              {stepOrder.map((step, index) => (
                <div
                  key={step}
                  className={`step-indicator ${
                    workflowState.currentStep === step ? 'active' : ''
                  } ${index < getCurrentStepIndex() ? 'completed' : ''}`}
                  onClick={() => advanceToStep(step)}
                >
                  <div className="step-number">{index + 1}</div>
                  <div className="step-label">{step.charAt(0).toUpperCase() + step.slice(1)}</div>
                </div>
              ))}
            </div>

            <div className="step-content">
              {workflowState.currentStep === 'upload' && (
                <UploadStep
                  onComplete={handleUploadComplete}
                  onError={(error) => console.error('Upload error:', error)}
                />
              )}

              {workflowState.currentStep === 'verify' && workflowState.shapefileId && (
                <VerifyBoundaryStep
                  shapefileId={workflowState.shapefileId}
                  onComplete={handleVerifyComplete}
                  onError={(error) => console.error('Verify error:', error)}
                />
              )}

              {workflowState.currentStep === 'generate' && workflowState.shapefileId && (
                <GenerateHierarchicalCompartmentsStep
                  shapefileId={workflowState.shapefileId}
                  onComplete={handleGenerateComplete}
                  onError={(error) => console.error('Generate error:', error)}
                />
              )}

              {workflowState.currentStep === 'calculate' && workflowState.shapefileId && (
                <CalculateTerrainStep
                  shapefileId={workflowState.shapefileId}
                  demPath={workflowState.demPath || undefined}
                  onComplete={handleCalculateComplete}
                  onError={(error) => console.error('Calculate error:', error)}
                />
              )}

              {workflowState.currentStep === 'export' && workflowState.shapefileId && (
                <div className="export-placeholder">
                  <h2>Export Results</h2>
                  <p>Export functionality coming soon. Your analysis is complete!</p>
                  <div className="export-summary">
                    <p>Shapefile ID: {workflowState.shapefileId}</p>
                    <p>Compartment Analysis: {workflowState.compartmentAnalysisId}</p>
                    <p>Terrain Analysis: {workflowState.terrainAnalysisId}</p>
                  </div>
                </div>
              )}
            </div>

            <div className="workflow-navigation">
              <button
                className="btn btn-secondary"
                onClick={goToPreviousStep}
                disabled={getCurrentStepIndex() === 0}
              >
                ← Back
              </button>

              {!workflowState.isComplete && (
                <button
                  className="btn btn-primary"
                  onClick={goToNextStep}
                  disabled={getCurrentStepIndex() === stepOrder.length - 1}
                >
                  Next →
                </button>
              )}

              {workflowState.isComplete && (
                <button className="btn btn-success" onClick={handleReset}>
                  Start New Analysis
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
