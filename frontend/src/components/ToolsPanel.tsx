/**
 * ToolsPanel component - Left panel with tools for upload, DEM status, and map generation.
 */

import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import UploadPanel from './UploadPanel';
import ExportDialog from './ExportDialog';
import '../styles/ToolsPanel.css';

const ToolsPanel: React.FC = () => {
  const [showUploadPanel, setShowUploadPanel] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [activeTab, setActiveTab] = useState<'upload' | 'export'>('upload');

  const demStatus = useAppStore((state) => state.demStatus);
  const analysisStatus = useAppStore((state) => state.analysisStatus);
  const currentAnalysisId = useAppStore((state) => state.currentAnalysisId);

  const handleGenerateMaps = () => {
    if (!currentAnalysisId) {
      alert('Please upload a shapefile first');
      return;
    }
    // Map generation would be triggered here
    alert('Map generation started');
  };

  const handleDownloadOutputs = () => {
    if (!currentAnalysisId) {
      alert('Please complete analysis first');
      return;
    }
    setShowExportDialog(true);
  };

  return (
    <div className="tools-panel">
      {/* Upload Tool */}
      <div className="tool-section">
        <button
          className="tool-button primary"
          onClick={() => {
            setShowUploadPanel(!showUploadPanel);
            setActiveTab('upload');
          }}
        >
          📁 Upload Shapefile
        </button>
        {showUploadPanel && (
          <div className="tool-content">
            <UploadPanel onClose={() => setShowUploadPanel(false)} />
          </div>
        )}
      </div>

      {/* DEM Status */}
      <div className="tool-section">
        <div className="tool-info">
          <h3>DEM Status</h3>
          <div className={`status-badge ${demStatus.status}`}>
            {demStatus.status === 'idle' && '⏸ Ready'}
            {demStatus.status === 'downloading' && '⬇️ Downloading...'}
            {demStatus.status === 'clipping' && '✂️ Clipping...'}
            {demStatus.status === 'complete' && '✅ Complete'}
            {demStatus.status === 'error' && '❌ Error'}
          </div>
          {demStatus.message && (
            <p className="status-message">{demStatus.message}</p>
          )}
          {demStatus.source && (
            <p className="status-detail">Source: {demStatus.source}</p>
          )}
        </div>
      </div>

      {/* Generate Maps */}
      <div className="tool-section">
        <button
          className="tool-button"
          onClick={handleGenerateMaps}
          disabled={!currentAnalysisId || analysisStatus.status === 'processing'}
        >
          🗺️ Generate Maps
        </button>
        <p className="tool-description">
          Generate slope, aspect, compartment, and sample plot maps
        </p>
      </div>

      {/* Download Outputs */}
      <div className="tool-section">
        <button
          className="tool-button"
          onClick={handleDownloadOutputs}
          disabled={!currentAnalysisId || analysisStatus.status !== 'complete'}
        >
          💾 Download Outputs
        </button>
        <p className="tool-description">
          Export maps and coordinates as PDF, PNG, CSV, or Excel
        </p>
      </div>

      {/* Export Dialog */}
      {showExportDialog && (
        <ExportDialog onClose={() => setShowExportDialog(false)} />
      )}

      {/* Analysis Status */}
      {currentAnalysisId && (
        <div className="tool-section">
          <div className="tool-info">
            <h3>Analysis Status</h3>
            <div className={`status-badge ${analysisStatus.status}`}>
              {analysisStatus.status === 'idle' && '⏸ Ready'}
              {analysisStatus.status === 'processing' && '⚙️ Processing...'}
              {analysisStatus.status === 'complete' && '✅ Complete'}
              {analysisStatus.status === 'error' && '❌ Error'}
            </div>
            {analysisStatus.message && (
              <p className="status-message">{analysisStatus.message}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolsPanel;
