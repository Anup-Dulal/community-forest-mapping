"""
Slope calculator module.
Calculates slope from DEM and classifies into categories.
"""

import logging
from typing import Dict, Tuple
import numpy as np
import rasterio
from rasterio.plot import show
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
            with rasterio.open(dem_path) as src:
                dem_data = src.read(1).astype(np.float32)
                dem_crs = src.crs
                dem_transform = src.transform

                # Calculate slope using Zevenbergen & Thorne method
                slope_degrees = self._calculate_slope_degrees(dem_data)

                # Prepare output path
                if output_path is None:
                    output_path = os.path.join(self.export_dir, f"slope_{hash(dem_path)}.tif")

                # Save slope raster
                with rasterio.open(
                    output_path,
                    'w',
                    driver='GTiff',
                    height=slope_degrees.shape[0],
                    width=slope_degrees.shape[1],
                    count=1,
                    dtype=slope_degrees.dtype,
                    crs=dem_crs,
                    transform=dem_transform,
                    nodata=-9999
                ) as dst:
                    dst.write(slope_degrees, 1)

                logger.info(f"Slope raster saved: {output_path}")
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
            with rasterio.open(slope_path) as src:
                slope_data = src.read(1)
                slope_crs = src.crs
                slope_transform = src.transform

                # Classify slope
                classified = self._classify_slope_data(slope_data)

                # Prepare output path
                if output_path is None:
                    output_path = os.path.join(self.export_dir, f"slope_classified_{hash(slope_path)}.tif")

                # Save classified raster
                with rasterio.open(
                    output_path,
                    'w',
                    driver='GTiff',
                    height=classified.shape[0],
                    width=classified.shape[1],
                    count=1,
                    dtype=classified.dtype,
                    crs=slope_crs,
                    transform=slope_transform,
                    nodata=0
                ) as dst:
                    dst.write(classified, 1)

                logger.info(f"Classified slope raster saved: {output_path}")
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

    def get_slope_statistics(self, slope_path: str) -> Dict:
        """
        Calculate statistics for slope raster.
        
        Args:
            slope_path: Path to slope raster
            
        Returns:
            Dictionary with slope statistics
        """
        try:
            with rasterio.open(slope_path) as src:
                slope_data = src.read(1)

                # Remove nodata values
                valid_data = slope_data[slope_data != src.nodata]

                stats = {
                    'min': float(np.min(valid_data)),
                    'max': float(np.max(valid_data)),
                    'mean': float(np.mean(valid_data)),
                    'std': float(np.std(valid_data)),
                    'median': float(np.median(valid_data))
                }

                logger.info(f"Slope statistics: {stats}")
                return stats

        except Exception as e:
            logger.error(f"Error calculating slope statistics: {str(e)}")
            raise ValueError(f"Failed to calculate slope statistics: {str(e)}")
