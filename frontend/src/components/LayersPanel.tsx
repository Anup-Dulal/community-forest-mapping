/**
 * LayersPanel component - Right panel for managing layer visibility.
 */

import React from 'react';
import { useAppStore } from '../store/appStore';
import '../styles/LayersPanel.css';

interface LayerItem {
  id: keyof import('../types').LayerVisibility;
  label: string;
  description: string;
  icon: string;
}

const LAYERS: LayerItem[] = [
  {
    id: 'boundary',
    label: 'Boundary',
    description: 'Community forest boundary',
    icon: '🗺️',
  },
  {
    id: 'dem',
    label: 'DEM',
    description: 'Digital Elevation Model',
    icon: '⛰️',
  },
  {
    id: 'slope',
    label: 'Slope',
    description: 'Slope classification (0-20°, 20-30°, >30°)',
    icon: '📈',
  },
  {
    id: 'aspect',
    label: 'Aspect',
    description: 'Aspect direction (N, NE, E, SE, S, SW, W, NW)',
    icon: '🧭',
  },
  {
    id: 'compartments',
    label: 'Compartments',
    description: 'Equal-area compartment divisions',
    icon: '📦',
  },
  {
    id: 'samplePlots',
    label: 'Sample Plots',
    description: 'Sample plot locations',
    icon: '📍',
  },
];

const LayersPanel: React.FC = () => {
  const layers = useAppStore((state) => state.mapState.layers);
  const setLayerVisibility = useAppStore((state) => state.setLayerVisibility);

  const handleLayerToggle = (layerId: keyof import('../types').LayerVisibility) => {
    setLayerVisibility(layerId, !layers[layerId]);
  };

  return (
    <div className="layers-panel">
      <div className="layers-list">
        {LAYERS.map((layer) => (
          <div key={layer.id} className="layer-item">
            <label className="layer-checkbox">
              <input
                type="checkbox"
                checked={layers[layer.id]}
                onChange={() => handleLayerToggle(layer.id)}
              />
              <span className="layer-icon">{layer.icon}</span>
              <span className="layer-label">{layer.label}</span>
            </label>
            <p className="layer-description">{layer.description}</p>
          </div>
        ))}
      </div>

      {/* Legend Section */}
      <div className="legend-section">
        <h3>Slope Legend</h3>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#90EE90' }}></div>
          <span>0-20°</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#FFD700' }}></div>
          <span>20-30°</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#FF6347' }}></div>
          <span>&gt;30°</span>
        </div>
      </div>

      <div className="legend-section">
        <h3>Aspect Legend</h3>
        <div className="legend-grid">
          {['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'].map((direction) => (
            <div key={direction} className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#4169E1' }}></div>
              <span>{direction}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LayersPanel;
