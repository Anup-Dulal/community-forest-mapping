/**
 * DashboardLayout component - Main container for the application.
 * Manages left panel with tools, main map area, and layers panel.
 */

import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import ToolsPanel from './ToolsPanel';
import MapViewer from './MapViewer';
import LayersPanel from './LayersPanel';
import '../styles/DashboardLayout.css';

const DashboardLayout: React.FC = () => {
  const [showLayersPanel, setShowLayersPanel] = useState(true);
  const uploadStatus = useAppStore((state) => state.uploadStatus);
  const demStatus = useAppStore((state) => state.demStatus);
  const analysisStatus = useAppStore((state) => state.analysisStatus);

  return (
    <div className="dashboard-layout">
      {/* Left Panel - Tools */}
      <aside className="dashboard-left-panel">
        <div className="panel-header">
          <h2>Tools</h2>
        </div>
        <ToolsPanel />
      </aside>

      {/* Main Content Area */}
      <main className="dashboard-main">
        {/* Map Viewer */}
        <div className="map-container">
          <MapViewer />
        </div>

        {/* Status Bar */}
        <div className="status-bar">
          <div className="status-item">
            <span className="status-label">Upload:</span>
            <span className={`status-value ${uploadStatus.status}`}>
              {uploadStatus.status === 'idle' && 'Ready'}
              {uploadStatus.status === 'uploading' && 'Uploading...'}
              {uploadStatus.status === 'success' && 'Complete'}
              {uploadStatus.status === 'error' && 'Error'}
            </span>
            {uploadStatus.message && (
              <span className="status-message">{uploadStatus.message}</span>
            )}
          </div>

          <div className="status-item">
            <span className="status-label">DEM:</span>
            <span className={`status-value ${demStatus.status}`}>
              {demStatus.status === 'idle' && 'Ready'}
              {demStatus.status === 'downloading' && 'Downloading...'}
              {demStatus.status === 'clipping' && 'Clipping...'}
              {demStatus.status === 'complete' && 'Complete'}
              {demStatus.status === 'error' && 'Error'}
            </span>
            {demStatus.message && (
              <span className="status-message">{demStatus.message}</span>
            )}
          </div>

          <div className="status-item">
            <span className="status-label">Analysis:</span>
            <span className={`status-value ${analysisStatus.status}`}>
              {analysisStatus.status === 'idle' && 'Ready'}
              {analysisStatus.status === 'processing' && 'Processing...'}
              {analysisStatus.status === 'complete' && 'Complete'}
              {analysisStatus.status === 'error' && 'Error'}
            </span>
            {analysisStatus.message && (
              <span className="status-message">{analysisStatus.message}</span>
            )}
          </div>
        </div>
      </main>

      {/* Right Panel - Layers */}
      {showLayersPanel && (
        <aside className="dashboard-right-panel">
          <div className="panel-header">
            <h2>Layers</h2>
            <button
              className="close-button"
              onClick={() => setShowLayersPanel(false)}
              title="Close layers panel"
            >
              ×
            </button>
          </div>
          <LayersPanel />
        </aside>
      )}

      {/* Toggle Layers Panel Button */}
      {!showLayersPanel && (
        <button
          className="toggle-layers-button"
          onClick={() => setShowLayersPanel(true)}
          title="Show layers panel"
        >
          Layers
        </button>
      )}
    </div>
  );
};

export default DashboardLayout;
