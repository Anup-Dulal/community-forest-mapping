/**
 * Map Layer Manager - Utilities for managing Leaflet layers
 * Handles boundary display, layer rendering, and layer management
 */

import L from 'leaflet';

export interface BoundaryData {
  geometry: GeoJSON.Feature;
  area?: number;
  name?: string;
}

export interface LayerRenderOptions {
  color?: string;
  fillColor?: string;
  fillOpacity?: number;
  weight?: number;
  opacity?: number;
  dashArray?: string;
}

/**
 * Add boundary layer to map with auto-zoom
 */
export const addBoundaryLayer = (
  map: L.Map,
  boundaryData: BoundaryData,
  options?: LayerRenderOptions
): L.GeoJSON => {
  const defaultOptions: LayerRenderOptions = {
    color: '#FF0000',
    fillColor: '#FF0000',
    fillOpacity: 0.1,
    weight: 3,
    opacity: 1,
    ...options,
  };

  const geoJsonLayer = L.geoJSON(boundaryData.geometry, {
    style: {
      color: defaultOptions.color,
      fillColor: defaultOptions.fillColor,
      fillOpacity: defaultOptions.fillOpacity,
      weight: defaultOptions.weight,
      opacity: defaultOptions.opacity,
      dashArray: defaultOptions.dashArray,
    },
  });

  geoJsonLayer.addTo(map);

  // Auto-zoom to fit boundary
  const bounds = geoJsonLayer.getBounds();
  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [50, 50], animate: true });
  }

  return geoJsonLayer;
};

/**
 * Add raster layer to map (for DEM, slope, aspect, etc.)
 */
export const addRasterLayer = (
  map: L.Map,
  imageUrl: string,
  bounds: L.LatLngBoundsExpression,
  opacity: number = 0.7,
  name?: string
): L.ImageOverlay => {
  const imageOverlay = L.imageOverlay(imageUrl, bounds, {
    opacity,
    className: `raster-layer ${name || 'unnamed'}`,
  });

  imageOverlay.addTo(map);
  return imageOverlay;
};

/**
 * Add marker layer to map (for sample plots, etc.)
 */
export const addMarkerLayer = (
  map: L.Map,
  points: Array<{ lat: number; lng: number; label?: string; color?: string }>,
  options?: { radius?: number; color?: string }
): L.FeatureGroup => {
  const featureGroup = L.featureGroup();

  points.forEach((point) => {
    const marker = L.circleMarker([point.lat, point.lng], {
      radius: options?.radius || 5,
      fillColor: point.color || options?.color || '#00FF00',
      color: '#000',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8,
    });

    if (point.label) {
      marker.bindPopup(point.label);
    }

    featureGroup.addLayer(marker);
  });

  featureGroup.addTo(map);
  return featureGroup;
};

/**
 * Add polygon layer to map (for compartments, etc.)
 */
export const addPolygonLayer = (
  map: L.Map,
  features: GeoJSON.FeatureCollection,
  options?: LayerRenderOptions
): L.GeoJSON => {
  const defaultOptions: LayerRenderOptions = {
    color: '#0000FF',
    fillColor: '#0000FF',
    fillOpacity: 0.2,
    weight: 2,
    opacity: 0.8,
    ...options,
  };

  const geoJsonLayer = L.geoJSON(features, {
    style: {
      color: defaultOptions.color,
      fillColor: defaultOptions.fillColor,
      fillOpacity: defaultOptions.fillOpacity,
      weight: defaultOptions.weight,
      opacity: defaultOptions.opacity,
      dashArray: defaultOptions.dashArray,
    },
    onEachFeature: (feature, layer) => {
      if (feature.properties) {
        const popupContent = Object.entries(feature.properties)
          .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
          .join('<br>');
        layer.bindPopup(popupContent);
      }
    },
  });

  geoJsonLayer.addTo(map);
  return geoJsonLayer;
};

/**
 * Remove layer from map
 */
export const removeLayer = (map: L.Map, layer: L.Layer): void => {
  map.removeLayer(layer);
};

/**
 * Update layer opacity
 */
export const updateLayerOpacity = (layer: L.Layer, opacity: number): void => {
  if (layer instanceof L.ImageOverlay) {
    layer.setOpacity(opacity);
  } else if (layer instanceof L.GeoJSON) {
    layer.setStyle({ fillOpacity: opacity });
  }
};

/**
 * Get map bounds as GeoJSON bbox
 */
export const getMapBounds = (map: L.Map): [number, number, number, number] => {
  const bounds = map.getBounds();
  return [bounds.getWest(), bounds.getSouth(), bounds.getEast(), bounds.getNorth()];
};

/**
 * Fit map to bounds
 */
export const fitMapToBounds = (
  map: L.Map,
  bounds: L.LatLngBoundsExpression,
  padding: number = 50
): void => {
  map.fitBounds(bounds, { padding: [padding, padding], animate: true });
};
