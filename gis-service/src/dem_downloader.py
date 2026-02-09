"""
DEM downloader module.
Handles downloading DEM data from various sources (SRTM, OpenTopography, NASA).
"""

import os
import logging
from typing import Dict, Optional, Tuple
import requests
import rasterio
from rasterio.io import MemoryFile
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class DEMDownloader:
    """Downloads DEM data from various sources."""

    # SRTM tile size
    SRTM_TILE_SIZE = 1  # 1 degree tiles

    def __init__(self, cache_dir: str = './dem_cache'):
        """
        Initialize DEM downloader.
        
        Args:
            cache_dir: Directory to cache downloaded DEM files
        """
        self.cache_dir = cache_dir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

    def download_dem(self, bbox: Dict, source: str = 'SRTM') -> str:
        """
        Download DEM data for given bounding box.
        
        Property 4: DEM Clipping Boundary Constraint (partial)
        Ensures DEM covers the bounding box area.
        
        Args:
            bbox: Bounding box dictionary with minLon, maxLon, minLat, maxLat
            source: DEM source ('SRTM', 'OpenTopography', 'NASA')
            
        Returns:
            Path to downloaded DEM file
            
        Raises:
            ValueError: If download fails
        """
        logger.info(f"Downloading DEM from {source} for bbox: {bbox}")

        try:
            if source == 'SRTM':
                return self._download_srtm(bbox)
            elif source == 'OpenTopography':
                return self._download_opentopography(bbox)
            elif source == 'NASA':
                return self._download_nasa(bbox)
            else:
                raise ValueError(f"Unknown DEM source: {source}")
        except Exception as e:
            logger.error(f"Error downloading DEM: {str(e)}")
            raise ValueError(f"Failed to download DEM: {str(e)}")

    def _download_srtm(self, bbox: Dict) -> str:
        """
        Download SRTM 30m DEM data.
        
        Args:
            bbox: Bounding box dictionary
            
        Returns:
            Path to downloaded DEM file
        """
        logger.info("Downloading SRTM 30m DEM")

        # Calculate tile indices
        min_lon = int(np.floor(bbox['minLon']))
        max_lon = int(np.ceil(bbox['maxLon']))
        min_lat = int(np.floor(bbox['minLat']))
        max_lat = int(np.ceil(bbox['maxLat']))

        # Download tiles
        tiles = []
        for lon in range(min_lon, max_lon):
            for lat in range(min_lat, max_lat):
                tile_path = self._download_srtm_tile(lon, lat)
                if tile_path:
                    tiles.append(tile_path)

        if not tiles:
            raise ValueError("No SRTM tiles available for bbox")

        # Merge tiles if multiple
        if len(tiles) == 1:
            return tiles[0]
        else:
            return self._merge_rasters(tiles, bbox)

    def _download_srtm_tile(self, lon: int, lat: int) -> Optional[str]:
        """
        Download a single SRTM tile.
        
        Args:
            lon: Longitude of tile
            lat: Latitude of tile
            
        Returns:
            Path to downloaded tile or None if not available
        """
        try:
            # SRTM tile naming convention: N/S + latitude, E/W + longitude
            ns = 'N' if lat >= 0 else 'S'
            ew = 'E' if lon >= 0 else 'W'
            tile_name = f"{ns}{abs(lat):02d}{ew}{abs(lon):03d}"

            # Check cache first
            cache_path = os.path.join(self.cache_dir, f"{tile_name}.tif")
            if os.path.exists(cache_path):
                logger.debug(f"Using cached SRTM tile: {tile_name}")
                return cache_path

            # Download from USGS SRTM server
            url = f"https://cloud.sdsc.edu/v1/AUTH_ogc/Raster/SRTM_GL30/SRTM_GL30_srtm/{tile_name}.tar.gz"

            logger.info(f"Downloading SRTM tile: {tile_name}")
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                # Extract and save
                import tarfile
                import io
                tar = tarfile.open(fileobj=io.BytesIO(response.content))
                # Extract the .tif file
                for member in tar.getmembers():
                    if member.name.endswith('.tif'):
                        tar.extract(member, self.cache_dir)
                        extracted_path = os.path.join(self.cache_dir, member.name)
                        # Move to cache with standard name
                        import shutil
                        shutil.move(extracted_path, cache_path)
                        logger.info(f"Cached SRTM tile: {tile_name}")
                        return cache_path

            logger.warning(f"SRTM tile not available: {tile_name}")
            return None

        except Exception as e:
            logger.error(f"Error downloading SRTM tile {lon},{lat}: {str(e)}")
            return None

    def _download_opentopography(self, bbox: Dict) -> str:
        """
        Download DEM from OpenTopography API.
        
        Args:
            bbox: Bounding box dictionary
            
        Returns:
            Path to downloaded DEM file
        """
        logger.info("Downloading DEM from OpenTopography")

        api_key = os.getenv('OPENTOPOGRAPHY_API_KEY')
        if not api_key:
            raise ValueError("OpenTopography API key not configured")

        # OpenTopography API endpoint
        url = "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SRTM_GL30/SRTM_GL30_srtm/SRTM_GL30_srtm_srtm.tif"

        params = {
            'west': bbox['minLon'],
            'south': bbox['minLat'],
            'east': bbox['maxLon'],
            'north': bbox['maxLat'],
            'outputFormat': 'GeoTIFF'
        }

        try:
            response = requests.get(url, params=params, headers={'Authorization': f'Bearer {api_key}'}, timeout=60)
            response.raise_for_status()

            # Save to cache
            cache_path = os.path.join(self.cache_dir, f"dem_opentopography_{hash(str(bbox))}.tif")
            with open(cache_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded DEM from OpenTopography: {cache_path}")
            return cache_path

        except Exception as e:
            logger.error(f"Error downloading from OpenTopography: {str(e)}")
            raise ValueError(f"Failed to download from OpenTopography: {str(e)}")

    def _download_nasa(self, bbox: Dict) -> str:
        """
        Download DEM from NASA sources.
        
        Args:
            bbox: Bounding box dictionary
            
        Returns:
            Path to downloaded DEM file
        """
        logger.info("Downloading DEM from NASA")

        api_key = os.getenv('NASA_API_KEY')
        if not api_key:
            raise ValueError("NASA API key not configured")

        # NASA ASTER GDEM endpoint
        url = "https://lpdaac.usgs.gov/products/astgtmv003/"

        # For now, fall back to SRTM
        logger.warning("NASA download not fully implemented, using SRTM fallback")
        return self._download_srtm(bbox)

    def _merge_rasters(self, raster_paths: list, bbox: Dict) -> str:
        """
        Merge multiple raster tiles into single raster.
        
        Args:
            raster_paths: List of raster file paths
            bbox: Bounding box for output
            
        Returns:
            Path to merged raster
        """
        try:
            import rasterio.merge
            from rasterio.io import MemoryFile

            logger.info(f"Merging {len(raster_paths)} raster tiles")

            # Open all rasters
            sources = [rasterio.open(path) for path in raster_paths]

            # Merge
            merged_data, merged_transform = rasterio.merge.merge(sources)

            # Save merged raster
            cache_path = os.path.join(self.cache_dir, f"dem_merged_{hash(str(bbox))}.tif")

            with rasterio.open(
                cache_path,
                'w',
                driver='GTiff',
                height=merged_data.shape[1],
                width=merged_data.shape[2],
                count=merged_data.shape[0],
                dtype=merged_data.dtype,
                transform=merged_transform,
                crs='EPSG:4326'
            ) as dst:
                dst.write(merged_data)

            # Close sources
            for src in sources:
                src.close()

            logger.info(f"Merged raster saved: {cache_path}")
            return cache_path

        except Exception as e:
            logger.error(f"Error merging rasters: {str(e)}")
            raise ValueError(f"Failed to merge rasters: {str(e)}")
