/**
 * ExportDialog component - Dialog for exporting maps and coordinates.
 */

import React, { useState } from 'react';
import { useAppStore } from '../store/appStore';
import '../styles/ExportDialog.css';

interface ExportDialogProps {
  onClose: () => void;
}

type ExportType = 'map' | 'coordinates' | 'gpx' | 'areas';
type MapFormat = 'pdf' | 'png';
type CoordFormat = 'excel' | 'csv';
type AreaType = 'compartments' | 'slope' | 'aspect';

const ExportDialog: React.FC<ExportDialogProps> = ({ onClose }) => {
  const [exportType, setExportType] = useState<ExportType>('map');
  const [format, setFormat] = useState<MapFormat | CoordFormat>('pdf');
  const [areaType, setAreaType] = useState<AreaType>('compartments');
  const [cfName, setCfName] = useState('Community Forest');
  const [cfNameNepali, setCfNameNepali] = useState('सामुदायिक वन');
  const [mapTitle, setMapTitle] = useState('Compartment Map');
  const [language, setLanguage] = useState<'english' | 'nepali'>('english');
  const [isExporting, setIsExporting] = useState(false);

  const currentAnalysisId = useAppStore((state) => state.currentAnalysisId);

  const handleExport = async () => {
    if (!currentAnalysisId) {
      alert('No analysis selected');
      return;
    }

    setIsExporting(true);

    try {
      let endpoint = '';
      let filename = '';
      let contentType = '';

      if (exportType === 'map') {
        // Export professional map layout (PDF or PNG)
        const cfNameToUse = language === 'nepali' ? cfNameNepali : cfName;
        endpoint = `/api/export/map/${format}?analysisId=${currentAnalysisId}&cfName=${encodeURIComponent(cfNameToUse)}&mapTitle=${encodeURIComponent(mapTitle)}&language=${language}`;
        filename = `compartment_map_${currentAnalysisId}.${format}`;
        contentType = format === 'pdf' ? 'application/pdf' : 'image/png';
      } else if (exportType === 'coordinates') {
        // Export polygon vertices with UTM coordinates
        const coordFormat = format === 'csv' ? 'csv' : 'excel';
        endpoint = `/api/export/coordinates/${coordFormat}?analysisId=${currentAnalysisId}`;
        filename = `compartment_coordinates_${currentAnalysisId}.${format === 'csv' ? 'csv' : 'xlsx'}`;
        contentType = format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      } else if (exportType === 'gpx') {
        // Export sample plots as GPX
        endpoint = `/api/export/gpx?analysisId=${currentAnalysisId}`;
        filename = `sample_plots_${currentAnalysisId}.gpx`;
        contentType = 'application/gpx+xml';
      } else if (exportType === 'areas') {
        // Export area summaries as Excel
        endpoint = `/api/export/areas/${areaType}?analysisId=${currentAnalysisId}`;
        filename = `${areaType}_areas_${currentAnalysisId}.xlsx`;
        contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      }

      const response = await fetch(endpoint, {
        method: 'POST',
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert(`${exportType === 'map' ? 'Map' : exportType === 'coordinates' ? 'Coordinates' : 'GPX'} exported successfully!`);
        onClose();
      } else {
        const contentType = response.headers.get('content-type');
        let errorMessage = 'Failed to export';
        
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMessage = errorData.error || errorMessage;
        } else {
          const errorText = await response.text();
          if (errorText) {
            errorMessage = errorText;
          }
        }
        
        alert(errorMessage);
      }
    } catch (error) {
      console.error('Export error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      alert(`Export failed: ${errorMessage}`);
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
                  value="map"
                  checked={exportType === 'map'}
                  onChange={(e) => setExportType(e.target.value as ExportType)}
                />
                Professional Map
              </label>
              <label>
                <input
                  type="radio"
                  value="coordinates"
                  checked={exportType === 'coordinates'}
                  onChange={(e) => setExportType(e.target.value as ExportType)}
                />
                Polygon Coordinates
              </label>
              <label>
                <input
                  type="radio"
                  value="areas"
                  checked={exportType === 'areas'}
                  onChange={(e) => setExportType(e.target.value as ExportType)}
                />
                Area Summaries
              </label>
              <label>
                <input
                  type="radio"
                  value="gpx"
                  checked={exportType === 'gpx'}
                  onChange={(e) => setExportType(e.target.value as ExportType)}
                />
                GPS Waypoints (GPX)
              </label>
            </div>
          </div>

          {/* Map Export Options */}
          {exportType === 'map' && (
            <>
              <div className="form-group">
                <label>Language / भाषा</label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as 'english' | 'nepali')}
                >
                  <option value="english">English</option>
                  <option value="nepali">नेपाली (Nepali)</option>
                </select>
              </div>
              
              {language === 'english' ? (
                <div className="form-group">
                  <label>Community Forest Name</label>
                  <input
                    type="text"
                    value={cfName}
                    onChange={(e) => setCfName(e.target.value)}
                    placeholder="Enter CF name in English"
                  />
                </div>
              ) : (
                <div className="form-group">
                  <label>सामुदायिक वनको नाम</label>
                  <input
                    type="text"
                    value={cfNameNepali}
                    onChange={(e) => setCfNameNepali(e.target.value)}
                    placeholder="नेपालीमा नाम लेख्नुहोस्"
                    style={{ fontFamily: 'Noto Sans Devanagari, sans-serif' }}
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>{language === 'english' ? 'Map Title' : 'नक्साको शीर्षक'}</label>
                <input
                  type="text"
                  value={mapTitle}
                  onChange={(e) => setMapTitle(e.target.value)}
                  placeholder={language === 'english' ? 'Enter map title' : 'शीर्षक लेख्नुहोस्'}
                  style={language === 'nepali' ? { fontFamily: 'Noto Sans Devanagari, sans-serif' } : {}}
                />
              </div>
            </>
          )}

          {/* Area Type Selection */}
          {exportType === 'areas' && (
            <div className="form-group">
              <label>Area Summary Type</label>
              <select
                value={areaType}
                onChange={(e) => setAreaType(e.target.value as AreaType)}
              >
                <option value="compartments">Compartment Areas</option>
                <option value="slope">Slope Area Summary</option>
                <option value="aspect">Aspect Area Summary</option>
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
              {exportType === 'map' ? (
                <>
                  <option value="pdf">PDF (Print Quality)</option>
                  <option value="png">PNG (Web/Presentation)</option>
                </>
              ) : exportType === 'coordinates' ? (
                <>
                  <option value="excel">Excel (XLSX)</option>
                  <option value="csv">CSV</option>
                </>
              ) : exportType === 'areas' ? (
                <option value="excel">Excel (XLSX)</option>
              ) : (
                <option value="gpx">GPX</option>
              )}
            </select>
          </div>

          {/* Format Description */}
          <div className="format-description">
            {exportType === 'map' && format === 'pdf' && (
              <p>Professional PDF map with CF name, north arrow, scale bar, legend, and area tables. Print-ready A4 format.</p>
            )}
            {exportType === 'map' && format === 'png' && (
              <p>High-resolution PNG image suitable for presentations and web viewing.</p>
            )}
            {exportType === 'coordinates' && format === 'excel' && (
              <p>Excel spreadsheet with polygon vertices in UTM coordinates. Includes compartment labels and formatted columns.</p>
            )}
            {exportType === 'coordinates' && format === 'csv' && (
              <p>CSV file with polygon vertices in UTM coordinates. Compatible with any spreadsheet application.</p>
            )}
            {exportType === 'areas' && areaType === 'compartments' && (
              <p>Excel file with compartment and sub-compartment areas in hectares. Includes Compartment ID, Sub-compartment ID, and Area.</p>
            )}
            {exportType === 'areas' && areaType === 'slope' && (
              <p>Excel file with slope area summary. Shows total area in hectares for each slope class (0-20°, 20-30°, &gt;30°).</p>
            )}
            {exportType === 'areas' && areaType === 'aspect' && (
              <p>Excel file with aspect area summary. Shows total area in hectares for each direction (N, NE, E, SE, S, SW, W, NW).</p>
            )}
            {exportType === 'gpx' && (
              <p>GPX file with sample plot waypoints for GPS devices. Load directly into your GPS or mapping app.</p>
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
