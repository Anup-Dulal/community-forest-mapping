"""
Coordinate Converter for transforming between coordinate systems.
Supports lat/lon (EPSG:4326) and UTM/UPS conversions.
"""

import logging
from typing import Dict, Tuple
import pyproj
from pyproj import Transformer, CRS

logger = logging.getLogger(__name__)


class CoordinateConverter:
    """Converts coordinates between lat/lon and UTM/UPS coordinate systems."""

    # Standard UTM/UPS zones
    WGS84_CRS = CRS.from_epsg(4326)  # lat/lon

    def __init__(self):
        """Initialize the coordinate converter."""
        pass

    def lat_lon_to_utm(self, latitude: float, longitude: float) -> Dict:
        """
        Convert latitude/longitude to UTM coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary with UTM zone, easting, northing, and CRS info
            
        Raises:
            ValueError: If coordinates are invalid
        """
        try:
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                raise ValueError(f"Invalid latitude: {latitude}")
            if not (-180 <= longitude <= 180):
                raise ValueError(f"Invalid longitude: {longitude}")
            
            # Determine UTM zone
            utm_zone = self._calculate_utm_zone(longitude, latitude)
            
            # Get UTM CRS
            utm_crs = CRS.from_epsg(self._get_utm_epsg(utm_zone, latitude))
            
            # Create transformer
            transformer = Transformer.from_crs(self.WGS84_CRS, utm_crs, always_xy=True)
            
            # Transform coordinates
            easting, northing = transformer.transform(longitude, latitude)
            
            return {
                'easting': round(easting, 2),
                'northing': round(northing, 2),
                'utm_zone': utm_zone,
                'crs': f'EPSG:{self._get_utm_epsg(utm_zone, latitude)}',
                'latitude': latitude,
                'longitude': longitude
            }
            
        except Exception as e:
            logger.error(f"Error converting lat/lon to UTM: {str(e)}")
            raise ValueError(f"Failed to convert coordinates: {str(e)}")

    def utm_to_lat_lon(
        self,
        easting: float,
        northing: float,
        utm_zone: int,
        is_southern: bool = False
    ) -> Dict:
        """
        Convert UTM coordinates to latitude/longitude.
        
        Args:
            easting: Easting coordinate in meters
            northing: Northing coordinate in meters
            utm_zone: UTM zone number (1-60)
            is_southern: True if in southern hemisphere
            
        Returns:
            Dictionary with latitude, longitude, and original UTM info
            
        Raises:
            ValueError: If coordinates are invalid
        """
        try:
            # Validate UTM zone
            if not (1 <= utm_zone <= 60):
                raise ValueError(f"Invalid UTM zone: {utm_zone}")
            
            # Get UTM CRS
            utm_epsg = self._get_utm_epsg_from_zone(utm_zone, is_southern)
            utm_crs = CRS.from_epsg(utm_epsg)
            
            # Create transformer
            transformer = Transformer.from_crs(utm_crs, self.WGS84_CRS, always_xy=True)
            
            # Transform coordinates
            longitude, latitude = transformer.transform(easting, northing)
            
            return {
                'latitude': round(latitude, 6),
                'longitude': round(longitude, 6),
                'utm_zone': utm_zone,
                'is_southern': is_southern,
                'easting': easting,
                'northing': northing
            }
            
        except Exception as e:
            logger.error(f"Error converting UTM to lat/lon: {str(e)}")
            raise ValueError(f"Failed to convert coordinates: {str(e)}")

    def _calculate_utm_zone(self, longitude: float, latitude: float) -> int:
        """
        Calculate UTM zone from longitude and latitude.
        
        Args:
            longitude: Longitude in decimal degrees
            latitude: Latitude in decimal degrees
            
        Returns:
            UTM zone number (1-60)
        """
        # Standard UTM zone calculation
        zone = int((longitude + 180) / 6) + 1
        
        # Handle special cases (Norway and Svalbard)
        if 3 <= latitude < 12 and 56 <= longitude < 64:
            zone = 32  # Norway exception
        elif 72 <= latitude < 84 and 0 <= longitude < 42:
            # Svalbard exceptions
            if longitude < 9:
                zone = 31
            elif longitude < 21:
                zone = 33
            elif longitude < 33:
                zone = 35
            elif longitude < 42:
                zone = 37
        
        return zone

    def _get_utm_epsg(self, zone: int, latitude: float) -> int:
        """
        Get EPSG code for UTM zone.
        
        Args:
            zone: UTM zone number
            latitude: Latitude to determine hemisphere
            
        Returns:
            EPSG code for the UTM zone
        """
        # Northern hemisphere: 32601-32660
        # Southern hemisphere: 32701-32760
        if latitude >= 0:
            return 32600 + zone
        else:
            return 32700 + zone

    def _get_utm_epsg_from_zone(self, zone: int, is_southern: bool) -> int:
        """
        Get EPSG code from UTM zone and hemisphere.
        
        Args:
            zone: UTM zone number
            is_southern: True if southern hemisphere
            
        Returns:
            EPSG code for the UTM zone
        """
        if is_southern:
            return 32700 + zone
        else:
            return 32600 + zone

    def validate_round_trip(
        self,
        latitude: float,
        longitude: float,
        tolerance_meters: float = 1.0
    ) -> Dict:
        """
        Validate coordinate conversion round trip (lat/lon -> UTM -> lat/lon).
        
        Args:
            latitude: Original latitude
            longitude: Original longitude
            tolerance_meters: Acceptable error in meters
            
        Returns:
            Dictionary with validation results
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Convert to UTM
            utm_result = self.lat_lon_to_utm(latitude, longitude)
            
            # Convert back to lat/lon
            latlon_result = self.utm_to_lat_lon(
                utm_result['easting'],
                utm_result['northing'],
                utm_result['utm_zone'],
                is_southern=(latitude < 0)
            )
            
            # Calculate error
            lat_error = abs(latlon_result['latitude'] - latitude)
            lon_error = abs(latlon_result['longitude'] - longitude)
            
            # Convert degree error to meters (approximate)
            # 1 degree ≈ 111 km at equator
            lat_error_m = lat_error * 111000
            lon_error_m = lon_error * 111000 * abs(__import__('math').cos(__import__('math').radians(latitude)))
            
            max_error_m = max(lat_error_m, lon_error_m)
            
            is_valid = max_error_m <= tolerance_meters
            
            return {
                'is_valid': is_valid,
                'original_latitude': latitude,
                'original_longitude': longitude,
                'converted_latitude': latlon_result['latitude'],
                'converted_longitude': latlon_result['longitude'],
                'error_meters': round(max_error_m, 2),
                'tolerance_meters': tolerance_meters
            }
            
        except Exception as e:
            logger.error(f"Error validating round trip: {str(e)}")
            raise ValueError(f"Failed to validate round trip: {str(e)}")

    def batch_convert_lat_lon_to_utm(
        self,
        coordinates: list
    ) -> list:
        """
        Convert multiple lat/lon coordinates to UTM.
        
        Args:
            coordinates: List of [latitude, longitude] pairs
            
        Returns:
            List of UTM conversion results
        """
        results = []
        for lat, lon in coordinates:
            try:
                result = self.lat_lon_to_utm(lat, lon)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to convert ({lat}, {lon}): {str(e)}")
                results.append({'error': str(e)})
        
        return results
