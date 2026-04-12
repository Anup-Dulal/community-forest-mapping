/**
 * MapViewer component - Main map container with Leaflet integration.
 * Displays interactive map with Google Maps basemap, zoom/pan controls,
 * layer toggles, and touch gesture support for mobile.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useAppStore } from '../store/appStore';
import LayerPanel from './LayerPanel';

// Fix Leaflet default icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface BasemapLayer {
  name: string;
  layer: L.Layer;
  visible: boolean;
}

/**
 * MapViewer component - Interactive map with Leaflet.
 * Features:
 * - Google Maps basemap (with fallback to satellite/street)
 * - Zoom, pan, and layer toggle controls
 * - Touch gesture support (pinch-to-zoom, two-finger pan)
 * - Responsive sizing for mobile/tablet/desktop
 * - Boundary display with auto-zoom
 * - Layer rendering and management
 */
const MapViewer: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const basemapLayersRef = useRef<Map<string, BasemapLayer>>(new Map());
  const [isMapReady, setIsMapReady] = useState(false);
  const [availableLayers, setAvailableLayers] = useState<Map<string, L.Layer>>(new Map());
  const [currentBasemap, setCurrentBasemap] = useState<'street' | 'satellite' | 'hybrid'>('street');

  const mapState = useAppStore((state) => state.mapState);
  const setMapCenter = useAppStore((state) => state.setMapCenter);
  const setMapZoom = useAppStore((state) => state.setMapZoom);

  // Initialize map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Create map instance with touch support (NO zoom control, we'll add custom one)
    const map = L.map(mapContainerRef.current, {
      center: mapState.center as L.LatLngExpression,
      zoom: mapState.zoom,
      zoomControl: false, // Disable default zoom control
      attributionControl: true,
      touchZoom: true,
      doubleClickZoom: true,
      scrollWheelZoom: true,
      dragging: true,
    });

    // Add custom zoom control in top-left
    L.control.zoom({ position: 'topleft' }).addTo(map);

    // Add basemap layers
    // Google Maps style (using Leaflet providers)
    const googleStreetLayer = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 2,
        className: 'map-tiles',
      }
    );

    // Satellite layer (Esri World Imagery)
    const satelliteLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: '© Esri',
        maxZoom: 19,
        minZoom: 2,
        className: 'map-tiles',
      }
    );

    // Hybrid layer (Street + Satellite)
    const hybridLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: '© Esri',
        maxZoom: 19,
        minZoom: 2,
        className: 'map-tiles',
      }
    );

    // Add default basemap
    googleStreetLayer.addTo(map);

    // Store basemap layers (separate from data layers)
    basemapLayersRef.current.set('street', { name: 'Street Map', layer: googleStreetLayer, visible: true });
    basemapLayersRef.current.set('satellite', { name: 'Satellite', layer: satelliteLayer, visible: false });
    basemapLayersRef.current.set('hybrid', { name: 'Hybrid', layer: hybridLayer, visible: false });

    // Note: No Leaflet layer control - we'll use our custom LayerPanel for everything

    // Expose basemap layers for switching
    (window as any).__basemapLayers = basemapLayersRef.current;

    // Handle map events
    const handleMoveEnd = () => {
      const center = map.getCenter();
      const zoom = map.getZoom();
      setMapCenter([center.lat, center.lng]);
      setMapZoom(zoom);
    };

    map.on('moveend', handleMoveEnd);
    map.on('zoomend', handleMoveEnd);

    mapRef.current = map;
    setIsMapReady(true);

    // Cleanup
    return () => {
      map.off('moveend', handleMoveEnd);
      map.off('zoomend', handleMoveEnd);
    };
  }, []);

  // Update map center and zoom from store
  useEffect(() => {
    if (!mapRef.current || !isMapReady) return;

    const currentCenter = mapRef.current.getCenter();
    const currentZoom = mapRef.current.getZoom();

    // Only update if values changed significantly
    if (
      Math.abs(currentCenter.lat - mapState.center[0]) > 0.0001 ||
      Math.abs(currentCenter.lng - mapState.center[1]) > 0.0001 ||
      currentZoom !== mapState.zoom
    ) {
      mapRef.current.setView(mapState.center as L.LatLngExpression, mapState.zoom, {
        animate: true,
        duration: 0.5,
      });
    }
  }, [mapState.center, mapState.zoom, isMapReady]);

  // Handle layer visibility changes
  useEffect(() => {
    if (!mapRef.current || !isMapReady) return;

    // Layer visibility is managed through the store
    // This effect can be extended when actual layer data is available
  }, [mapState.layers, isMapReady]);

  // Expose map reference for external layer management
  useEffect(() => {
    if (mapRef.current) {
      (window as any).__mapInstance = mapRef.current;
      (window as any).__mapReady = isMapReady;
    }
  }, [isMapReady]);

  // Public API for adding layers
  const addLayer = useCallback((layer: L.Layer) => {
    if (mapRef.current) {
      mapRef.current.addLayer(layer);
    }
  }, []);

  const removeLayer = useCallback((layer: L.Layer) => {
    if (mapRef.current) {
      mapRef.current.removeLayer(layer);
    }
  }, []);

  const fitBounds = useCallback((bounds: L.LatLngBoundsExpression) => {
    if (mapRef.current) {
      mapRef.current.fitBounds(bounds, { padding: [50, 50], animate: true });
    }
  }, []);

  // Expose public methods
  useEffect(() => {
    if (mapRef.current) {
      (window as any).__mapAPI = {
        addLayer,
        removeLayer,
        fitBounds,
        getMap: () => mapRef.current,
        setLayers: (layers: Map<string, L.Layer>) => {
          // Store data layers and update state
          console.log('setLayers called with:', layers);
          console.log('Layer entries:');
          layers.forEach((layer, name) => {
            console.log(`  - ${name}:`, layer, 'has addTo:', typeof layer?.addTo === 'function');
          });
          setAvailableLayers(new Map(layers));
          console.log('Layers updated in MapViewer:', layers.size);
        },
      };
    }
  }, [addLayer, removeLayer, fitBounds]);

  // Handle basemap change
  const handleBasemapChange = useCallback((basemap: 'street' | 'satellite' | 'hybrid') => {
    if (!mapRef.current) return;

    console.log(`🗺️ Switching basemap to: ${basemap}`);

    // Remove all basemaps
    basemapLayersRef.current.forEach((layer) => {
      if (mapRef.current!.hasLayer(layer.layer)) {
        mapRef.current!.removeLayer(layer.layer);
      }
    });

    // Add selected basemap
    const selectedBasemap = basemapLayersRef.current.get(basemap);
    if (selectedBasemap) {
      selectedBasemap.layer.addTo(mapRef.current);
      setCurrentBasemap(basemap);
      console.log(`  ✅ Basemap switched to ${basemap}`);
    }
  }, []);

  // Handle layer opacity change
  const handleOpacityChange = useCallback((layerName: string, opacity: number) => {
    const layer = availableLayers.get(layerName);
    
    if (!layer) {
      console.warn(`Layer ${layerName} not found for opacity change`);
      return;
    }

    console.log(`🎨 Setting ${layerName} opacity to ${opacity}`);

    // Check if it's a TileLayer
    if (layer instanceof L.TileLayer) {
      layer.setOpacity(opacity);
      console.log(`  ✅ Opacity updated for tile layer ${layerName}`);
      return;
    }

    // Handle GeoJSON layers
    if ('setStyle' in layer && typeof layer.setStyle === 'function') {
      const geoJsonLayer = layer as L.GeoJSON;
      geoJsonLayer.setStyle(() => {
        const currentStyle = (geoJsonLayer.options as any) || {};
        return {
          ...currentStyle,
          opacity: opacity,
          fillOpacity: opacity * (currentStyle.fillOpacity || 0.5),
        };
      });
      console.log(`  ✅ Opacity updated for GeoJSON layer ${layerName}`);
    }
  }, [availableLayers]);

  // Handle layer toggle from LayerPanel
  const handleToggleLayer = useCallback((layerName: string, visible: boolean) => {
    const layer = availableLayers.get(layerName);
    
    if (!layer) {
      console.warn(`Layer ${layerName} not found in availableLayers`);
      return;
    }
    
    if (!mapRef.current) {
      console.warn('Map not ready');
      return;
    }

    console.log(`🔄 Toggle ${layerName}: ${visible ? 'SHOW' : 'HIDE'}`);
    
    try {
      const map = mapRef.current;
      
      if (visible) {
        // Check if layer is already on map
        if (map.hasLayer(layer)) {
          console.log(`  ℹ️ Layer ${layerName} already on map`);
          return;
        }
        
        // Add layer to map
        layer.addTo(map);
        console.log(`  ✅ Layer ${layerName} added to map`);
        
        // Log bounds for debugging
        if ('getBounds' in layer && typeof layer.getBounds === 'function') {
          const geoJsonLayer = layer as L.GeoJSON;
          const bounds = geoJsonLayer.getBounds();
          if (bounds.isValid()) {
            console.log(`  📍 Bounds:`, bounds.toBBoxString());
          }
        }
      } else {
        // Check if layer is on map
        if (!map.hasLayer(layer)) {
          console.log(`  ℹ️ Layer ${layerName} not on map`);
          return;
        }
        
        // Remove layer from map
        map.removeLayer(layer);
        console.log(`  ✅ Layer ${layerName} removed from map`);
      }
    } catch (error) {
      console.error(`❌ Error toggling layer ${layerName}:`, error);
    }
  }, [availableLayers]);

  return (
    <div className="relative w-full h-full bg-gray-100 flex flex-col">
      {/* Map Container */}
      <div
        ref={mapContainerRef}
        className="flex-1 relative overflow-hidden bg-white"
        data-testid="map-container"
      >
        {!isMapReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50 z-50">
            <div className="text-center">
              <div className="text-6xl mb-4">🗺️</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Loading Map</h2>
              <p className="text-gray-600">Initializing Leaflet map...</p>
            </div>
          </div>
        )}
      </div>

      {/* Layer Panel - Only show when layers are available */}
      {isMapReady && availableLayers.size > 0 && (
        <LayerPanel 
          layers={availableLayers} 
          onToggleLayer={handleToggleLayer}
          onOpacityChange={handleOpacityChange}
          onBasemapChange={handleBasemapChange}
          currentBasemap={currentBasemap}
        />
      )}
    </div>
  );
};

export default MapViewer;
