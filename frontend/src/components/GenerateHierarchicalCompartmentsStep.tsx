import React, { useState } from 'react';
import SubCompartmentInput, { CompartmentSpec } from './SubCompartmentInput';
import ErrorNotification from './ErrorNotification';
import { compartmentAPI, shapefileAPI } from '../services/api';
import '../styles/GenerateCompartmentsStep.css';

/**
 * GenerateHierarchicalCompartmentsStep Component
 * Generates compartments with sub-compartments in hierarchical structure
 * Example: C1 → C1S1, C1S2, ..., C1S8
 */

interface CompartmentStatistics {
  totalCompartments: number;
  totalSubCompartments: number;
  compartmentStats: {
    mean: number;
    min: number;
    max: number;
    std: number;
  };
  subCompartmentStats: {
    mean: number;
    min: number;
    max: number;
    std: number;
  };
}

interface GenerateHierarchicalCompartmentsStepProps {
  shapefileId: string;
  onComplete?: (analysisId: string, statistics: CompartmentStatistics) => void;
  onError?: (error: string) => void;
}

export const GenerateHierarchicalCompartmentsStep: React.FC<
  GenerateHierarchicalCompartmentsStepProps
> = ({ shapefileId, onComplete, onError }) => {
  const [compartmentSpecs, setCompartmentSpecs] = useState<CompartmentSpec[]>([
    { compartmentNumber: 1, subCompartmentCount: 8 },
  ]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [statistics, setStatistics] = useState<CompartmentStatistics | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!shapefileId) {
      setError('Shapefile ID is required');
      return;
    }

    setIsGenerating(true);
    setProgress(0);
    setStatusMessage('Fetching shapefile data...');
    setError(null);
    setStatistics(null);

    try {
      // Step 1: Get shapefile data to extract boundary WKT
      setProgress(10);
      setStatusMessage('Loading shapefile...');
      
      const shapefileResponse = await shapefileAPI.getById(shapefileId);
      const boundaryWkt = shapefileResponse.data.geometry;

      if (!boundaryWkt) {
        throw new Error('Shapefile geometry not found');
      }

      // Step 2: Call hierarchical compartment generation API
      setProgress(20);
      setStatusMessage('Starting compartment generation...');

      const response = await compartmentAPI.generateHierarchical({
        boundaryWkt,
        analysisId: shapefileId,
        compartments: compartmentSpecs,
      });

      const responseAnalysisId = response.data.analysisId;
      setAnalysisId(responseAnalysisId);

      // Step 3: Poll for completion
      setProgress(30);
      setStatusMessage('Generating compartments...');

      await pollForCompletion(responseAnalysisId);

      setProgress(100);
      setStatusMessage('Compartments generated successfully!');
      setIsGenerating(false);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      console.error('Error generating hierarchical compartments:', err);
      setError(errorMessage);
      setIsGenerating(false);
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const pollForCompletion = async (analysisId: string): Promise<void> => {
    const maxAttempts = 60; // 60 attempts * 2 seconds = 2 minutes max
    let attempts = 0;

    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        attempts++;

        try {
          // Get analysis details to check status
          const detailsResponse = await compartmentAPI.getAnalysisDetails(analysisId);
          const status = detailsResponse.data.status;

          setProgress(30 + (attempts / maxAttempts) * 60);
          setStatusMessage(`Processing... (${attempts}/${maxAttempts})`);

          if (status === 'complete') {
            clearInterval(interval);

            // Get compartments to extract statistics
            const compartmentsResponse = await compartmentAPI.getByAnalysisId(analysisId);
            const compartments = compartmentsResponse.data;

            // Calculate statistics
            const stats = calculateStatistics(compartments);
            setStatistics(stats);

            if (onComplete) {
              onComplete(analysisId, stats);
            }

            resolve();
          } else if (status === 'error') {
            clearInterval(interval);
            reject(new Error('Compartment generation failed'));
          } else if (attempts >= maxAttempts) {
            clearInterval(interval);
            reject(new Error('Timeout waiting for compartment generation'));
          }
        } catch (err) {
          console.error('Error polling for completion:', err);
          // Continue polling on error
        }
      }, 2000); // Poll every 2 seconds
    });
  };

  const calculateStatistics = (compartments: any[]): CompartmentStatistics => {
    const topLevel = compartments.filter((c) => c.level === 0);
    const subLevel = compartments.filter((c) => c.level === 1);

    const calcStats = (items: any[]) => {
      if (items.length === 0) {
        return { mean: 0, min: 0, max: 0, std: 0 };
      }

      const areas = items.map((item) => parseFloat(item.area));
      const mean = areas.reduce((a, b) => a + b, 0) / areas.length;
      const min = Math.min(...areas);
      const max = Math.max(...areas);
      const variance = areas.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / areas.length;
      const std = Math.sqrt(variance);

      return { mean, min, max, std };
    };

    return {
      totalCompartments: topLevel.length,
      totalSubCompartments: subLevel.length,
      compartmentStats: calcStats(topLevel),
      subCompartmentStats: calcStats(subLevel),
    };
  };

  const handleCancel = () => {
    setIsGenerating(false);
    setProgress(0);
    setStatusMessage('');
  };

  const getTotalSubCompartments = () => {
    return compartmentSpecs.reduce((sum, spec) => sum + spec.subCompartmentCount, 0);
  };

  return (
    <div className="generate-compartments-step">
      <div className="step-header">
        <h2>Generate Compartments & Sub-compartments</h2>
        <p>
          Divide the forest boundary into compartments, then further divide each compartment into
          sub-compartments with equal areas.
        </p>
      </div>

      {error && <ErrorNotification error={error} onDismiss={() => setError(null)} />}

      {!isGenerating && !statistics && (
        <>
          <SubCompartmentInput
            value={compartmentSpecs}
            onChange={setCompartmentSpecs}
            disabled={isGenerating}
          />

          <div className="action-buttons">
            <button className="btn btn-primary" onClick={handleGenerate} disabled={isGenerating}>
              Generate Compartments
            </button>
          </div>
        </>
      )}

      {isGenerating && (
        <div className="progress-section">
          <div className="progress-wrapper">
            <div className="progress-bar-container">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                  role="progressbar"
                  aria-valuenow={progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
              <span className="progress-percentage">{progress.toFixed(0)}%</span>
            </div>
            <p className="progress-message">{statusMessage}</p>
            <div className="progress-actions">
              <button className="btn btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </div>

          <div className="generation-info">
            <h3>Generating:</h3>
            <ul>
              <li>{compartmentSpecs.length} compartments</li>
              <li>{getTotalSubCompartments()} sub-compartments</li>
            </ul>
          </div>
        </div>
      )}

      {statistics && (
        <div className="statistics-section">
          <h3>Generation Complete!</h3>

          <div className="statistics-grid">
            <div className="stat-card">
              <h4>Compartments</h4>
              <div className="stat-item">
                <span className="stat-label">Total:</span>
                <span className="stat-value">{statistics.totalCompartments}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Area:</span>
                <span className="stat-value">{statistics.compartmentStats.mean.toFixed(2)} ha</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Min Area:</span>
                <span className="stat-value">{statistics.compartmentStats.min.toFixed(2)} ha</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Max Area:</span>
                <span className="stat-value">{statistics.compartmentStats.max.toFixed(2)} ha</span>
              </div>
            </div>

            <div className="stat-card">
              <h4>Sub-compartments</h4>
              <div className="stat-item">
                <span className="stat-label">Total:</span>
                <span className="stat-value">{statistics.totalSubCompartments}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Area:</span>
                <span className="stat-value">
                  {statistics.subCompartmentStats.mean.toFixed(2)} ha
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Min Area:</span>
                <span className="stat-value">{statistics.subCompartmentStats.min.toFixed(2)} ha</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Max Area:</span>
                <span className="stat-value">{statistics.subCompartmentStats.max.toFixed(2)} ha</span>
              </div>
            </div>
          </div>

          <div className="success-message">
            <p>
              ✓ Successfully generated {statistics.totalCompartments} compartments with{' '}
              {statistics.totalSubCompartments} sub-compartments
            </p>
            <p className="note-info">
              Areas calculated using UTM projection for accuracy (hectares)
            </p>
            <p className="label-info">
              Labels: {compartmentSpecs.map((spec) => `C${spec.compartmentNumber}S1-C${spec.compartmentNumber}S${spec.subCompartmentCount}`).join(', ')}
            </p>
          </div>

          <div className="action-buttons">
            <button className="btn btn-primary" onClick={() => window.location.reload()}>
              Continue to Next Step
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerateHierarchicalCompartmentsStep;
