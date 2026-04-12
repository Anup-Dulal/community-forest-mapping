/**
 * Terrain Tile Loader Utility
 * Handles loading terrain layers (DEM, Slope, Aspect) as Google Maps-style tile layers
 * Replaces GeoJSON-based approach with efficient raster tiles
 */

import L from 'leaflet';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

/**
 * Create a tile layer for terrain data (DEM, Slope, Aspect)
 */
export function createTerrainTileLayer(
  layerType: 'dem' | 'slope' | 'aspect',
  analysisId: string,
  options?: L.TileLayerOptions
): L.TileLayer {
  const tileUrl = `${API_BASE_URL}/api/tiles/${layerType}/${analysisId}/{z}/{x}/{y}.png`;
  
  const defaultOptions: L.TileLayerOptions = {
    attribution: `${layerType.toUpperCase()} Terrain Data`,
    opacity: 0.7,
    maxZoom: 18,
    minZoom: 8,
    tileSize: 256,
    crossOrigin: true,
    // Error handling
    errorTileUrl: '', // Transparent tile on error
  };

  const tileLayer = L.tileLayer(tileUrl, {
    ...defaultOptions,
    ...options,
  });

  console.log(`✓ Created ${layerType} tile layer: ${tileUrl}`);
  
  return tileLayer;
}

/**
 * Fetch terrain layer bounds from backend
 */
export async function getTerrainLayerBounds(
  layerType: 'dem' | 'slope' | 'aspect',
  analysisId: string
): Promise<L.LatLngBounds | null> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/tiles/${layerType}/${analysisId}/bounds`
    );
    
    if (!response.ok) {
      console.warn(`Failed to fetch ${layerType} bounds: ${response.statusText}`);
      return null;
    }

    const data = await response.json();
    
    if (!data.bounds) {
      console.warn(`No bounds data for ${layerType}`);
      return null;
    }

    const { minLat, minLon, maxLat, maxLon } = data.bounds;
    const bounds = L.latLngBounds(
      L.latLng(minLat, minLon),
      L.latLng(maxLat, maxLon)
    );

    console.log(`✓ ${layerType} bounds:`, bounds.toBBoxString());
    
    return bounds;
  } catch (error) {
    console.error(`Error fetching ${layerType} bounds:`, error);
    return null;
  }
}

/**
 * Check if terrain layer is available
 */
export async function isTerrainLayerAvailable(
  layerType: 'dem' | 'slope' | 'aspect',
  analysisId: string
): Promise<boolean> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/tiles/${layerType}/${analysisId}/bounds`,
      { method: 'HEAD' }
    );
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Load all terrain tile layers for an analysis
 */
export async function loadTerrainTileLayers(
  analysisId: string,
  _map: L.Map
): Promise<Map<string, L.TileLayer>> {
  const layers = new Map<string, L.TileLayer>();
  const layerTypes: Array<'dem' | 'slope' | 'aspect'> = ['dem', 'slope', 'aspect'];

  console.log(`Loading terrain tile layers for analysis: ${analysisId}`);

  for (const layerType of layerTypes) {
    try {
      // Check if layer is available
      const available = await isTerrainLayerAvailable(layerType, analysisId);
      
      if (!available) {
        console.warn(`✗ ${layerType} layer not available`);
        continue;
      }

      // Create tile layer
      const tileLayer = createTerrainTileLayer(layerType, analysisId);
      
      // Get bounds (optional - for fitting map view)
      const bounds = await getTerrainLayerBounds(layerType, analysisId);
      if (bounds) {
        // Store bounds on the layer for later use
        (tileLayer as any)._bounds = bounds;
      }

      layers.set(layerType, tileLayer);
      console.log(`✓ ${layerType} tile layer loaded`);
    } catch (error) {
      console.error(`Error loading ${layerType} tile layer:`, error);
    }
  }

  console.log(`Total terrain tile layers loaded: ${layers.size}`);
  
  return layers;
}

/**
 * Update tile layer opacity
 */
export function updateTileLayerOpacity(
  layer: L.TileLayer,
  opacity: number
): void {
  layer.setOpacity(opacity);
}

/**
 * Remove all tile layers from map
 */
export function removeAllTileLayers(
  layers: Map<string, L.TileLayer>,
  map: L.Map
): void {
  layers.forEach((layer) => {
    if (map.hasLayer(layer)) {
      map.removeLayer(layer);
    }
  });
}
