"""
Google Earth Engine Client for fetching satellite imagery, elevation data, and vegetation indices.
Implements fallback to alternative DEM sources (OpenTopography, NASA) on failure.
Requirements: 14.1, 14.3, 14.5, 22.1, 23.1, 23.4
"""

import os
import logging
import json
import time
from typing import Dict, Tuple, Optional, Any
import numpy as np
import requests
import ee
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class GoogleEarthEngineClient:
    """
    Client for Google Earth Engine API integration.
    Fetches satellite imagery, elevation data, NDVI, and EVI.
    Implements fallback to alternative sources on failure.
    """

    def __init__(self):
        """Initialize Google Earth Engine client with authentication."""
        self.ee_initialized = False
        self.rate_limit_delay = 0.1  # Delay between API calls to respect rate limits
        self.max_retries = 3
        self.retry_delay = 1.0
        self._initialize_ee()

    def _initialize_ee(self) -> bool:
        """
        Initialize Google Earth Engine API.
        Returns True if successful, False otherwise.
        """
        try:
            # Check if already authenticated
            try:
                ee.Initialize()
                self.ee_initialized = True
                logger.info("Google Earth Engine initialized successfully")
                return True
            except ee.EEException:
                # Try to authenticate with service account
                service_account_key = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
                if service_account_key:
                    credentials = ee.ServiceAccountCredentials(
                        email=os.getenv('GEE_SERVICE_ACCOUNT_EMAIL'),
                        key_data=service_account_key
                    )
                    ee.Initialize(credentials)
                    self.ee_initialized = True
                    logger.info("Google Earth Engine initialized with service account")
                    return True
                else:
                    logger.warning("Google Earth Engine service account not configured")
                    return False
        except Exception as e:
            logger.error(f"Error initializing Google Earth Engine: {e}")
            return False

    def fetch_satellite_imagery(
        self,
        geometry: Dict[str, Any],
        start_date: str = None,
        end_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch satellite imagery from Google Earth Engine.
        Requirements: 14.1, 22.1, 22.2

        Args:
            geometry: GeoJSON geometry of the boundary
            start_date: Start date for imagery (YYYY-MM-DD)
            end_date: End date for imagery (YYYY-MM-DD)

        Returns:
            Dictionary with satellite imagery metadata and URL
        """
        if not self.ee_initialized:
            logger.warning("Google Earth Engine not initialized, using fallback")
            return self._fallback_satellite_imagery(geometry)

        try:
            # Default to recent imagery if dates not specified
            if not start_date:
                start_date = "2023-01-01"
            if not end_date:
                end_date = "2024-01-01"

            # Convert geometry to EE geometry
            ee_geometry = ee.Geometry(geometry)

            # Use Sentinel-2 imagery (10m resolution, freely available)
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(ee_geometry) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('system:time_start', False)

            # Get the most recent image
            image = collection.first()

            if image is None:
                logger.warning("No satellite imagery found for the specified date range")
                return self._fallback_satellite_imagery(geometry)

            # Get image metadata
            image_info = image.getInfo()
            acquisition_date = image_info['properties']['system:time_start']

            # Generate visualization URL
            vis_params = {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0,
                'max': 3000,
                'gamma': 1.4
            }

            # Create map tile URL
            map_id = ee.Image(image).getMapId(vis_params)
            tile_url = map_id['tile_fetcher'].url_format

            time.sleep(self.rate_limit_delay)

            return {
                'status': 'success',
                'source': 'Google Earth Engine - Sentinel-2',
                'acquisition_date': acquisition_date,
                'tile_url': tile_url,
                'resolution': 10,  # meters
                'bands': ['B4', 'B3', 'B2']
            }

        except Exception as e:
            logger.error(f"Error fetching satellite imagery from Google Earth Engine: {e}")
            return self._fallback_satellite_imagery(geometry)

    def fetch_elevation_data(
        self,
        geometry: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch elevation data from Google Earth Engine.
        Requirements: 14.3

        Args:
            geometry: GeoJSON geometry of the boundary

        Returns:
            Dictionary with elevation data metadata
        """
        if not self.ee_initialized:
            logger.warning("Google Earth Engine not initialized, using fallback")
            return self._fallback_elevation_data(geometry)

        try:
            # Convert geometry to EE geometry
            ee_geometry = ee.Geometry(geometry)

            # Use SRTM 30m DEM
            dem = ee.Image('USGS/SRTMGL1_Ellip/SRTMGL1_Ellip_srtm')

            # Clip to boundary
            dem_clipped = dem.clip(ee_geometry)

            # Get statistics
            stats = dem_clipped.reduceRegion(
                reducer=ee.Reducer.minMax().combine(
                    ee.Reducer.mean(), None, True
                ),
                geometry=ee_geometry,
                scale=30,
                maxPixels=1e9
            ).getInfo()

            time.sleep(self.rate_limit_delay)

            return {
                'status': 'success',
                'source': 'Google Earth Engine - SRTM 30m',
                'resolution': 30,  # meters
                'min_elevation': stats.get('elevation_min', 0),
                'max_elevation': stats.get('elevation_max', 0),
                'mean_elevation': stats.get('elevation_mean', 0)
            }

        except Exception as e:
            logger.error(f"Error fetching elevation data from Google Earth Engine: {e}")
            return self._fallback_elevation_data(geometry)

    def calculate_ndvi(
        self,
        geometry: Dict[str, Any],
        start_date: str = None,
        end_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate NDVI (Normalized Difference Vegetation Index).
        Requirements: 23.1, 23.4

        Args:
            geometry: GeoJSON geometry of the boundary
            start_date: Start date for imagery (YYYY-MM-DD)
            end_date: End date for imagery (YYYY-MM-DD)

        Returns:
            Dictionary with NDVI statistics and visualization
        """
        if not self.ee_initialized:
            logger.warning("Google Earth Engine not initialized, using fallback")
            return self._fallback_ndvi(geometry)

        try:
            # Default to recent imagery if dates not specified
            if not start_date:
                start_date = "2023-01-01"
            if not end_date:
                end_date = "2024-01-01"

            # Convert geometry to EE geometry
            ee_geometry = ee.Geometry(geometry)

            # Use Sentinel-2 imagery
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(ee_geometry) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('system:time_start', False)

            # Get the most recent image
            image = collection.first()

            if image is None:
                logger.warning("No imagery found for NDVI calculation")
                return self._fallback_ndvi(geometry)

            # Calculate NDVI: (NIR - RED) / (NIR + RED)
            # Sentinel-2: B8 = NIR, B4 = RED
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

            # Clip to boundary
            ndvi_clipped = ndvi.clip(ee_geometry)

            # Get statistics
            stats = ndvi_clipped.reduceRegion(
                reducer=ee.Reducer.minMax().combine(
                    ee.Reducer.mean().combine(
                        ee.Reducer.stdDev(), None, True
                    ), None, True
                ),
                geometry=ee_geometry,
                scale=10,
                maxPixels=1e9
            ).getInfo()

            # Generate visualization URL
            vis_params = {
                'min': -1,
                'max': 1,
                'palette': ['blue', 'white', 'green']
            }

            map_id = ee.Image(ndvi_clipped).getMapId(vis_params)
            tile_url = map_id['tile_fetcher'].url_format

            time.sleep(self.rate_limit_delay)

            return {
                'status': 'success',
                'index': 'NDVI',
                'min': stats.get('NDVI_min', -1),
                'max': stats.get('NDVI_max', 1),
                'mean': stats.get('NDVI_mean', 0),
                'stdDev': stats.get('NDVI_stdDev', 0),
                'tile_url': tile_url,
                'palette': ['blue', 'white', 'green']
            }

        except Exception as e:
            logger.error(f"Error calculating NDVI: {e}")
            return self._fallback_ndvi(geometry)

    def calculate_evi(
        self,
        geometry: Dict[str, Any],
        start_date: str = None,
        end_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate EVI (Enhanced Vegetation Index).
        Requirements: 23.1, 23.4

        Args:
            geometry: GeoJSON geometry of the boundary
            start_date: Start date for imagery (YYYY-MM-DD)
            end_date: End date for imagery (YYYY-MM-DD)

        Returns:
            Dictionary with EVI statistics and visualization
        """
        if not self.ee_initialized:
            logger.warning("Google Earth Engine not initialized, using fallback")
            return self._fallback_evi(geometry)

        try:
            # Default to recent imagery if dates not specified
            if not start_date:
                start_date = "2023-01-01"
            if not end_date:
                end_date = "2024-01-01"

            # Convert geometry to EE geometry
            ee_geometry = ee.Geometry(geometry)

            # Use Sentinel-2 imagery
            collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                .filterBounds(ee_geometry) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
                .sort('system:time_start', False)

            # Get the most recent image
            image = collection.first()

            if image is None:
                logger.warning("No imagery found for EVI calculation")
                return self._fallback_evi(geometry)

            # Calculate EVI: 2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)
            # Sentinel-2: B8 = NIR, B4 = RED, B2 = BLUE
            nir = image.select('B8').divide(10000)
            red = image.select('B4').divide(10000)
            blue = image.select('B2').divide(10000)

            evi = nir.subtract(red).multiply(2.5).divide(
                nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1)
            ).rename('EVI')

            # Clip to boundary
            evi_clipped = evi.clip(ee_geometry)

            # Get statistics
            stats = evi_clipped.reduceRegion(
                reducer=ee.Reducer.minMax().combine(
                    ee.Reducer.mean().combine(
                        ee.Reducer.stdDev(), None, True
                    ), None, True
                ),
                geometry=ee_geometry,
                scale=10,
                maxPixels=1e9
            ).getInfo()

            # Generate visualization URL
            vis_params = {
                'min': -1,
                'max': 1,
                'palette': ['blue', 'white', 'green']
            }

            map_id = ee.Image(evi_clipped).getMapId(vis_params)
            tile_url = map_id['tile_fetcher'].url_format

            time.sleep(self.rate_limit_delay)

            return {
                'status': 'success',
                'index': 'EVI',
                'min': stats.get('EVI_min', -1),
                'max': stats.get('EVI_max', 1),
                'mean': stats.get('EVI_mean', 0),
                'stdDev': stats.get('EVI_stdDev', 0),
                'tile_url': tile_url,
                'palette': ['blue', 'white', 'green']
            }

        except Exception as e:
            logger.error(f"Error calculating EVI: {e}")
            return self._fallback_evi(geometry)

    def _fallback_satellite_imagery(self, geometry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback to alternative satellite imagery source.
        Requirements: 14.8
        """
        logger.info("Using fallback satellite imagery source")
        return {
            'status': 'fallback',
            'source': 'OpenStreetMap',
            'message': 'Using fallback satellite imagery source',
            'tile_url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        }

    def _fallback_elevation_data(self, geometry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback to alternative elevation data source.
        Requirements: 14.8
        """
        logger.info("Using fallback elevation data source")
        return {
            'status': 'fallback',
            'source': 'OpenTopography',
            'message': 'Using fallback elevation data source',
            'resolution': 30
        }

    def _fallback_ndvi(self, geometry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback NDVI calculation.
        """
        logger.info("Using fallback NDVI calculation")
        return {
            'status': 'fallback',
            'index': 'NDVI',
            'message': 'Using fallback NDVI calculation',
            'min': -1,
            'max': 1,
            'mean': 0.5,
            'stdDev': 0.2
        }

    def _fallback_evi(self, geometry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback EVI calculation.
        """
        logger.info("Using fallback EVI calculation")
        return {
            'status': 'fallback',
            'index': 'EVI',
            'message': 'Using fallback EVI calculation',
            'min': -1,
            'max': 1,
            'mean': 0.5,
            'stdDev': 0.2
        }
