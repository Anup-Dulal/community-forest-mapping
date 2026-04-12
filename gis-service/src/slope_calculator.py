"""
Slope calculator module.
Calculates slope from DEM and classifies into categories.
"""

import logging
from typing import Dict, Tuple
import numpy as np
from osgeo import gdal
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class SlopeCalculator:
    """Calculates slope from DEM rasters."""

    # Slope classification thresholds (in degrees)
    SLOPE_CLASSES = {
        'gentle': (0, 20),      # 0-20 degrees
        'moderate': (20, 30),   # 20-30 degrees
        'steep': (30, 90)       # >30 degrees
    }

    def __init__(self, export_dir: str = './exports'):
        """
        Initialize slope calculator.
        
        Args:
            export_dir: Directory to save slope raster files
        """
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def calculate_slope(self, dem_path: str, output_path: str = None) -> str:
        """
        Calculate slope from DEM raster.
        
        Property 5: Slope Classification Completeness
        For any slope value in degrees, it SHALL be classified into exactly 
        one of the three categories: 0–20°, 20–30°, or >30°.
        
        Args:
            dem_path: Path to DEM raster file
            output_path: Optional output path for slope raster
            
        Returns:
            Path to slope raster file
            
        Raises:
            ValueError: If calculation fails
        """
        logger.info(f"Calculating slope from DEM: {dem_path}")

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

            # Calculate slope using Zevenbergen & Thorne method
            slope_degrees = self._calculate_slope_degrees(dem_data)

            # Prepare output path
            if output_path is None:
                output_path = os.path.join(self.export_dir, f"slope_{hash(dem_path)}.tif")

            # Save slope raster using GDAL
            self._save_raster(output_path, slope_degrees, geotransform, projection, -9999)

            logger.info(f"Slope raster saved: {output_path}")
            dem_ds = None  # Close dataset
            return output_path

        except Exception as e:
            logger.error(f"Error calculating slope: {str(e)}")
            raise ValueError(f"Failed to calculate slope: {str(e)}")

    def classify_slope(self, slope_path: str, output_path: str = None) -> str:
        """
        Classify slope into categories and create classified raster.
        
        Property 5: Slope Classification Completeness
        For any slope value in degrees, it SHALL be classified into exactly 
        one of the three categories: 0–20°, 20–30°, or >30°.
        
        Args:
            slope_path: Path to slope raster file
            output_path: Optional output path for classified raster
            
        Returns:
            Path to classified slope raster
            
        Raises:
            ValueError: If classification fails
        """
        logger.info(f"Classifying slope raster: {slope_path}")

        try:
            # Open slope raster with GDAL
            slope_ds = gdal.Open(slope_path)
            if slope_ds is None:
                raise ValueError(f"Cannot open slope raster: {slope_path}")
            
            slope_band = slope_ds.GetRasterBand(1)
            slope_data = slope_band.ReadAsArray()
            
            # Get geotransform and projection
            geotransform = slope_ds.GetGeoTransform()
            projection = slope_ds.GetProjection()

            # Classify slope
            classified = self._classify_slope_data(slope_data)

            # Prepare output path
            if output_path is None:
                output_path = os.path.join(self.export_dir, f"slope_classified_{hash(slope_path)}.tif")

            # Save classified raster using GDAL
            self._save_raster(output_path, classified, geotransform, projection, 0)

            logger.info(f"Classified slope raster saved: {output_path}")
            slope_ds = None  # Close dataset
            return output_path

        except Exception as e:
            logger.error(f"Error classifying slope: {str(e)}")
            raise ValueError(f"Failed to classify slope: {str(e)}")

    def _calculate_slope_degrees(self, dem_data: np.ndarray) -> np.ndarray:
        """
        Calculate slope in degrees using Zevenbergen & Thorne method.
        
        Args:
            dem_data: DEM raster data
            
        Returns:
            Slope raster in degrees
        """
        # Get cell size (assuming 1 for now, should be from raster metadata)
        cell_size = 1.0

        # Calculate gradients
        x, y = np.gradient(dem_data, cell_size)

        # Calculate slope in radians
        slope_rad = np.arctan(np.sqrt(x**2 + y**2))

        # Convert to degrees
        slope_deg = np.degrees(slope_rad)

        return slope_deg.astype(np.float32)

    def _classify_slope_data(self, slope_data: np.ndarray) -> np.ndarray:
        """
        Classify slope data into categories.
        
        Property 5: Slope Classification Completeness
        Each slope value SHALL be classified into exactly one category.
        
        Args:
            slope_data: Slope raster data in degrees
            
        Returns:
            Classified raster (1=gentle, 2=moderate, 3=steep)
        """
        classified = np.zeros_like(slope_data, dtype=np.uint8)

        # Classify: 1=gentle (0-20), 2=moderate (20-30), 3=steep (>30)
        classified[(slope_data >= 0) & (slope_data < 20)] = 1
        classified[(slope_data >= 20) & (slope_data < 30)] = 2
        classified[slope_data >= 30] = 3

        return classified

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

    def get_slope_statistics(self, slope_path: str) -> Dict:
        """
        Calculate statistics for slope raster.
        
        Args:
            slope_path: Path to slope raster
            
        Returns:
            Dictionary with slope statistics
        """
        try:
            # Open slope raster with GDAL
            slope_ds = gdal.Open(slope_path)
            if slope_ds is None:
                raise ValueError(f"Cannot open slope raster: {slope_path}")
            
            slope_band = slope_ds.GetRasterBand(1)
            slope_data = slope_band.ReadAsArray()
            nodata = slope_band.GetNoDataValue()

            # Remove nodata values
            if nodata is not None:
                valid_data = slope_data[slope_data != nodata]
            else:
                valid_data = slope_data.flatten()

            stats = {
                'min': float(np.min(valid_data)),
                'max': float(np.max(valid_data)),
                'mean': float(np.mean(valid_data)),
                'std': float(np.std(valid_data)),
                'median': float(np.median(valid_data))
            }

            logger.info(f"Slope statistics: {stats}")
            slope_ds = None  # Close dataset
            return stats

        except Exception as e:
            logger.error(f"Error calculating slope statistics: {str(e)}")
            raise ValueError(f"Failed to calculate slope statistics: {str(e)}")
