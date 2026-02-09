/**
 * MapViewer component - Simplified placeholder for map display.
 * Removed interactive Leaflet map to improve performance.
 */

import React from 'react';
import '../styles/MapViewer.css';

/**
 * MapViewer component - Main map container.
 */
const MapViewer: React.FC = () => {
  return (
    <div className="map-viewer">
      <div className="map-placeholder">
        <div className="placeholder-content">
          <div className="placeholder-icon">🗺️</div>
          <h2>Map Viewer</h2>
          <p>Upload a shapefile to view the map</p>
          <p className="placeholder-subtext">Shapefiles will be displayed here after upload</p>
        </div>
      </div>

      {/* Map Legend */}
      <div className="map-legend">
        <h3>Legend</h3>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#FF0000' }}></div>
          <span>Boundary</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#0000FF' }}></div>
          <span>Compartments</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#FF0000' }}></div>
          <span>Sample Plots</span>
        </div>
      </div>
    </div>
  );
};

export default MapViewer;
