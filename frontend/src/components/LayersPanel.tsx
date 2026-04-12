/**
 * LayersPanel component - Right panel for managing layer visibility and transparency.
 * Responsive design with Tailwind CSS.
 * Features:
 * - Checkbox controls for each layer
 * - Transparency slider for each layer
 * - Legend display for active layers
 * - Collapsible on mobile devices
 * - Real-time layer opacity updates
 */

import React, { useState, useEffect } from 'react';
import { useAppStore } from '../store/appStore';

interface LayerItem {
  id: keyof import('../types').LayerVisibility;
  label: string;
  description: string;
  icon: string;
  color?: string;
}

const LAYERS: LayerItem[] = [
  {
    id: 'boundary',
    label: 'Boundary',
    description: 'Community forest boundary',
    icon: '🗺️',
    color: '#FF0000',
  },
  {
    id: 'dem',
    label: 'DEM',
    description: 'Digital Elevation Model',
    icon: '⛰️',
    color: '#8B7355',
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
    color: '#0000FF',
  },
  {
    id: 'samplePlots',
    label: 'Sample Plots',
    description: 'Sample plot locations',
    icon: '📍',
    color: '#00FF00',
  },
];

const LayersPanel: React.FC = () => {
  const layers = useAppStore((state) => state.mapState.layers);
  const setLayerVisibility = useAppStore((state) => state.setLayerVisibility);
  const [transparency, setTransparency] = useState<Record<string, number>>({
    boundary: 1,
    dem: 0.7,
    slope: 0.8,
    aspect: 0.8,
    compartments: 0.6,
    samplePlots: 1,
  });
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleLayerToggle = (layerId: keyof import('../types').LayerVisibility) => {
    setLayerVisibility(layerId, !layers[layerId]);
  };

  const handleTransparencyChange = (layerId: string, value: number) => {
    const numValue = parseFloat(value as any);
    setTransparency((prev) => ({
      ...prev,
      [layerId]: numValue,
    }));

    // Update map layer opacity if map API is available
    if ((window as any).__mapAPI) {
      const mapAPI = (window as any).__mapAPI;
      // This will be extended when actual layer instances are available
      // For now, just store the transparency value
    }
  };

  const activeLayers = LAYERS.filter((layer) => layers[layer.id]);

  return (
    <div className="space-y-4">
      {/* Collapse Button - Mobile only */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="md:hidden w-full flex items-center justify-between p-2 bg-gray-100 rounded hover:bg-gray-200"
      >
        <span className="font-semibold text-gray-800">Layers</span>
        <span className="text-lg">{isCollapsed ? '▼' : '▲'}</span>
      </button>

      {/* Layers List */}
      <div className={`space-y-3 ${isCollapsed ? 'hidden md:block' : ''}`}>
        {LAYERS.map((layer) => (
          <div key={layer.id} className="space-y-2 pb-3 border-b border-gray-200 last:border-b-0">
            {/* Layer Toggle */}
            <label className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors">
              <input
                type="checkbox"
                checked={layers[layer.id]}
                onChange={() => handleLayerToggle(layer.id)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                aria-label={`Toggle ${layer.label} layer`}
              />
              <span className="text-lg">{layer.icon}</span>
              <span className="font-medium text-gray-800 flex-1">{layer.label}</span>
            </label>

            {/* Layer Description */}
            <p className="text-xs text-gray-600 ml-9">{layer.description}</p>

            {/* Transparency Slider - Only show if layer is visible */}
            {layers[layer.id] && (
              <div className="ml-9 space-y-1">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-gray-700">Transparency</label>
                  <span className="text-xs text-gray-600">
                    {Math.round((1 - transparency[layer.id]) * 100)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={transparency[layer.id]}
                  onChange={(e) => handleTransparencyChange(layer.id, parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  aria-label={`Adjust ${layer.label} transparency`}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Active Layers Legend */}
      {activeLayers.length > 0 && (
        <div className={`border-t border-gray-200 pt-4 ${isCollapsed ? 'hidden md:block' : ''}`}>
          <h3 className="font-semibold text-gray-800 mb-3">Active Layers Legend</h3>
          <div className="space-y-2">
            {activeLayers.map((layer) => (
              <div key={layer.id} className="flex items-center gap-2">
                {layer.color ? (
                  <div
                    className="w-4 h-4 rounded border border-gray-300"
                    style={{
                      backgroundColor: layer.color,
                      opacity: transparency[layer.id],
                    }}
                  ></div>
                ) : (
                  <span className="text-lg">{layer.icon}</span>
                )}
                <span className="text-sm text-gray-700">{layer.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Slope Legend */}
      {layers.slope && (
        <div className={`border-t border-gray-200 pt-4 ${isCollapsed ? 'hidden md:block' : ''}`}>
          <h3 className="font-semibold text-gray-800 mb-3">Slope Classification</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{
                  backgroundColor: '#90EE90',
                  opacity: transparency.slope,
                }}
              ></div>
              <span className="text-sm text-gray-700">0-20° (Gentle)</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{
                  backgroundColor: '#FFD700',
                  opacity: transparency.slope,
                }}
              ></div>
              <span className="text-sm text-gray-700">20-30° (Moderate)</span>
            </div>
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{
                  backgroundColor: '#FF6347',
                  opacity: transparency.slope,
                }}
              ></div>
              <span className="text-sm text-gray-700">&gt;30° (Steep)</span>
            </div>
          </div>
        </div>
      )}

      {/* Aspect Legend */}
      {layers.aspect && (
        <div className={`border-t border-gray-200 pt-4 ${isCollapsed ? 'hidden md:block' : ''}`}>
          <h3 className="font-semibold text-gray-800 mb-3">Aspect Directions</h3>
          <div className="grid grid-cols-4 gap-2">
            {['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'].map((direction) => (
              <div key={direction} className="flex flex-col items-center gap-1">
                <div
                  className="w-6 h-6 rounded border border-gray-300"
                  style={{
                    backgroundColor: '#4169E1',
                    opacity: transparency.aspect,
                  }}
                ></div>
                <span className="text-xs text-gray-700 font-medium">{direction}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LayersPanel;
