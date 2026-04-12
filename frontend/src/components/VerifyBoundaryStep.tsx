/**
 * VerifyBoundaryStep component - Step 2 of the workflow for verifying uploaded boundary.
 * Displays the uploaded boundary on the map with auto-zoom, area calculation, and success notification.
 * Requirements: 13.1, 13.2, 13.4, 13.5
 */

import React, { useEffect, useState, useRef } from 'react';
import L from 'leaflet';
import { useAppStore } from '../store/appStore';
import '../styles/VerifyBoundaryStep.css';

interface VerifyBoundaryStepProps {
  shapefileId: string;
  onComplete: () => void;
}

interface BoundaryData {
  geometry: GeoJSON.Feature;
  area: number;
  boundingBox: {
    minLat: number;
    maxLat: number;
    minLon: number;
    maxLon: number;
  };
}

/**
 * VerifyBoundaryStep component - Display and verify uploaded boundary.
 * Features:
 * - Display boundary on map within 2 seconds
 * - Auto-zoom and center map to fit boundary
 * - Calculate and display boundary area in square kilometers
 * - Show success notification
 * - Layer toggle for satellite imagery and elevation
 */
const VerifyBoundaryStep: React.FC<VerifyBoundaryStepProps> = ({ shapefileId, onComplete }) => {
  const [boundaryData, setBoundaryData] = useState<BoundaryData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const boundaryLayerRef = useRef<L.Layer | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  const setMapCenter = useAppStore((state) => state.setMapCenter);
  const setMapZoom = useAppStore((state) => state.setMapZoom);
  const setLayerVisibility = useAppStore((state) => state.setLayerVisibility);

  // Fetch boundary geometry from backend
  useEffect(() => {
    const fetchBoundary = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await fetch(`/api/shapefile/${shapefileId}/boundary`);
        if (!response.ok) {
          throw new Error('Failed to fetch boundary geometry');
        }

        const data = await response.json();
        setBoundaryData(data);
        setShowSuccess(true);

        // Auto-dismiss success notification after 3 seconds
        setTimeout(() => setShowSuccess(false), 3000);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load boundary';
        setError(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBoundary();
  }, [shapefileId]);

  // Display boundary on map
  useEffect(() => {
    if (!boundaryData || !mapInstanceRef.current) return;

    try {
      // Remove previous boundary layer if exists
      if (boundaryLayerRef.current) {
        mapInstanceRef.current.removeLayer(boundaryLayerRef.current);
      }

      // Create GeoJSON layer for boundary
      const geoJsonLayer = L.geoJSON(boundaryData.geometry, {
        style: {
          color: '#2563eb',
          weight: 3,
          opacity: 0.8,
          fillColor: '#3b82f6',
          fillOpacity: 0.2,
        },
        onEachFeature: (feature, layer) => {
          layer.bindPopup(`
            <div class="boundary-popup">
              <h3>Community Forest Boundary</h3>
              <p><strong>Area:</strong> ${boundaryData.area.toFixed(2)} km²</p>
            </div>
          `);
        },
      });

      geoJsonLayer.addTo(mapInstanceRef.current);
      boundaryLayerRef.current = geoJsonLayer;

      // Auto-zoom and center to fit boundary
      const bounds = geoJsonLayer.getBounds();
      if (bounds.isValid()) {
        mapInstanceRef.current.fitBounds(bounds, {
          padding: [50, 50],
          animate: true,
          duration: 0.5,
        });

        // Update store with new center and zoom
        const center = mapInstanceRef.current.getCenter();
        const zoom = mapInstanceRef.current.getZoom();
        setMapCenter([center.lat, center.lng]);
        setMapZoom(zoom);
      }

      // Enable boundary layer visibility
      setLayerVisibility('boundary', true);
    } catch (err) {
      console.error('Error displaying boundary:', err);
      setError('Failed to display boundary on map');
    }
  }, [boundaryData, setMapCenter, setMapZoom, setLayerVisibility]);

  // Get map instance from window
  useEffect(() => {
    const checkMapReady = () => {
      const mapAPI = (window as any).__mapAPI;
      const mapInstance = (window as any).__mapInstance;
      const mapReady = (window as any).__mapReady;

      if (mapInstance && mapReady && mapAPI) {
        mapInstanceRef.current = mapInstance;
      } else {
        // Retry after a short delay
        setTimeout(checkMapReady, 100);
      }
    };

    checkMapReady();
  }, []);

  const handleProceed = () => {
    onComplete();
  };

  return (
    <div className="verify-boundary-step">
      <div className="step-header">
        <h2>Step 2: Verify Boundary</h2>
        <p className="step-description">
          Your boundary has been uploaded and is displayed on the map below. Verify that the correct
          area has been selected before proceeding to the next step.
        </p>
      </div>

      {/* Success Notification */}
      {showSuccess && (
        <div className="success-notification" role="status">
          <span className="success-icon">✓</span>
          <span className="success-message">Boundary loaded successfully</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-notification" role="alert">
          <span className="error-icon">❌</span>
          <span className="error-message">{error}</span>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading boundary geometry...</p>
        </div>
      )}

      {/* Boundary Information */}
      {boundaryData && !isLoading && (
        <div className="boundary-info">
          <div className="info-card">
            <h3>Boundary Statistics</h3>
            <div className="info-grid">
              <div className="info-item">
                <label>Area</label>
                <span className="info-value">{boundaryData.area.toFixed(2)} km²</span>
              </div>
              <div className="info-item">
                <label>Bounding Box</label>
                <span className="info-value">
                  {boundaryData.boundingBox.minLat.toFixed(4)}° to{' '}
                  {boundaryData.boundingBox.maxLat.toFixed(4)}°N,{' '}
                  {boundaryData.boundingBox.minLon.toFixed(4)}° to{' '}
                  {boundaryData.boundingBox.maxLon.toFixed(4)}°E
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="verify-actions">
        <button
          className="button secondary"
          onClick={() => window.location.reload()}
          disabled={isLoading}
        >
          Re-upload
        </button>
        <button
          className="button primary"
          onClick={handleProceed}
          disabled={isLoading || !boundaryData || !!error}
        >
          Proceed to Next Step
        </button>
      </div>
    </div>
  );
};

export default VerifyBoundaryStep;
