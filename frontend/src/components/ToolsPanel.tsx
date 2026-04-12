/**
 * ToolsPanel component - Left panel with tools for upload, DEM status, and map generation.
 * Responsive design with Tailwind CSS.
 */

import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import UploadPanel from './UploadPanel';
import ExportDialog from './ExportDialog';
import { loadAllLayers } from '../utils/layerLoader';

const ToolsPanel: React.FC = () => {
  const [showUploadPanel, setShowUploadPanel] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showCompartmentConfig, setShowCompartmentConfig] = useState(false);
  const [numCompartments, setNumCompartments] = useState(3);
  const [subCompartmentCounts, setSubCompartmentCounts] = useState<number[]>([8, 8, 8]);

  const demStatus = useAppStore((state) => state.demStatus);
  const analysisStatus = useAppStore((state) => state.analysisStatus);
  const currentAnalysisId = useAppStore((state) => state.currentAnalysisId);
  const currentShapefileId = useAppStore((state) => state.currentShapefileId);

  // Update sub-compartment counts when number of compartments changes
  const handleNumCompartmentsChange = (num: number) => {
    setNumCompartments(num);
    const newCounts = Array(num).fill(8);
    setSubCompartmentCounts(newCounts);
  };

  const handleSubCompartmentCountChange = (index: number, count: number) => {
    const newCounts = [...subCompartmentCounts];
    newCounts[index] = count;
    setSubCompartmentCounts(newCounts);
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'complete':
        return 'bg-green-100 text-green-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'downloading':
      case 'clipping':
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'idle':
        return '⏸';
      case 'downloading':
        return '⬇️';
      case 'clipping':
        return '✂️';
      case 'complete':
        return '✅';
      case 'error':
        return '❌';
      case 'processing':
        return '⚙️';
      default:
        return '•';
    }
  };

  const handleGenerateMaps = async () => {
    if (!currentShapefileId) {
      alert('Please upload a shapefile first');
      return;
    }

    try {
      const setAnalysisStatus = useAppStore.getState().setAnalysisStatus;
      const setCurrentAnalysisId = useAppStore.getState().setCurrentAnalysisId;
      
      // Step 1: Get shapefile data to extract boundary WKT
      setAnalysisStatus({ status: 'processing', message: 'Loading shapefile...' });
      
      const shapefileResponse = await fetch(`/api/shapefile/${currentShapefileId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!shapefileResponse.ok) {
        throw new Error('Failed to load shapefile');
      }

      const shapefileData = await shapefileResponse.json();
      const boundaryWkt = shapefileData.geometry;

      if (!boundaryWkt) {
        throw new Error('Shapefile geometry not found');
      }

      // Step 2: Generate hierarchical compartments with user-specified configuration
      setAnalysisStatus({ status: 'processing', message: 'Generating hierarchical compartments...' });

      // Build compartment configuration from user input
      const compartmentConfig = subCompartmentCounts.map((count, index) => ({
        compartmentNumber: index + 1,
        subCompartmentCount: count,
      }));

      const hierarchicalResponse = await fetch('/api/compartments/generate-hierarchical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          boundaryWkt,
          analysisId: currentShapefileId,
          compartments: compartmentConfig,
        }),
      });

      if (!hierarchicalResponse.ok) {
        const error = await hierarchicalResponse.text();
        throw new Error(`Failed to generate hierarchical compartments: ${error}`);
      }

      const hierarchicalData = await hierarchicalResponse.json();
      const analysisId = hierarchicalData.analysisId;
      setCurrentAnalysisId(analysisId);

      // Step 3: Poll for compartment generation completion
      setAnalysisStatus({ status: 'processing', message: 'Processing compartments...' });

      let compartmentComplete = false;
      let attempts = 0;
      const maxAttempts = 120;
      let compartmentGeometryPath = '';

      while (!compartmentComplete && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 2000));

        try {
          const detailsResponse = await fetch(`/api/compartments/${analysisId}/details`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          });

          if (detailsResponse.ok) {
            const details = await detailsResponse.json();
            if (details.status === 'complete') {
              compartmentComplete = true;
              compartmentGeometryPath = details.compartmentGeometryPath || '';
            } else if (details.status === 'error') {
              throw new Error('Compartment generation failed');
            }
          }
        } catch (e) {
          console.warn('Error checking compartment status, retrying...');
        }
        attempts++;
      }

      if (!compartmentComplete) {
        throw new Error('Compartment generation timed out');
      }

      // Step 4: Generate sample plots for sub-compartments
      setAnalysisStatus({ status: 'processing', message: 'Generating sample plots...' });

      try {
        // Use the compartment geometry path from the details response
        if (compartmentGeometryPath) {
          const samplePlotsResponse = await fetch('/api/sample-plots/generate-hierarchical', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              analysisId,
              compartmentGeometryPath,
              samplingIntensity: 0.01,
              minPlotsPerCompartment: 5,
              distributionMethod: 'systematic',
            }),
          });

          if (!samplePlotsResponse.ok) {
            console.warn('Sample plot generation failed, continuing...');
          }
        }
      } catch (samplePlotError) {
        console.warn('Error generating sample plots:', samplePlotError);
      }

      // Step 5: Download and process DEM (optional)
      setAnalysisStatus({ status: 'processing', message: 'Downloading DEM data...' });

      try {
        const demResponse = await fetch(`/api/dem/download?shapefileId=${currentShapefileId}&source=SRTM`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (demResponse.ok) {
          const demData = await demResponse.json();
          const demId = demData.demId;

          // Wait for DEM processing
          let demComplete = false;
          let demAttempts = 0;
          const maxDemAttempts = 60;

          while (!demComplete && demAttempts < maxDemAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000));

            const statusResponse = await fetch(`/api/dem/${demId}/status`, {
              method: 'GET',
              headers: { 'Content-Type': 'application/json' },
            });

            if (statusResponse.ok) {
              const status = await statusResponse.json();
              if (status.status === 'clipped' || status.status === 'downloaded') {
                demComplete = true;

                // Calculate slope and aspect using analysisId
                setAnalysisStatus({ status: 'processing', message: 'Calculating terrain...' });

                await fetch(`/api/terrain/slope?analysisId=${analysisId}`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                });

                await fetch(`/api/terrain/aspect?analysisId=${analysisId}`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                });
              }
            }
            demAttempts++;
          }
        }
      } catch (demError) {
        console.warn('DEM processing failed, continuing without terrain data...');
      }

      setAnalysisStatus({
        status: 'complete',
        message: 'Hierarchical compartments generated successfully!',
      });

      // Load layers on map
      setAnalysisStatus({ status: 'processing', message: 'Loading layers on map...' });
      
      try {
        let mapReady = false;
        let mapAttempts = 0;
        const maxMapAttempts = 20;
        
        while (!mapReady && mapAttempts < maxMapAttempts) {
          const mapInstance = (window as any).__mapInstance;
          const isReady = (window as any).__mapReady;
          
          if (mapInstance && isReady) {
            mapReady = true;
            const layers = await loadAllLayers(analysisId, currentShapefileId, mapInstance);
            
            if (layers.size > 0) {
              setAnalysisStatus({
                status: 'complete',
                message: `Hierarchical compartments generated! ${layers.size} layers loaded.`,
              });
            } else {
              setAnalysisStatus({
                status: 'complete',
                message: 'Compartments generated. Click "Refresh Layers" to display them.',
              });
            }
          } else {
            await new Promise(resolve => setTimeout(resolve, 200));
            mapAttempts++;
          }
        }
        
        if (!mapReady) {
          setAnalysisStatus({
            status: 'complete',
            message: 'Compartments generated. Refresh the page to view them.',
          });
        }
      } catch (layerError) {
        console.error('Error loading layers:', layerError);
        setAnalysisStatus({
          status: 'complete',
          message: 'Compartments generated. Use "Refresh Layers" button to load them.',
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate maps';
      const setAnalysisStatus = useAppStore.getState().setAnalysisStatus;
      setAnalysisStatus({
        status: 'error',
        message: errorMessage,
      });
      alert(`Error: ${errorMessage}`);
    }
  };

  const handleDownloadOutputs = () => {
    if (!currentAnalysisId) {
      alert('Please complete analysis first');
      return;
    }
    setShowExportDialog(true);
  };

  const handleRefreshLayers = async () => {
    if (!currentAnalysisId || !currentShapefileId) {
      alert('Please generate maps first');
      return;
    }

    try {
      const setAnalysisStatus = useAppStore.getState().setAnalysisStatus;
      setAnalysisStatus({ status: 'processing', message: 'Refreshing layers...' });

      const mapInstance = (window as any).__mapInstance;
      if (!mapInstance) {
        alert('Map not ready. Please wait a moment and try again.');
        setAnalysisStatus({ status: 'complete', message: 'Map not ready' });
        return;
      }

      // Use analysisId for analysis results and shapefileId for boundary
      const layers = await loadAllLayers(currentAnalysisId, currentShapefileId, mapInstance);
      
      if (layers.size > 0) {
        setAnalysisStatus({
          status: 'complete',
          message: `${layers.size} layers loaded successfully`,
        });
      } else {
        setAnalysisStatus({
          status: 'complete',
          message: 'No layers found. Generate maps first.',
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load layers';
      alert(`Error: ${errorMessage}`);
      const setAnalysisStatus = useAppStore.getState().setAnalysisStatus;
      setAnalysisStatus({
        status: 'error',
        message: errorMessage,
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Upload Tool */}
      <div className="card">
        <button
          onClick={() => setShowUploadPanel(!showUploadPanel)}
          className="btn-primary w-full text-left flex items-center gap-2"
        >
          <span>📁</span>
          <span>Upload Shapefile</span>
        </button>
        {showUploadPanel && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <UploadPanel onClose={() => setShowUploadPanel(false)} />
          </div>
        )}
      </div>

      {/* DEM Status */}
      <div className="card">
        <h3 className="font-semibold text-gray-800 mb-2">DEM Status</h3>
        <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeColor(demStatus.status)}`}>
          {getStatusIcon(demStatus.status)} {demStatus.status.charAt(0).toUpperCase() + demStatus.status.slice(1)}
        </div>
        {demStatus.message && (
          <p className="text-sm text-gray-600 mt-2">{demStatus.message}</p>
        )}
        {demStatus.source && (
          <p className="text-xs text-gray-500 mt-1">Source: {demStatus.source}</p>
        )}
      </div>

      {/* Generate Maps */}
      <div className="card">
        <button
          onClick={() => setShowCompartmentConfig(!showCompartmentConfig)}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          <span>⚙️</span>
          <span>Configure Compartments</span>
        </button>
        
        {showCompartmentConfig && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Compartments
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={numCompartments}
                onChange={(e) => handleNumCompartmentsChange(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Sub-compartments per Compartment
              </label>
              {Array.from({ length: numCompartments }).map((_, index) => (
                <div key={index} className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 w-24">C{index + 1}:</span>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={subCompartmentCounts[index] || 8}
                    onChange={(e) => handleSubCompartmentCountChange(index, parseInt(e.target.value) || 1)}
                    className="flex-1 px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-xs text-gray-500">sub-comps</span>
                </div>
              ))}
            </div>
            
            <p className="text-xs text-gray-500 mt-2">
              Total: {numCompartments} compartments, {subCompartmentCounts.reduce((a, b) => a + b, 0)} sub-compartments
            </p>
          </div>
        )}
        
        <button
          onClick={handleGenerateMaps}
          disabled={!currentShapefileId || analysisStatus.status === 'processing'}
          className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mt-3"
        >
          <span>🗺️</span>
          <span>Generate Maps</span>
        </button>
        <p className="text-xs text-gray-600 mt-2">
          Generate compartments, sub-compartments, sample plots, and terrain maps
        </p>
      </div>

      {/* Refresh Layers */}
      <div className="card">
        <button
          onClick={handleRefreshLayers}
          disabled={!currentAnalysisId || !currentShapefileId || analysisStatus.status === 'processing'}
          className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>🔄</span>
          <span>Refresh Layers</span>
        </button>
        <p className="text-xs text-gray-600 mt-2">
          Reload map layers if they don't appear automatically
        </p>
      </div>

      {/* Download Outputs */}
      <div className="card">
        <button
          onClick={handleDownloadOutputs}
          disabled={!currentAnalysisId || analysisStatus.status !== 'complete'}
          className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>💾</span>
          <span>Download Outputs</span>
        </button>
        <p className="text-xs text-gray-600 mt-2">
          Export maps and coordinates as PDF, PNG, CSV, or Excel
        </p>
      </div>

      {/* Export Dialog */}
      {showExportDialog && (
        <ExportDialog onClose={() => setShowExportDialog(false)} />
      )}

      {/* Analysis Status */}
      {currentAnalysisId && (
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-2">Analysis Status</h3>
          <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeColor(analysisStatus.status)}`}>
            {getStatusIcon(analysisStatus.status)} {analysisStatus.status.charAt(0).toUpperCase() + analysisStatus.status.slice(1)}
          </div>
          {analysisStatus.message && (
            <p className="text-sm text-gray-600 mt-2">{analysisStatus.message}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default ToolsPanel;
