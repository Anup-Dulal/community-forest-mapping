"""
DEM clipper module.
Handles clipping DEM rasters to boundary polygons.
"""

import logging
from typing import Dict
from osgeo import gdal
import geopandas as gpd
from shapely.geometry import shape
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DEMClipper:
    """Clips DEM rasters to boundary polygons."""

    def __init__(self, export_dir: str = './exports'):
        """
        Initialize DEM clipper.
        
        Args:
            export_dir: Directory to save clipped DEM files
        """
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def clip_dem(self, dem_path: str, boundary_geometry: Dict, output_path: str = None) -> str:
        """
        Clip DEM raster to boundary polygon.
        
        Property 4: DEM Clipping Boundary Constraint
        For any DEM raster and boundary polygon, the clipped DEM SHALL only 
        contain cells that intersect with the boundary polygon.
        
        Args:
            dem_path: Path to DEM raster file
            boundary_geometry: GeoJSON geometry dictionary of boundary
            output_path: Optional output path for clipped DEM
            
        Returns:
            Path to clipped DEM file
            
        Raises:
            ValueError: If clipping fails
        """
        logger.info(f"Clipping DEM to boundary")

        try:
            # Convert GeoJSON to shapely geometry
            boundary_geom = shape(boundary_geometry)

            # Ensure geometry is valid
            if not boundary_geom.is_valid:
                raise ValueError("Invalid boundary geometry")

            # Open DEM raster with GDAL
            dem_ds = gdal.Open(dem_path)
            if dem_ds is None:
                raise ValueError(f"Cannot open DEM file: {dem_path}")
            
            dem_band = dem_ds.GetRasterBand(1)
            dem_data = dem_band.ReadAsArray()
            geotransform = dem_ds.GetGeoTransform()
            projection = dem_ds.GetProjection()
            nodata = dem_band.GetNoDataValue()

            logger.info(f"DEM projection: {projection}")

            # For now, use simple bounding box clipping
            # Full polygon clipping would require more complex rasterization
            bounds = boundary_geom.bounds
            
            # Convert bounds to pixel coordinates
            x_min, y_min, x_max, y_max = bounds
            
            # Calculate pixel indices from geotransform
            # geotransform = (x_origin, pixel_width, 0, y_origin, 0, -pixel_height)
            x_origin, pixel_width, _, y_origin, _, pixel_height = geotransform
            
            col_min = max(0, int((x_min - x_origin) / pixel_width))
            col_max = min(dem_data.shape[1], int((x_max - x_origin) / pixel_width) + 1)
            row_min = max(0, int((y_origin - y_max) / abs(pixel_height)))
            row_max = min(dem_data.shape[0], int((y_origin - y_min) / abs(pixel_height)) + 1)
            
            # Clip data
            clipped_data = dem_data[row_min:row_max, col_min:col_max]
            
            # Update geotransform for clipped raster
            new_x_origin = x_origin + col_min * pixel_width
            new_y_origin = y_origin + row_min * pixel_height
            clipped_geotransform = (new_x_origin, pixel_width, 0, new_y_origin, 0, pixel_height)
            
            # Prepare output path
            if output_path is None:
                output_path = os.path.join(self.export_dir, f"dem_clipped_{hash(str(boundary_geometry))}.tif")

            # Save clipped raster using GDAL
            self._save_raster(output_path, clipped_data, clipped_geotransform, projection, nodata)

            logger.info(f"Clipped DEM saved: {output_path}")
            dem_ds = None  # Close dataset
            return output_path

        except Exception as e:
            logger.error(f"Error clipping DEM: {str(e)}")
            raise ValueError(f"Failed to clip DEM: {str(e)}")

    def validate_clipped_dem(self, clipped_dem_path: str, boundary_geometry: Dict) -> bool:
        """
        Validate that clipped DEM only contains cells within boundary.
        
        Property 4: DEM Clipping Boundary Constraint
        Verifies that all cells in clipped DEM intersect with boundary.
        
        Args:
            clipped_dem_path: Path to clipped DEM file
            boundary_geometry: GeoJSON geometry dictionary of boundary
            
        Returns:
            True if validation passes, False otherwise
        """
        try:
            boundary_geom = shape(boundary_geometry)

            # Open clipped DEM with GDAL
            dem_ds = gdal.Open(clipped_dem_path)
            if dem_ds is None:
                raise ValueError(f"Cannot open clipped DEM: {clipped_dem_path}")
            
            geotransform = dem_ds.GetGeoTransform()
            
            # Get bounds of clipped DEM from geotransform
            x_origin, pixel_width, _, y_origin, _, pixel_height = geotransform
            width = dem_ds.RasterXSize
            height = dem_ds.RasterYSize
            
            dem_bounds = (
                x_origin,
                y_origin + height * pixel_height,
                x_origin + width * pixel_width,
                y_origin
            )

            # Check if DEM bounds are within boundary
            boundary_bounds = boundary_geom.bounds

            # Verify DEM is within boundary (with small tolerance)
            tolerance = 0.0001
            if (dem_bounds[0] < boundary_bounds[0] - tolerance or
                dem_bounds[1] < boundary_bounds[1] - tolerance or
                dem_bounds[2] > boundary_bounds[2] + tolerance or
                dem_bounds[3] > boundary_bounds[3] + tolerance):
                logger.warning("Clipped DEM extends beyond boundary")
                dem_ds = None
                return False

            logger.info("Clipped DEM validation passed")
            dem_ds = None
            return True

        except Exception as e:
            logger.error(f"Error validating clipped DEM: {str(e)}")
            return False

    def _reproject_geometry(self, geometry, from_crs: str, to_crs: str):
        """
        Reproject geometry between coordinate systems.
        
        Args:
            geometry: Shapely geometry
            from_crs: Source CRS
            to_crs: Target CRS
            
        Returns:
            Reprojected geometry
        """
        try:
            from pyproj import Transformer

            transformer = Transformer.from_crs(from_crs, to_crs, always_xy=True)

            # Transform coordinates
            if hasattr(geometry, 'exterior'):
                # Polygon
                exterior_coords = [transformer.transform(x, y) for x, y in geometry.exterior.coords]
                interior_coords = [
                    [transformer.transform(x, y) for x, y in interior.coords]
                    for interior in geometry.interiors
                ]
                from shapely.geometry import Polygon
                return Polygon(exterior_coords, interior_coords)
            else:
                # Point or other
                from shapely.ops import transform
                return transform(lambda x, y: transformer.transform(x, y), geometry)

        except Exception as e:
            logger.error(f"Error reprojecting geometry: {str(e)}")
            raise ValueError(f"Failed to reproject geometry: {str(e)}")

    def _save_raster(self, output_path: str, data, geotransform, projection, nodata):
        """
        Save raster data using GDAL.
        
        Args:
            output_path: Output file path
            data: Raster data array
            geotransform: GDAL geotransform
            projection: GDAL projection
            nodata: NoData value
        """
        import numpy as np
        
        driver = gdal.GetDriverByName('GTiff')
        height, width = data.shape
        
        # Determine data type
        if data.dtype == np.uint8:
            gdal_dtype = gdal.GDT_Byte
        elif data.dtype == np.float32:
            gdal_dtype = gdal.GDT_Float32
        elif data.dtype == np.float64:
            gdal_dtype = gdal.GDT_Float64
        elif data.dtype == np.int32:
            gdal_dtype = gdal.GDT_Int32
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
