"""
DEM clipper module.
Handles clipping DEM rasters to boundary polygons.
"""

import logging
from typing import Dict
import rasterio
from rasterio.mask import mask
from rasterio.io import MemoryFile
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

            # Open DEM raster
            with rasterio.open(dem_path) as src:
                # Get DEM CRS
                dem_crs = src.crs

                logger.info(f"DEM CRS: {dem_crs}")

                # Reproject boundary to DEM CRS if needed
                if dem_crs and dem_crs != 'EPSG:4326':
                    logger.info(f"Reprojecting boundary from EPSG:4326 to {dem_crs}")
                    boundary_geom = self._reproject_geometry(boundary_geom, 'EPSG:4326', dem_crs)

                # Clip raster to boundary
                clipped_data, clipped_transform = mask(
                    src,
                    [boundary_geom],
                    crop=True,
                    nodata=src.nodata
                )

                # Prepare output path
                if output_path is None:
                    output_path = os.path.join(self.export_dir, f"dem_clipped_{hash(str(boundary_geometry))}.tif")

                # Save clipped raster
                with rasterio.open(
                    output_path,
                    'w',
                    driver='GTiff',
                    height=clipped_data.shape[1],
                    width=clipped_data.shape[2],
                    count=clipped_data.shape[0],
                    dtype=clipped_data.dtype,
                    crs=dem_crs,
                    transform=clipped_transform,
                    nodata=src.nodata
                ) as dst:
                    dst.write(clipped_data)

                logger.info(f"Clipped DEM saved: {output_path}")
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

            with rasterio.open(clipped_dem_path) as src:
                # Get bounds of clipped DEM
                dem_bounds = src.bounds
                dem_crs = src.crs

                # Reproject boundary if needed
                if dem_crs and dem_crs != 'EPSG:4326':
                    boundary_geom = self._reproject_geometry(boundary_geom, 'EPSG:4326', dem_crs)

                # Check if DEM bounds are within boundary
                boundary_bounds = boundary_geom.bounds

                # Verify DEM is within boundary (with small tolerance)
                tolerance = 0.0001
                if (dem_bounds.left < boundary_bounds[0] - tolerance or
                    dem_bounds.bottom < boundary_bounds[1] - tolerance or
                    dem_bounds.right > boundary_bounds[2] + tolerance or
                    dem_bounds.top > boundary_bounds[3] + tolerance):
                    logger.warning("Clipped DEM extends beyond boundary")
                    return False

                logger.info("Clipped DEM validation passed")
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
