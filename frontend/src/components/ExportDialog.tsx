/**
 * ExportDialog component - Dialog for exporting maps and coordinates.
 */

import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import '../styles/ExportDialog.css';

interface ExportDialogProps {
  onClose: () => void;
}

const ExportDialog: React.FC<ExportDialogProps> = ({ onClose }) => {
  const [exportType, setExportType] = useState<'maps' | 'coordinates'>('maps');
  const [mapType, setMapType] = useState<'slope' | 'aspect' | 'compartment' | 'sample_plots'>('slope');
  const [format, setFormat] = useState<'png' | 'pdf' | 'csv' | 'excel'>('png');
  const [isExporting, setIsExporting] = useState(false);

  const currentAnalysisId = useAppStore((state) => state.currentAnalysisId);

  const handleExport = async () => {
    if (!currentAnalysisId) {
      alert('No analysis selected');
      return;
    }

    setIsExporting(true);

    try {
      if (exportType === 'maps') {
        // Export map
        const response = await fetch(
          `/api/maps/export/${mapType}?analysisResultId=${currentAnalysisId}&format=${format}`,
          {
            method: 'POST',
          }
        );

        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${mapType}_map.${format}`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
          alert('Failed to export map');
        }
      } else {
        // Export coordinates
        const endpoint = format === 'csv' ? 'csv' : 'excel';
        const response = await fetch(
          `/api/export/coordinates/${endpoint}?analysisResultId=${currentAnalysisId}`
        );

        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `sample_plots.${format === 'csv' ? 'csv' : 'xlsx'}`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
          alert('Failed to export coordinates');
        }
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-dialog-overlay">
      <div className="export-dialog">
        <div className="dialog-header">
          <h2>Export Data</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="dialog-content">
          {/* Export Type Selection */}
          <div className="form-group">
            <label>Export Type</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  value="maps"
                  checked={exportType === 'maps'}
                  onChange={(e) => setExportType(e.target.value as 'maps' | 'coordinates')}
                />
                Maps
              </label>
              <label>
                <input
                  type="radio"
                  value="coordinates"
                  checked={exportType === 'coordinates'}
                  onChange={(e) => setExportType(e.target.value as 'maps' | 'coordinates')}
                />
                Coordinates
              </label>
            </div>
          </div>

          {/* Map Type Selection */}
          {exportType === 'maps' && (
            <div className="form-group">
              <label>Map Type</label>
              <select
                value={mapType}
                onChange={(e) => setMapType(e.target.value as any)}
              >
                <option value="slope">Slope Classification</option>
                <option value="aspect">Aspect Direction</option>
                <option value="compartment">Compartment Division</option>
                <option value="sample_plots">Sample Plot Distribution</option>
              </select>
            </div>
          )}

          {/* Format Selection */}
          <div className="form-group">
            <label>Format</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value as any)}
            >
              {exportType === 'maps' ? (
                <>
                  <option value="png">PNG (Web)</option>
                  <option value="pdf">PDF (Print)</option>
                </>
              ) : (
                <>
                  <option value="csv">CSV</option>
                  <option value="excel">Excel</option>
                </>
              )}
            </select>
          </div>

          {/* Format Description */}
          <div className="format-description">
            {exportType === 'maps' && format === 'png' && (
              <p>PNG format is suitable for web viewing and presentations.</p>
            )}
            {exportType === 'maps' && format === 'pdf' && (
              <p>PDF format is suitable for printing and professional documentation.</p>
            )}
            {exportType === 'coordinates' && format === 'csv' && (
              <p>CSV format can be opened in any spreadsheet application.</p>
            )}
            {exportType === 'coordinates' && format === 'excel' && (
              <p>Excel format includes formatting and is ready for analysis.</p>
            )}
          </div>
        </div>

        <div className="dialog-footer">
          <button
            className="button secondary"
            onClick={onClose}
            disabled={isExporting}
          >
            Cancel
          </button>
          <button
            className="button primary"
            onClick={handleExport}
            disabled={isExporting}
          >
            {isExporting ? 'Exporting...' : 'Export'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportDialog;
