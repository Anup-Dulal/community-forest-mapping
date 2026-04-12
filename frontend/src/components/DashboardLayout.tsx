/**
 * DashboardLayout component - Main container for the application.
 * Manages left panel with tools, main map area, and layers panel.
 * Responsive design: mobile-first with collapsible panels.
 */

import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import ToolsPanel from './ToolsPanel';
import MapViewer from './MapViewer';

const DashboardLayout: React.FC = () => {
  const [showToolsPanel, setShowToolsPanel] = useState(true);
  const uploadStatus = useAppStore((state) => state.uploadStatus);
  const demStatus = useAppStore((state) => state.demStatus);
  const analysisStatus = useAppStore((state) => state.analysisStatus);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
      case 'complete':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'uploading':
      case 'downloading':
      case 'clipping':
      case 'processing':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'idle':
        return 'Ready';
      case 'uploading':
        return 'Uploading...';
      case 'success':
      case 'complete':
        return 'Complete';
      case 'error':
        return 'Error';
      case 'downloading':
        return 'Downloading...';
      case 'clipping':
        return 'Clipping...';
      case 'processing':
        return 'Processing...';
      default:
        return status;
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-gray-50 md:flex-row">
      {/* Left Panel - Tools (Mobile: collapsible, Desktop: always visible) */}
      <aside
        className={`${
          showToolsPanel ? 'block' : 'hidden'
        } md:block md:w-64 bg-white border-r border-gray-200 overflow-y-auto flex-shrink-0`}
      >
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">Tools</h2>
          <button
            onClick={() => setShowToolsPanel(false)}
            className="md:hidden text-gray-500 hover:text-gray-700 text-xl"
            aria-label="Close tools panel"
          >
            ×
          </button>
        </div>
        <div className="p-4">
          <ToolsPanel />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Map Viewer */}
        <div className="flex-1 min-h-0 relative">
          <MapViewer />
        </div>

        {/* Status Bar - Mobile: horizontal scroll, Desktop: grid */}
        <div className="bg-white border-t border-gray-200 p-3 md:p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
            {/* Upload Status */}
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium text-gray-700 whitespace-nowrap">Upload:</span>
              <span className={`font-semibold ${getStatusColor(uploadStatus.status)}`}>
                {getStatusText(uploadStatus.status)}
              </span>
              {uploadStatus.message && (
                <span className="text-gray-600 truncate">{uploadStatus.message}</span>
              )}
            </div>

            {/* DEM Status */}
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium text-gray-700 whitespace-nowrap">DEM:</span>
              <span className={`font-semibold ${getStatusColor(demStatus.status)}`}>
                {getStatusText(demStatus.status)}
              </span>
              {demStatus.message && (
                <span className="text-gray-600 truncate">{demStatus.message}</span>
              )}
            </div>

            {/* Analysis Status */}
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium text-gray-700 whitespace-nowrap">Analysis:</span>
              <span className={`font-semibold ${getStatusColor(analysisStatus.status)}`}>
                {getStatusText(analysisStatus.status)}
              </span>
              {analysisStatus.message && (
                <span className="text-gray-600 truncate">{analysisStatus.message}</span>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Mobile Toggle Button for Tools */}
      <div className="md:hidden fixed bottom-4 left-4 z-40">
        {!showToolsPanel && (
          <button
            onClick={() => setShowToolsPanel(true)}
            className="btn-primary text-sm py-2 px-4 shadow-lg"
            aria-label="Show tools panel"
          >
            📋 Tools
          </button>
        )}
      </div>
    </div>
  );
};

export default DashboardLayout;
