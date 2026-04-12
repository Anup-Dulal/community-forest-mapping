import React, { useState, useEffect, useRef } from 'react';
import ProgressIndicator from './ProgressIndicator';
import ErrorNotification from './ErrorNotification';
import '../styles/CalculateTerrainStep.css';

/**
 * CalculateTerrainStep Component
 * Displays live slope and aspect calculation with real-time preview on map.
 * Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 15.4, 15.5, 15.6, 15.7, 15.8
 */

interface SlopeStatistics {
  min: number;
  max: number;
  mean: number;
  std: number;
  median: number;
}

interface SlopeDistribution {
  gentle_0_20: {
    count: number;
    percentage: number;
  };
  moderate_20_30: {
    count: number;
    percentage: number;
  };
  steep_30_plus: {
    count: number;
    percentage: number;
  };
}

interface AspectStatistics {
  min: number;
  max: number;
  mean: number;
  std: number;
}

interface AspectDistribution {
  [key: string]: {
    count: number;
    percentage: number;
  };
}

interface TerrainAnalysisResults {
  slope_statistics: SlopeStatistics;
  aspect_statistics: AspectStatistics;
  slope_distribution: SlopeDistribution;
  aspect_distribution: AspectDistribution;
  slope_path: string;
  slope_classified_path: string;
  aspect_path: string;
  aspect_classified_path: string;
  elapsed_time: number;
}

interface CalculateTerrainStepProps {
  shapefileId: string;
  demPath?: string;
  onComplete?: (analysisId: string, results: TerrainAnalysisResults) => void;
  onError?: (error: string) => void;
}

export const CalculateTerrainStep: React.FC<CalculateTerrainStepProps> = ({
  shapefileId,
  demPath,
  onComplete,
  onError,
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<TerrainAnalysisResults | null>(null);
  const [activeTab, setActiveTab] = useState<'slope' | 'aspect'>('slope');
  const wsRef = useRef<WebSocket | null>(null);
  const operationIdRef = useRef<string>('');

  // Connect to WebSocket for progress updates
  useEffect(() => {
    if (!isAnalyzing) return;

    const connectWebSocket = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;

      try {
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('WebSocket connected for terrain analysis');
        };

        wsRef.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            // Check if this is a progress update for our operation
            if (data.operationId === operationIdRef.current) {
              setProgress(data.percentage || 0);
              setStatusMessage(data.statusMessage || '');
              setEstimatedTimeRemaining(data.estimatedTimeRemaining || 0);

              // Handle completion
              if (data.status === 'completed' && data.summary) {
                setResults(data.summary);
                setIsAnalyzing(false);
                if (onComplete) {
                  onComplete(data.operationId, data.summary);
                }
              }

              // Handle error
              if (data.status === 'error') {
                setError(data.errorMessage || 'Unknown error occurred');
                setIsAnalyzing(false);
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
          setIsAnalyzing(false);
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
        };
      } catch (e) {
        console.error('Error connecting to WebSocket:', e);
        setError('Failed to connect to WebSocket');
        setIsAnalyzing(false);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isAnalyzing, onComplete, onError]);

  const handleAnalyzeTerrain = async () => {
    if (!shapefileId) {
      setError('Shapefile ID is required');
      return;
    }

    setIsAnalyzing(true);
    setProgress(0);
    setStatusMessage('Starting terrain analysis...');
    setError(null);
    setResults(null);

    try {
      // Generate operation ID
      operationIdRef.current = `terrain-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      // Call backend API to start terrain analysis
      const response = await fetch('/terrain/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          shapefileId,
          demPath,
          operationId: operationIdRef.current,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to start terrain analysis');
      }

      const data = await response.json();
      console.log('Terrain analysis started:', data);

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
      setIsAnalyzing(false);
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const handleCancel = () => {
    setIsAnalyzing(false);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: 'cancel',
          operationId: operationIdRef.current,
        })
      );
    }
  };

  const getSlopeColor = (percentage: number): string => {
    if (percentage < 20) return '#2ecc71'; // Green for gentle
    if (percentage < 30) return '#f39c12'; // Orange for moderate
    return '#e74c3c'; // Red for steep
  };

  const getAspectColor = (direction: string): string => {
    const colors: { [key: string]: string } = {
      N: '#0066cc',   // Blue
      NE: '#0099ff',  // Light Blue
      E: '#00cc99',   // Teal
      SE: '#00ff66',  // Light Green
      S: '#ffff00',   // Yellow
      SW: '#ff9900',  // Orange
      W: '#ff6600',   // Dark Orange
      NW: '#cc0000',  // Red
    };
    return colors[direction] || '#999999';
  };

  return (
    <div className="calculate-terrain-step">
      <div className="step-header">
        <h2>Calculate Terrain Analysis</h2>
        <p>Analyze slope and aspect to understand terrain characteristics.</p>
      </div>

      {error && <ErrorNotification error={error} onDismiss={() => setError(null)} />}

      <div className="terrain-controls">
        {!isAnalyzing && !results && (
          <button
            className="btn btn-primary"
            onClick={handleAnalyzeTerrain}
            disabled={isAnalyzing}
          >
            Analyze Terrain
          </button>
        )}

        {isAnalyzing && (
          <button className="btn btn-secondary" onClick={handleCancel}>
            Cancel
          </button>
        )}
      </div>

      {isAnalyzing && (
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
        </div>
      )}

      {results && (
        <div className="results-section">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'slope' ? 'active' : ''}`}
              onClick={() => setActiveTab('slope')}
            >
              Slope Analysis
            </button>
            <button
              className={`tab ${activeTab === 'aspect' ? 'active' : ''}`}
              onClick={() => setActiveTab('aspect')}
            >
              Aspect Analysis
            </button>
          </div>

          {activeTab === 'slope' && (
            <div className="tab-content">
              <h3>Slope Statistics</h3>
              <div className="statistics-grid">
                <div className="stat-item">
                  <span className="stat-label">Minimum Slope:</span>
                  <span className="stat-value">{results.slope_statistics.min.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Maximum Slope:</span>
                  <span className="stat-value">{results.slope_statistics.max.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Mean Slope:</span>
                  <span className="stat-value">{results.slope_statistics.mean.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Std Deviation:</span>
                  <span className="stat-value">{results.slope_statistics.std.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Median Slope:</span>
                  <span className="stat-value">{results.slope_statistics.median.toFixed(2)}°</span>
                </div>
              </div>

              <h3>Slope Classification Distribution</h3>
              <div className="distribution-chart">
                <div className="distribution-item">
                  <div className="distribution-bar-container">
                    <div
                      className="distribution-bar"
                      style={{
                        width: `${results.slope_distribution.gentle_0_20.percentage}%`,
                        backgroundColor: getSlopeColor(15),
                      }}
                    />
                  </div>
                  <div className="distribution-label">
                    <span className="label-text">Gentle (0-20°)</span>
                    <span className="label-value">
                      {results.slope_distribution.gentle_0_20.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="distribution-item">
                  <div className="distribution-bar-container">
                    <div
                      className="distribution-bar"
                      style={{
                        width: `${results.slope_distribution.moderate_20_30.percentage}%`,
                        backgroundColor: getSlopeColor(25),
                      }}
                    />
                  </div>
                  <div className="distribution-label">
                    <span className="label-text">Moderate (20-30°)</span>
                    <span className="label-value">
                      {results.slope_distribution.moderate_20_30.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="distribution-item">
                  <div className="distribution-bar-container">
                    <div
                      className="distribution-bar"
                      style={{
                        width: `${results.slope_distribution.steep_30_plus.percentage}%`,
                        backgroundColor: getSlopeColor(35),
                      }}
                    />
                  </div>
                  <div className="distribution-label">
                    <span className="label-text">Steep (&gt;30°)</span>
                    <span className="label-value">
                      {results.slope_distribution.steep_30_plus.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'aspect' && (
            <div className="tab-content">
              <h3>Aspect Statistics</h3>
              <div className="statistics-grid">
                <div className="stat-item">
                  <span className="stat-label">Minimum Aspect:</span>
                  <span className="stat-value">{results.aspect_statistics.min.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Maximum Aspect:</span>
                  <span className="stat-value">{results.aspect_statistics.max.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Mean Aspect:</span>
                  <span className="stat-value">{results.aspect_statistics.mean.toFixed(2)}°</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Std Deviation:</span>
                  <span className="stat-value">{results.aspect_statistics.std.toFixed(2)}°</span>
                </div>
              </div>

              <h3>Aspect Direction Distribution</h3>
              <div className="aspect-compass">
                {Object.entries(results.aspect_distribution).map(([direction, data]) => (
                  <div key={direction} className="compass-item">
                    <div
                      className="compass-color"
                      style={{ backgroundColor: getAspectColor(direction) }}
                    />
                    <div className="compass-label">
                      <span className="direction">{direction}</span>
                      <span className="percentage">{data.percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="distribution-chart">
                {Object.entries(results.aspect_distribution).map(([direction, data]) => (
                  <div key={direction} className="distribution-item">
                    <div className="distribution-bar-container">
                      <div
                        className="distribution-bar"
                        style={{
                          width: `${data.percentage}%`,
                          backgroundColor: getAspectColor(direction),
                        }}
                      />
                    </div>
                    <div className="distribution-label">
                      <span className="label-text">{direction}</span>
                      <span className="label-value">{data.percentage.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="results-footer">
            <p className="analysis-time">
              Analysis completed in {results.elapsed_time.toFixed(2)} seconds
            </p>
            <button className="btn btn-primary" onClick={() => window.location.reload()}>
              Continue to Next Step
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
