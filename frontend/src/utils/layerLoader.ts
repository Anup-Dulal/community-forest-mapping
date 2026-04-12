/**
 * Layer Loader Utility
 * Handles loading and rendering GeoJSON layers on the Leaflet map
 * Terrain layers (DEM, Slope, Aspect) are loaded as tile layers
 */

import L from 'leaflet';
import { loadTerrainTileLayers } from './terrainTileLoader';

interface LayerStyle {
  color?: string;
  weight?: number;
  opacity?: number;
  fillColor?: string;
  fillOpacity?: number;
}

const DEFAULT_STYLES = {
  boundary: {
    color: '#dc2626', // Red for boundary
    weight: 3,
    opacity: 1,
    fillColor: 'transparent',
    fillOpacity: 0,
  },
  compartment: {
    color: '#2563eb', // Blue for parent compartments
    weight: 2,
    opacity: 1,
    fillColor: '#3b82f6',
    fillOpacity: 0.2,
  },
  subCompartment: {
    color: '#10b981', // Green for sub-compartments
    weight: 2,
    opacity: 1,
    fillColor: '#34d399',
    fillOpacity: 0.3,
  },
  samplePlot: {
    color: '#f59e0b', // Orange for sample plots
    weight: 2,
    opacity: 1,
    fillColor: '#fbbf24',
    fillOpacity: 0.8,
  },
  dem: {
    color: '#8B7355', // Brown for DEM
    weight: 1,
    opacity: 0.7,
    fillColor: '#A0826D',
    fillOpacity: 0.4,
  },
  slope: {
    color: '#6b7280', // Gray for slope
    weight: 1,
    opacity: 0.7,
    fillColor: '#9ca3af',
    fillOpacity: 0.3,
  },
  aspect: {
    color: '#8b5cf6', // Purple for aspect
    weight: 1,
    opacity: 0.7,
    fillColor: '#a78bfa',
    fillOpacity: 0.3,
  },
};

/**
 * Load boundary layer from shapefile
 */
export async function loadBoundaryLayer(
  shapefileId: string,
  map: L.Map
): Promise<L.GeoJSON | null> {
  try {
    console.log(`Fetching boundary from: /api/shapefile/${shapefileId}/boundary`);
    const response = await fetch(`/api/shapefile/${shapefileId}/boundary`);
    
    if (!response.ok) {
      console.error(`Failed to load boundary: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error('Error response:', errorText);
      return null;
    }

    const boundaryData = await response.json();
    console.log('Boundary data received:', boundaryData);

    if (!boundaryData || !boundaryData.geometry) {
      console.warn('No boundary geometry found in response');
      return null;
    }

    // Convert to GeoJSON FeatureCollection format
    const geojsonData: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: boundaryData.geometry.geometry || boundaryData.geometry,
        properties: {
          area: boundaryData.area,
          areaHectares: boundaryData.areaHectares,
        }
      }]
    };

    console.log('Creating boundary layer with style:', DEFAULT_STYLES.boundary);
    const style = DEFAULT_STYLES.boundary;
    const geoJsonLayer = L.geoJSON(geojsonData, {
      style: () => style,
      onEachFeature: (feature, layer) => {
        if (feature.properties) {
          const props = feature.properties;
          let popupContent = `<div class="text-sm"><strong>Boundary</strong><br/>`;
          popupContent += `Area: ${props.areaHectares?.toFixed(2) || 'N/A'} hectares<br/>`;
          popupContent += '</div>';
          
          try {
            layer.bindPopup(popupContent);
          } catch (error) {
            console.warn('Error binding popup for boundary:', error);
          }
        }
      },
    });

    // DON'T add to map yet - let LayerPanel control visibility
    // geoJsonLayer.addTo(map);
    console.log('Boundary layer created (not added to map yet)');

    const bounds = geoJsonLayer.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50], animate: true });
      console.log('Map fitted to boundary bounds');
    } else {
      console.warn('Boundary bounds are invalid');
    }

    console.log('✓ Boundary layer loaded successfully');
    return geoJsonLayer;
  } catch (error) {
    console.error('Error loading boundary layer:', error);
    return null;
  }
}

/**
 * Load GeoJSON layer from backend
 */
export async function loadGeoJSONLayer(
  layerType: 'compartment' | 'samplePlot',
  analysisId: string,
  _map: L.Map
): Promise<L.GeoJSON | null> {
  try {
    console.log(`Fetching ${layerType} from: /api/geojson/${layerType}?analysisId=${analysisId}`);
    
    // Fetch GeoJSON from backend
    const response = await fetch(`/api/geojson/${layerType}?analysisId=${analysisId}`);
    
    if (!response.ok) {
      console.warn(`Failed to load ${layerType} GeoJSON: ${response.statusText}`);
      return null;
    }

    const geojsonData = await response.json();

    if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
      console.warn(`No features found for ${layerType} - creating empty layer`);
      // Return empty GeoJSON layer so UI shows it as available but empty
      const emptyData: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: []
      };
      const emptyLayer = L.geoJSON(emptyData);
      console.log(`✓ ${layerType} layer created (empty - awaiting data)`);
      return emptyLayer;
    }

    console.log(`${layerType} data received with ${geojsonData.features.length} features`);

    // Create GeoJSON layer with styling
    const geoJsonLayer = L.geoJSON(geojsonData, {
      style: (feature) => {
        // For compartments, use different styles for parent vs sub-compartments
        if (layerType === 'compartment' && feature?.properties) {
          const level = feature.properties.level;
          if (level === 0) {
            // Parent compartment - blue
            return DEFAULT_STYLES.compartment;
          } else if (level === 1) {
            // Sub-compartment - green
            return DEFAULT_STYLES.subCompartment;
          }
        }
        // Default style
        return DEFAULT_STYLES[layerType];
      },
      pointToLayer: (_feature, latlng) => {
        // For point features (sample plots), create circle markers with custom style
        const style = DEFAULT_STYLES[layerType];
        return L.circleMarker(latlng, {
          radius: 6,
          fillColor: style.fillColor || style.color,
          color: style.color,
          weight: style.weight || 2,
          opacity: style.opacity || 1,
          fillOpacity: style.fillOpacity || 0.8,
        });
      },
      onEachFeature: (feature, layer) => {
        // Add popup with feature properties
        if (feature.properties) {
          const props = feature.properties;
          let popupContent = '<div class="text-sm">';
          
          // Add label as title
          if (props.label) {
            popupContent += `<strong>${props.label}</strong><br/>`;
          } else {
            popupContent += `<strong>${layerType}</strong><br/>`;
          }
          
          // Add area if available
          if (props.area !== null && props.area !== undefined) {
            popupContent += `Area: ${Number(props.area).toFixed(2)} hectares<br/>`;
          }
          
          // Add level info for compartments
          if (layerType === 'compartment' && props.level !== undefined) {
            const levelName = props.level === 0 ? 'Parent Compartment' : 'Sub-Compartment';
            popupContent += `Type: ${levelName}<br/>`;
          }
          
          // Add other properties
          Object.entries(props).forEach(([key, value]) => {
            if (key !== 'label' && key !== 'area' && key !== 'level' && 
                key && value !== null && value !== undefined) {
              popupContent += `${key}: ${value}<br/>`;
            }
          });
          
          popupContent += '</div>';
          
          try {
            layer.bindPopup(popupContent);
            
            // Add permanent label for compartments
            if (layerType === 'compartment' && props.label) {
              const label = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'compartment-label',
              }).setContent(props.label);
              
              (layer as any).bindTooltip(label);
            }
          } catch (error) {
            console.warn(`Error binding popup/label for ${layerType}:`, error);
          }
        }
      },
    });

    // DON'T add to map yet - let LayerPanel control visibility
    // geoJsonLayer.addTo(map);
    console.log(`${layerType} layer created (not added to map yet)`);

    console.log(`✓ ${layerType} layer loaded successfully with ${geojsonData.features.length} features`);
    return geoJsonLayer;
  } catch (error) {
    console.error(`Error loading ${layerType} layer:`, error);
    return null;
  }
}

/**
 * Load all analysis layers including boundary, compartments, sample plots, and terrain tiles
 */
export async function loadAllLayers(
  analysisId: string,
  shapefileId: string,
  _map: L.Map
): Promise<Map<string, L.GeoJSON | L.TileLayer>> {
  const layers = new Map<string, L.GeoJSON | L.TileLayer>();

  console.log(`Loading layers - analysisId: ${analysisId}, shapefileId: ${shapefileId}`);

  // Load boundary first (red outline)
  try {
    console.log('Loading boundary layer...');
    const boundaryLayer = await loadBoundaryLayer(shapefileId, _map);
    if (boundaryLayer) {
      layers.set('boundary', boundaryLayer);
      console.log('✓ Boundary layer loaded');
    } else {
      console.warn('✗ Boundary layer failed to load');
    }
  } catch (error) {
    console.error('Error loading boundary layer:', error);
  }

  // Load vector layers (compartments, sample plots)
  const vectorLayerTypes: Array<'compartment' | 'samplePlot'> = [
    'compartment',
    'samplePlot',
  ];

  for (const layerType of vectorLayerTypes) {
    try {
      console.log(`Loading ${layerType} layer...`);
      const layer = await loadGeoJSONLayer(layerType, analysisId, _map);
      if (layer) {
        layers.set(layerType, layer);
        console.log(`✓ ${layerType} layer loaded`);
      } else {
        console.warn(`✗ ${layerType} layer failed to load`);
      }
    } catch (error) {
      console.error(`Error loading ${layerType} layer:`, error);
    }
  }

  // Load terrain tile layers (Slope, Aspect only - no DEM per requirements)
  try {
    console.log('Loading terrain tile layers (Slope, Aspect)...');
    const terrainLayers = await loadTerrainTileLayers(analysisId, _map);
    // Filter out DEM layer - requirements state "must not generate or display a DEM map"
    terrainLayers.forEach((layer, name) => {
      if (name !== 'dem') {
        layers.set(name, layer);
      }
    });
    console.log(`✓ Loaded ${terrainLayers.size - 1} terrain tile layers (excluding DEM)`);
  } catch (error) {
    console.error('Error loading terrain tile layers:', error);
  }

  console.log(`Total layers loaded: ${layers.size}`);

  // Update the map's layer panel using setLayers
  if ((window as any).__mapAPI?.setLayers) {
    (window as any).__mapAPI.setLayers(layers);
    console.log('Layers synced with MapViewer');
  } else {
    console.warn('MapAPI.setLayers not available');
  }

  return layers;
}

/**
 * Toggle layer visibility
 */
export function toggleLayerVisibility(
  layer: L.GeoJSON,
  map: L.Map,
  visible: boolean
): void {
  if (visible) {
    map.addLayer(layer);
  } else {
    map.removeLayer(layer);
  }
}

/**
 * Remove all layers from map
 */
export function removeAllLayers(layers: Map<string, L.GeoJSON | L.TileLayer>, map: L.Map): void {
  layers.forEach((layer) => {
    if (map.hasLayer(layer)) {
      map.removeLayer(layer);
    }
  });
  layers.clear();
}

/**
 * Update layer style
 */
export function updateLayerStyle(
  layer: L.GeoJSON,
  style: LayerStyle
): void {
  layer.setStyle(style);
}
