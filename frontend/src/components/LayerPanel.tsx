/**
 * LayerPanel component - Unified layer control with transparency and basemap selection
 */

import React, { useState, useEffect } from 'react';

interface LayerInfo {
  name: string;
  displayName: string;
  color: string;
  visible: boolean;
  available: boolean;
  opacity: number;
}

interface LayerPanelProps {
  layers: Map<string, any>;
  onToggleLayer: (layerName: string, visible: boolean) => void;
  onOpacityChange: (layerName: string, opacity: number) => void;
  onBasemapChange: (basemap: 'street' | 'satellite' | 'hybrid') => void;
  currentBasemap: string;
}

const LayerPanel: React.FC<LayerPanelProps> = ({ 
  layers, 
  onToggleLayer, 
  onOpacityChange,
  onBasemapChange,
  currentBasemap 
}) => {
  const [layerStates, setLayerStates] = useState<Map<string, LayerInfo>>(new Map());
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Define layer metadata (DEM removed per requirements)
  // Compartments should be hidden by default - only show when user clicks checkbox
  const layerMetadata: Record<string, { displayName: string; color: string; defaultVisible: boolean }> = {
    boundary: { displayName: 'Boundary', color: '#dc2626', defaultVisible: true },
    compartment: { displayName: 'Compartments', color: '#2563eb', defaultVisible: false },
    samplePlot: { displayName: 'Sample Plots', color: '#f59e0b', defaultVisible: false },
    slope: { displayName: 'Slope', color: '#6b7280', defaultVisible: false },
    aspect: { displayName: 'Aspect', color: '#8b5cf6', defaultVisible: false },
  };

  // Basemap options
  const basemaps = [
    { id: 'street', name: 'Street Map', icon: '🗺️' },
    { id: 'satellite', name: 'Satellite', icon: '🛰️' },
    { id: 'hybrid', name: 'Hybrid', icon: '🌍' },
  ];

  // Initialize layer states when layers prop changes
  useEffect(() => {
    if (layers.size === 0) return;

    const newLayerStates = new Map<string, LayerInfo>();

    Object.entries(layerMetadata).forEach(([name, meta]) => {
      const available = layers.has(name);
      const defaultVisible = available && meta.defaultVisible;
      
      newLayerStates.set(name, {
        name,
        displayName: meta.displayName,
        color: meta.color,
        visible: defaultVisible,
        available,
        opacity: 1.0,
      });
      
      // Always call onToggleLayer to ensure correct visibility state
      // This will add the layer if defaultVisible is true, or remove it if false
      if (available) {
        onToggleLayer(name, defaultVisible);
      }
    });

    setLayerStates(newLayerStates);
  }, [layers]);

  const handleToggle = (layerName: string) => {
    const layer = layerStates.get(layerName);
    if (!layer?.available) return;

    const newVisible = !layer.visible;
    
    const newStates = new Map(layerStates);
    newStates.set(layerName, { ...layer, visible: newVisible });
    setLayerStates(newStates);

    onToggleLayer(layerName, newVisible);
  };

  const handleOpacityChange = (layerName: string, opacity: number) => {
    const layer = layerStates.get(layerName);
    if (!layer?.available) return;

    const newStates = new Map(layerStates);
    newStates.set(layerName, { ...layer, opacity });
    setLayerStates(newStates);

    onOpacityChange(layerName, opacity);
  };

  if (layerStates.size === 0) return null;

  return (
    <div className="absolute top-4 right-4 bg-white rounded-lg shadow-xl z-[1000] pointer-events-auto max-w-xs w-80">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center gap-2">
          <span className="text-xl">🗺️</span>
          <h3 className="font-semibold text-gray-800">Map Layers</h3>
        </div>
        <button className="text-gray-500 hover:text-gray-700 transition-colors">
          {isCollapsed ? '▼' : '▲'}
        </button>
      </div>

      {!isCollapsed && (
        <>
          {/* Basemap Selection */}
          <div className="p-3 border-b border-gray-200 bg-gray-50">
            <label className="text-xs font-semibold text-gray-700 mb-2 block">
              BASE MAP
            </label>
            <div className="grid grid-cols-3 gap-2">
              {basemaps.map((basemap) => (
                <button
                  key={basemap.id}
                  onClick={() => onBasemapChange(basemap.id as 'street' | 'satellite' | 'hybrid')}
                  className={`p-2 rounded-lg text-xs font-medium transition-all ${
                    currentBasemap === basemap.id
                      ? 'bg-blue-500 text-white shadow-md'
                      : 'bg-white text-gray-700 border border-gray-300 hover:border-blue-300'
                  }`}
                >
                  <div className="text-lg mb-1">{basemap.icon}</div>
                  <div>{basemap.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Data Layers */}
          <div className="p-3 space-y-2 max-h-[600px] overflow-y-auto">
            <label className="text-xs font-semibold text-gray-700 block mb-2">
              DATA LAYERS
            </label>
            {Array.from(layerStates.values()).map((layer) => (
              <div
                key={layer.name}
                className={`rounded-lg border-2 transition-all ${
                  layer.visible 
                    ? 'bg-blue-50 border-blue-300' 
                    : 'bg-gray-50 border-gray-200'
                } ${!layer.available ? 'opacity-50' : ''}`}
              >
                {/* Layer Toggle Row */}
                <div className="flex items-center gap-3 p-3">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={layer.visible}
                    onChange={() => handleToggle(layer.name)}
                    disabled={!layer.available}
                    className="w-5 h-5 rounded cursor-pointer"
                    style={{ accentColor: layer.color }}
                  />

                  {/* Color indicator */}
                  <div
                    className="w-4 h-4 rounded-full border-2"
                    style={{
                      backgroundColor: layer.color,
                      borderColor: layer.color,
                      opacity: layer.opacity,
                    }}
                  />

                  {/* Layer name */}
                  <span className={`flex-1 text-sm ${
                    layer.visible ? 'font-semibold text-gray-900' : 'font-medium text-gray-600'
                  }`}>
                    {layer.displayName}
                  </span>

                  {/* Status badge */}
                  {!layer.available && (
                    <span className="text-xs text-gray-400 bg-gray-200 px-2 py-1 rounded">
                      N/A
                    </span>
                  )}
                </div>

                {/* Opacity Slider - Only show for visible layers */}
                {layer.visible && layer.available && (
                  <div className="px-3 pb-3 pt-0">
                    <div className="flex items-center gap-2">
                      <label className="text-xs text-gray-600 w-20">
                        Opacity: {Math.round(layer.opacity * 100)}%
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={layer.opacity * 100}
                        onChange={(e) => handleOpacityChange(layer.name, parseInt(e.target.value) / 100)}
                        className="flex-1 h-2 rounded-lg appearance-none cursor-pointer"
                        style={{
                          background: `linear-gradient(to right, ${layer.color} 0%, ${layer.color} ${layer.opacity * 100}%, #e5e7eb ${layer.opacity * 100}%, #e5e7eb 100%)`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-gray-200 bg-gray-50 rounded-b-lg">
            <p className="text-xs text-gray-500 text-center">
              Toggle layers and adjust transparency
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default LayerPanel;
