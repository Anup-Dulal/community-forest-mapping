import React, { useState, useEffect, useRef } from 'react';
import ProgressIndicator from './ProgressIndicator';
import ErrorNotification from './ErrorNotification';
import '../styles/GenerateCompartmentsStep.css';

/**
 * GenerateCompartmentsStep Component
 * Displays live compartment generation with real-time preview on map.
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 15.1, 15.2, 15.3, 15.8
 */

interface CompartmentStatistics {
  num_compartments: number;
  total_area: number;
  mean_area: number;
  min_area: number;
  max_area: number;
  std_area: number;
  area_variance: number;
  compartment_ids: string[];
}

interface GenerateCompartmentsStepProps {
  shapefileId: string;
  onComplete?: (analysisId: string, statistics: CompartmentStatistics) => void;
  onError?: (error: string) => void;
}

export const GenerateCompartmentsStep: React.FC<GenerateCompartmentsStepProps> = ({
  shapefileId,
  onComplete,
  onError,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [statistics, setStatistics] = useState<CompartmentStatistics | null>(null);
  const [compartmentCount, setCompartmentCount] = useState(4);
  const [compartmentsGenerated, setCompartmentsGenerated] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const operationIdRef = useRef<string>('');

  // Connect to WebSocket for progress updates
  useEffect(() => {
    if (!isGenerating) return;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;

      try {
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected for compartment generation');
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            // Check if this is a progress update for our operation
            if (data.operationId === operationIdRef.current) {
              setProgress(data.percentage || 0);
              setStatusMessage(data.statusMessage || '');
              setEstimatedTimeRemaining(data.estimatedTimeRemaining || 0);

              // Update compartments generated list
              if (data.current_compartment) {
                setCompartmentsGenerated((prev) => {
                  if (!prev.includes(data.current_compartment)) {
                    return [...prev, data.current_compartment];
                  }
                  return prev;
                });
              }

              // Handle completion
              if (data.status === 'completed' && data.summary) {
                setStatistics(data.summary);
                setIsGenerating(false);
                if (onComplete) {
                  onComplete(data.operationId, data.summary);
                }
              }

              // Handle error
              if (data.status === 'error') {
                setError(data.errorMessage || 'Unknown error occurred');
                setIsGenerating(false);
                if (onError) {
                  onError(data.errorMessage || 'Unknown error occurred');
                }
              }
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e);
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('WebSocket connection error');
          setIsGenerating(false);
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (e) {
        console.error('Error connecting to WebSocket:', e);
        setError('Failed to connect to WebSocket');
        setIsGenerating(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isGenerating, onComplete, onError]);

  const handleGenerateCompartments = async () => {
    if (!shapefileId) {
      setError('Shapefile ID is required');
      return;
    }

    setIsGenerating(true);
    setProgress(0);
    setStatusMessage('Starting compartment generation...');
    setError(null);
    setCompartmentsGenerated([]);
    setStatistics(null);

    try {
      // Generate operation ID
      operationIdRef.current = `compartment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      // Call backend API to start compartment generation
      const response = await fetch('/compartments/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          shapefileId,
          numCompartments: compartmentCount,
          operationId: operationIdRef.current,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to start compartment generation');
      }

      const data = await response.json();
      console.log('Compartment generation started:', data);

      // Subscribe to progress updates via WebSocket
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            action: 'subscribe',
            operationId: operationIdRef.current,
          })
        );
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      setIsGenerating(false);
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const handleCancel = () => {
    setIsGenerating(false);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: 'cancel',
          operationId: operationIdRef.current,
        })
      );
    }
  };

  const handleCompartmentCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (value > 0 && value <= 100) {
      setCompartmentCount(value);
    }
  };

  return (
    <div className="generate-compartments-step">
      <div className="step-header">
        <h2>Generate Compartments</h2>
        <p>Divide the forest boundary into equal-area compartments for inventory management.</p>
      </div>

      {error && <ErrorNotification error={error} onDismiss={() => setError(null)} />}

      <div className="compartment-controls">
        <div className="control-group">
          <label htmlFor="compartment-count">Number of Compartments:</label>
          <input
            id="compartment-count"
            type="number"
            min="1"
            max="100"
            value={compartmentCount}
            onChange={handleCompartmentCountChange}
            disabled={isGenerating}
          />
        </div>

        {!isGenerating && !statistics && (
          <button
            className="btn btn-primary"
            onClick={handleGenerateCompartments}
            disabled={isGenerating}
          >
            Generate Compartments
          </button>
        )}

        {isGenerating && (
          <button className="btn btn-secondary" onClick={handleCancel}>
            Cancel
          </button>
        )}
      </div>

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
              <span className="progress-percentage">{progress}%</span>
            </div>
            <p className="progress-message">{statusMessage}</p>
            {estimatedTimeRemaining > 0 && (
              <p className="progress-time">
                <strong>Estimated Time Remaining:</strong> {estimatedTimeRemaining}s
              </p>
            )}
            <div className="progress-actions">
              <button className="btn btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </div>

          <div className="compartments-preview">
            <h3>Compartments Generated: {compartmentsGenerated.length}</h3>
            <div className="compartment-list">
              {compartmentsGenerated.map((compartmentId) => (
                <div key={compartmentId} className="compartment-badge">
                  {compartmentId}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {statistics && (
        <div className="statistics-section">
          <h3>Compartment Statistics</h3>
          <div className="statistics-grid">
            <div className="stat-item">
              <span className="stat-label">Total Compartments:</span>
              <span className="stat-value">{statistics.num_compartments}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Area:</span>
              <span className="stat-value">{statistics.total_area.toFixed(2)} sq km</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Average Area:</span>
              <span className="stat-value">{statistics.mean_area.toFixed(2)} sq km</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Min Area:</span>
              <span className="stat-value">{statistics.min_area.toFixed(2)} sq km</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Max Area:</span>
              <span className="stat-value">{statistics.max_area.toFixed(2)} sq km</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Std Deviation:</span>
              <span className="stat-value">{statistics.std_area.toFixed(2)} sq km</span>
            </div>
          </div>

          <div className="compartment-list-final">
            <h4>Generated Compartments:</h4>
            <div className="compartment-badges">
              {statistics.compartment_ids.map((compartmentId) => (
                <div key={compartmentId} className="compartment-badge-final">
                  {compartmentId}
                </div>
              ))}
            </div>
          </div>

          <button className="btn btn-primary" onClick={() => window.location.reload()}>
            Continue to Next Step
          </button>
        </div>
      )}
    </div>
  );
};
