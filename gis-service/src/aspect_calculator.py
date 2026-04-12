"""
Aspect calculator module.
Calculates aspect from DEM and classifies into cardinal directions.
"""

import logging
from typing import Dict
import numpy as np
from osgeo import gdal
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class AspectCalculator:
    """Calculates aspect from DEM rasters."""

    # Aspect classification (8 cardinal directions)
    ASPECT_CLASSES = {
        'N': (337.5, 22.5),      # North
        'NE': (22.5, 67.5),      # North-East
        'E': (67.5, 112.5),      # East
        'SE': (112.5, 157.5),    # South-East
        'S': (157.5, 202.5),     # South
        'SW': (202.5, 247.5),    # South-West
        'W': (247.5, 292.5),     # West
        'NW': (292.5, 337.5)     # North-West
    }

    # Numeric codes for directions
    DIRECTION_CODES = {
        'N': 1, 'NE': 2, 'E': 3, 'SE': 4,
        'S': 5, 'SW': 6, 'W': 7, 'NW': 8
    }

    def __init__(self, export_dir: str = './exports'):
        """
        Initialize aspect calculator.
        
        Args:
            export_dir: Directory to save aspect raster files
        """
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def calculate_aspect(self, dem_path: str, output_path: str = None) -> str:
        """
        Calculate aspect from DEM raster.
        
        Property 6: Aspect Classification Completeness
        For any aspect value in degrees, it SHALL be classified into exactly 
        one of the eight cardinal directions: N, NE, E, SE, S, SW, W, NW.
        
        Args:
            dem_path: Path to DEM raster file
            output_path: Optional output path for aspect raster
            
        Returns:
            Path to aspect raster file
            
        Raises:
            ValueError: If calculation fails
        """
        logger.info(f"Calculating aspect from DEM: {dem_path}")

        try:
            # Open DEM with GDAL
            dem_ds = gdal.Open(dem_path)
            if dem_ds is None:
                raise ValueError(f"Cannot open DEM file: {dem_path}")
            
            dem_band = dem_ds.GetRasterBand(1)
            dem_data = dem_band.ReadAsArray().astype(np.float32)
            
            # Get geotransform and projection
            geotransform = dem_ds.GetGeoTransform()
            projection = dem_ds.GetProjection()

            # Calculate aspect
            aspect_degrees = self._calculate_aspect_degrees(dem_data)

            # Prepare output path
            if output_path is None:
                output_path = os.path.join(self.export_dir, f"aspect_{hash(dem_path)}.tif")

            # Save aspect raster using GDAL
            self._save_raster(output_path, aspect_degrees, geotransform, projection, -9999)

            logger.info(f"Aspect raster saved: {output_path}")
            dem_ds = None  # Close dataset
            return output_path

        except Exception as e:
            logger.error(f"Error calculating aspect: {str(e)}")
            raise ValueError(f"Failed to calculate aspect: {str(e)}")

    def classify_aspect(self, aspect_path: str, output_path: str = None) -> str:
        """
        Classify aspect into cardinal directions.
        
        Property 6: Aspect Classification Completeness
        For any aspect value in degrees, it SHALL be classified into exactly 
        one of the eight cardinal directions: N, NE, E, SE, S, SW, W, NW.
        
        Args:
            aspect_path: Path to aspect raster file
            output_path: Optional output path for classified raster
            
        Returns:
            Path to classified aspect raster
            
        Raises:
            ValueError: If classification fails
        """
        logger.info(f"Classifying aspect raster: {aspect_path}")

        try:
            # Open aspect raster with GDAL
            aspect_ds = gdal.Open(aspect_path)
            if aspect_ds is None:
                raise ValueError(f"Cannot open aspect raster: {aspect_path}")
            
            aspect_band = aspect_ds.GetRasterBand(1)
            aspect_data = aspect_band.ReadAsArray()
            
            # Get geotransform and projection
            geotransform = aspect_ds.GetGeoTransform()
            projection = aspect_ds.GetProjection()

            # Classify aspect
            classified = self._classify_aspect_data(aspect_data)

            # Prepare output path
            if output_path is None:
                output_path = os.path.join(self.export_dir, f"aspect_classified_{hash(aspect_path)}.tif")

            # Save classified raster using GDAL
            self._save_raster(output_path, classified, geotransform, projection, 0)

            logger.info(f"Classified aspect raster saved: {output_path}")
            aspect_ds = None  # Close dataset
            return output_path

        except Exception as e:
            logger.error(f"Error classifying aspect: {str(e)}")
            raise ValueError(f"Failed to classify aspect: {str(e)}")

    def _calculate_aspect_degrees(self, dem_data: np.ndarray) -> np.ndarray:
        """
        Calculate aspect in degrees using gradient method.
        
        Args:
            dem_data: DEM raster data
            
        Returns:
            Aspect raster in degrees (0-360)
        """
        # Get cell size (assuming 1 for now)
        cell_size = 1.0

        # Calculate gradients
        x, y = np.gradient(dem_data, cell_size)

        # Calculate aspect in radians using atan2
        aspect_rad = np.arctan2(-x, y)

        # Convert to degrees (0-360)
        aspect_deg = np.degrees(aspect_rad)
        aspect_deg = np.where(aspect_deg < 0, aspect_deg + 360, aspect_deg)

        return aspect_deg.astype(np.float32)

    def _classify_aspect_data(self, aspect_data: np.ndarray) -> np.ndarray:
        """
        Classify aspect data into 8 cardinal directions.
        
        Property 6: Aspect Classification Completeness
        Each aspect value SHALL be classified into exactly one direction.
        
        Args:
            aspect_data: Aspect raster data in degrees
            
        Returns:
            Classified raster (1=N, 2=NE, 3=E, 4=SE, 5=S, 6=SW, 7=W, 8=NW)
        """
        classified = np.zeros_like(aspect_data, dtype=np.uint8)

        # Classify into 8 directions
        # N: 337.5-22.5 (wraps around 0)
        classified[(aspect_data >= 337.5) | (aspect_data < 22.5)] = 1
        # NE: 22.5-67.5
        classified[(aspect_data >= 22.5) & (aspect_data < 67.5)] = 2
        # E: 67.5-112.5
        classified[(aspect_data >= 67.5) & (aspect_data < 112.5)] = 3
        # SE: 112.5-157.5
        classified[(aspect_data >= 112.5) & (aspect_data < 157.5)] = 4
        # S: 157.5-202.5
        classified[(aspect_data >= 157.5) & (aspect_data < 202.5)] = 5
        # SW: 202.5-247.5
        classified[(aspect_data >= 202.5) & (aspect_data < 247.5)] = 6
        # W: 247.5-292.5
        classified[(aspect_data >= 247.5) & (aspect_data < 292.5)] = 7
        # NW: 292.5-337.5
        classified[(aspect_data >= 292.5) & (aspect_data < 337.5)] = 8

        return classified

    def get_aspect_statistics(self, aspect_path: str) -> Dict:
        """
        Calculate statistics for aspect raster.
        
        Args:
            aspect_path: Path to aspect raster
            
        Returns:
            Dictionary with aspect statistics
        """
        try:
            # Open aspect raster with GDAL
            aspect_ds = gdal.Open(aspect_path)
            if aspect_ds is None:
                raise ValueError(f"Cannot open aspect raster: {aspect_path}")
            
            aspect_band = aspect_ds.GetRasterBand(1)
            aspect_data = aspect_band.ReadAsArray()
            nodata = aspect_band.GetNoDataValue()

            # Remove nodata values
            if nodata is not None:
                valid_data = aspect_data[aspect_data != nodata]
            else:
                valid_data = aspect_data.flatten()

            stats = {
                'min': float(np.min(valid_data)),
                'max': float(np.max(valid_data)),
                'mean': float(np.mean(valid_data)),
                'std': float(np.std(valid_data))
            }

            logger.info(f"Aspect statistics: {stats}")
            aspect_ds = None  # Close dataset
            return stats

        except Exception as e:
            logger.error(f"Error calculating aspect statistics: {str(e)}")
            raise ValueError(f"Failed to calculate aspect statistics: {str(e)}")

    def get_direction_name(self, code: int) -> str:
        """
        Get direction name from numeric code.
        
        Args:
            code: Numeric direction code (1-8)
            
        Returns:
            Direction name (N, NE, E, etc.)
        """
        for direction, direction_code in self.DIRECTION_CODES.items():
            if direction_code == code:
                return direction
        return "Unknown"

    def _save_raster(self, output_path: str, data: np.ndarray, geotransform, projection, nodata):
        """
        Save raster data using GDAL.
        
        Args:
            output_path: Output file path
            data: Raster data array
            geotransform: GDAL geotransform
            projection: GDAL projection
            nodata: NoData value
        """
        driver = gdal.GetDriverByName('GTiff')
        height, width = data.shape
        
        # Determine data type
        if data.dtype == np.uint8:
            gdal_dtype = gdal.GDT_Byte
        elif data.dtype == np.float32:
            gdal_dtype = gdal.GDT_Float32
        elif data.dtype == np.float64:
            gdal_dtype = gdal.GDT_Float64
        else:
            gdal_dtype = gdal.GDT_Float32
        
        ds = driver.Create(output_path, width, height, 1, gdal_dtype)
        ds.SetGeoTransform(geotransform)
        ds.SetProjection(projection)
        
        band = ds.GetRasterBand(1)
        band.WriteArray(data)
        if nodata is not None:
            band.SetNoDataValue(nodata)
        
        ds = None  # Close dataset
