"""
Google Maps-style Tile Server using GDAL
Generates PNG tiles from GeoTIFF rasters using Web Mercator projection (EPSG:3857)
"""

import math
import numpy as np
from osgeo import gdal, osr
from PIL import Image
import io
import logging
from typing import Tuple, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

# Enable GDAL exceptions
gdal.UseExceptions()


class TileCoordinates:
    """Google Maps tile coordinate system utilities"""
    
    TILE_SIZE = 256
    EARTH_RADIUS = 6378137  # meters
    ORIGIN_SHIFT = 2 * math.pi * EARTH_RADIUS / 2.0
    
    @staticmethod
    def tile_to_meters(tx: int, ty: int, zoom: int) -> Tuple[float, float, float, float]:
        """Convert tile coordinates to Web Mercator meters (EPSG:3857)"""
        resolution = TileCoordinates.resolution(zoom)
        minx = tx * TileCoordinates.TILE_SIZE * resolution - TileCoordinates.ORIGIN_SHIFT
        maxy = TileCoordinates.ORIGIN_SHIFT - ty * TileCoordinates.TILE_SIZE * resolution
        maxx = (tx + 1) * TileCoordinates.TILE_SIZE * resolution - TileCoordinates.ORIGIN_SHIFT
        miny = TileCoordinates.ORIGIN_SHIFT - (ty + 1) * TileCoordinates.TILE_SIZE * resolution
        return minx, miny, maxx, maxy
    
    @staticmethod
    def resolution(zoom: int) -> float:
        """Resolution (meters/pixel) for given zoom level"""
        return (2 * TileCoordinates.ORIGIN_SHIFT) / (TileCoordinates.TILE_SIZE * 2 ** zoom)
    
    @staticmethod
    def latlon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """Convert lat/lon to tile coordinates"""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile


class TerrainTileServer:
    """Serves raster tiles for terrain data using Google Maps tile scheme"""
    
    # Color ramps for different terrain types
    COLORMAPS = {
        'dem': [
            (0, (0, 0, 128)),      # Deep blue for low elevations
            (0.2, (0, 128, 0)),    # Green
            (0.4, (255, 255, 0)),  # Yellow
            (0.6, (255, 128, 0)),  # Orange
            (0.8, (139, 69, 19)),  # Brown
            (1.0, (255, 255, 255)) # White for peaks
        ],
        'slope': [
            (0, (0, 255, 0)),      # Green for flat
            (0.3, (255, 255, 0)),  # Yellow
            (0.6, (255, 128, 0)),  # Orange
            (1.0, (255, 0, 0))     # Red for steep
        ],
        'aspect': [
            (0, (255, 0, 0)),      # Red for North
            (0.25, (255, 255, 0)), # Yellow for East
            (0.5, (0, 255, 0)),    # Green for South
            (0.75, (0, 255, 255)), # Cyan for West
            (1.0, (255, 0, 0))     # Red for North again
        ]
    }
    
    @staticmethod
    def apply_colormap(data: np.ndarray, colormap_name: str, vmin: float, vmax: float) -> np.ndarray:
        """Apply a colormap to normalized data"""
        colormap = TerrainTileServer.COLORMAPS.get(colormap_name, TerrainTileServer.COLORMAPS['dem'])
        
        # Normalize data to 0-1
        data_norm = np.clip((data - vmin) / (vmax - vmin + 1e-10), 0, 1)
        
        # Create RGB image
        rgb = np.zeros((*data.shape, 3), dtype=np.uint8)
        
        for i in range(len(colormap) - 1):
            pos1, color1 = colormap[i]
            pos2, color2 = colormap[i + 1]
            
            # Find pixels in this range
            mask = (data_norm >= pos1) & (data_norm < pos2)
            
            # Interpolate colors
            t = (data_norm[mask] - pos1) / (pos2 - pos1 + 1e-10)
            for c in range(3):
                rgb[mask, c] = (1 - t) * color1[c] + t * color2[c]
        
        # Handle the last segment
        mask = data_norm >= colormap[-1][0]
        rgb[mask] = colormap[-1][1]
        
        return rgb
    
    @staticmethod
    def get_tile(raster_path: str, z: int, x: int, y: int, colormap: str = "dem") -> bytes:
        """
        Generate a PNG tile from a GeoTIFF raster using Google Maps tile coordinates
        
        Args:
            raster_path: Path to the GeoTIFF file
            z: Zoom level
            x: Tile X coordinate
            y: Tile Y coordinate
            colormap: Color map to apply (dem, slope, aspect)
            
        Returns:
            PNG image bytes
        """
        try:
            # Get tile bounds in Web Mercator
            minx, miny, maxx, maxy = TileCoordinates.tile_to_meters(x, y, z)
            
            # Open source raster
            src_ds = gdal.Open(raster_path)
            if src_ds is None:
                raise ValueError(f"Could not open raster: {raster_path}")
            
            # Get source projection
            src_srs = osr.SpatialReference()
            src_srs.ImportFromWkt(src_ds.GetProjection())
            
            # Create Web Mercator projection
            dst_srs = osr.SpatialReference()
            dst_srs.ImportFromEPSG(3857)
            
            # Create temporary VRT for reprojection
            vrt_options = gdal.WarpOptions(
                format='VRT',
                srcSRS=src_srs.ExportToWkt(),
                dstSRS=dst_srs.ExportToWkt(),
                outputBounds=[minx, miny, maxx, maxy],
                width=TileCoordinates.TILE_SIZE,
                height=TileCoordinates.TILE_SIZE,
                resampleAlg='bilinear',
                outputType=gdal.GDT_Float32
            )
            
            # Warp to tile bounds
            vrt_ds = gdal.Warp('', src_ds, options=vrt_options)
            
            if vrt_ds is None:
                # Return transparent tile if no data
                return TerrainTileServer._create_empty_tile()
            
            # Read data
            band = vrt_ds.GetRasterBand(1)
            data = band.ReadAsArray()
            
            if data is None or data.size == 0:
                return TerrainTileServer._create_empty_tile()
            
            # Get nodata value
            nodata = band.GetNoDataValue()
            
            # Mask nodata values
            if nodata is not None:
                mask = data == nodata
            else:
                mask = np.isnan(data)
            
            # Get statistics for colormap
            valid_data = data[~mask]
            if valid_data.size == 0:
                return TerrainTileServer._create_empty_tile()
            
            vmin = np.percentile(valid_data, 2)
            vmax = np.percentile(valid_data, 98)
            
            # Apply colormap
            rgb = TerrainTileServer.apply_colormap(data, colormap, vmin, vmax)
            
            # Apply transparency to nodata
            rgba = np.dstack([rgb, np.where(mask, 0, 255).astype(np.uint8)])
            
            # Convert to PIL Image
            img = Image.fromarray(rgba, mode='RGBA')
            
            # Save to bytes
            buf = io.BytesIO()
            img.save(buf, format='PNG', optimize=True)
            buf.seek(0)
            
            return buf.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating tile z={z} x={x} y={y}: {str(e)}")
            return TerrainTileServer._create_empty_tile()
    
    @staticmethod
    def _create_empty_tile() -> bytes:
        """Create a transparent empty tile"""
        img = Image.new('RGBA', (TileCoordinates.TILE_SIZE, TileCoordinates.TILE_SIZE), (0, 0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()
    
    @staticmethod
    def get_dem_tile(raster_path: str, z: int, x: int, y: int) -> bytes:
        """Generate DEM tile with elevation colormap"""
        return TerrainTileServer.get_tile(raster_path, z, x, y, colormap="dem")
    
    @staticmethod
    def get_slope_tile(raster_path: str, z: int, x: int, y: int) -> bytes:
        """Generate slope tile with gradient colormap"""
        return TerrainTileServer.get_tile(raster_path, z, x, y, colormap="slope")
    
    @staticmethod
    def get_aspect_tile(raster_path: str, z: int, x: int, y: int) -> bytes:
        """Generate aspect tile with circular colormap"""
        return TerrainTileServer.get_tile(raster_path, z, x, y, colormap="aspect")
    
    @staticmethod
    def get_bounds(raster_path: str) -> dict:
        """Get the geographic bounds of a raster in WGS84"""
        try:
            ds = gdal.Open(raster_path)
            if ds is None:
                raise ValueError(f"Could not open raster: {raster_path}")
            
            # Get geotransform
            transform = ds.GetGeoTransform()
            width = ds.RasterXSize
            height = ds.RasterYSize
            
            # Calculate corners
            minx = transform[0]
            maxy = transform[3]
            maxx = minx + width * transform[1]
            miny = maxy + height * transform[5]
            
            # Get source projection
            src_srs = osr.SpatialReference()
            src_srs.ImportFromWkt(ds.GetProjection())
            
            # Create WGS84 projection
            dst_srs = osr.SpatialReference()
            dst_srs.ImportFromEPSG(4326)
            
            # Transform to WGS84 if needed
            if not src_srs.IsSame(dst_srs):
                transform_func = osr.CoordinateTransformation(src_srs, dst_srs)
                minx, miny, _ = transform_func.TransformPoint(minx, miny)
                maxx, maxy, _ = transform_func.TransformPoint(maxx, maxy)
            
            return {
                "minLon": minx,
                "minLat": miny,
                "maxLon": maxx,
                "maxLat": maxy
            }
        except Exception as e:
            logger.error(f"Error getting bounds: {str(e)}")
            raise
    
    @staticmethod
    def get_statistics(raster_path: str) -> dict:
        """Get raster statistics (min, max, mean, etc.)"""
        try:
            ds = gdal.Open(raster_path)
            if ds is None:
                raise ValueError(f"Could not open raster: {raster_path}")
            
            band = ds.GetRasterBand(1)
            stats = band.GetStatistics(True, True)
            
            return {
                "min": float(stats[0]),
                "max": float(stats[1]),
                "mean": float(stats[2]),
                "std": float(stats[3])
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise
