"""
DEM Downloader using GDAL and public SRTM data from AWS
"""
import os
import logging
import requests
import gzip
import struct
from osgeo import gdal, osr
import numpy as np
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_srtm_tile_url(lat, lon):
    """
    Get the AWS S3 URL for an SRTM tile
    SRTM tiles are named based on their southwest corner
    """
    # Determine hemisphere indicators
    lat_hem = 'N' if lat >= 0 else 'S'
    lon_hem = 'E' if lon >= 0 else 'W'
    
    # Format coordinates (SRTM uses southwest corner)
    lat_str = f"{lat_hem}{abs(int(lat)):02d}"
    lon_str = f"{lon_hem}{abs(int(lon)):03d}"
    
    # AWS Terrain Tiles URL pattern
    url = f"https://elevation-tiles-prod.s3.amazonaws.com/skadi/{lat_str}/{lat_str}{lon_str}.hgt.gz"
    
    return url

def hgt_to_geotiff(hgt_path, tif_path, lat, lon):
    """
    Convert SRTM HGT file to GeoTIFF
    
    Args:
        hgt_path: Path to .hgt file
        tif_path: Output GeoTIFF path
        lat: Latitude of southwest corner
        lon: Longitude of southwest corner
    """
    # SRTM 1 arc-second data is 3601x3601 pixels
    size = 3601
    
    # Read binary data
    with open(hgt_path, 'rb') as f:
        data = f.read()
    
    # Convert to numpy array (big-endian 16-bit signed integers)
    elevations = np.frombuffer(data, dtype='>i2').reshape((size, size))
    
    # Create GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(tif_path, size, size, 1, gdal.GDT_Int16)
    
    # Set geotransform (top-left corner, pixel size)
    # SRTM data goes from north to south
    pixel_size = 1.0 / (size - 1)
    geotransform = (lon, pixel_size, 0, lat + 1, 0, -pixel_size)
    ds.SetGeoTransform(geotransform)
    
    # Set projection (WGS84)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    ds.SetProjection(srs.ExportToWkt())
    
    # Write data
    band = ds.GetRasterBand(1)
    band.WriteArray(elevations)
    band.SetNoDataValue(-32768)
    
    ds = None  # Close dataset
    logger.info(f"Converted HGT to GeoTIFF: {tif_path}")

def download_dem(bounds, output_path):
    """
    Download DEM data for the given bounds using AWS Terrain Tiles (SRTM)
    
    Args:
        bounds: Dictionary with minLon, minLat, maxLon, maxLat
        output_path: Path where the DEM file should be saved
        
    Returns:
        str: Path to the downloaded DEM file
    """
    try:
        logger.info(f"Starting DEM download for bounds: {bounds}")
        logger.info(f"Output path: {output_path}")
        
        min_lon = bounds['minLon']
        min_lat = bounds['minLat']
        max_lon = bounds['maxLon']
        max_lat = bounds['maxLat']
        
        # Calculate SRTM tile coordinates (tiles are 1x1 degree)
        start_lon = int(np.floor(min_lon))
        end_lon = int(np.floor(max_lon))
        start_lat = int(np.floor(min_lat))
        end_lat = int(np.floor(max_lat))
        
        logger.info(f"SRTM tiles needed: lon {start_lon} to {end_lon}, lat {start_lat} to {end_lat}")
        
        # Download tiles
        tile_files = []
        temp_dir = tempfile.mkdtemp()
        
        for lat in range(start_lat, end_lat + 1):
            for lon in range(start_lon, end_lon + 1):
                url = get_srtm_tile_url(lat, lon)
                logger.info(f"Downloading tile from: {url}")
                
                try:
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        # Save compressed file
                        gz_path = os.path.join(temp_dir, f"tile_{lat}_{lon}.hgt.gz")
                        with open(gz_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Decompress the file
                        hgt_path = os.path.join(temp_dir, f"tile_{lat}_{lon}.hgt")
                        with gzip.open(gz_path, 'rb') as f_in:
                            with open(hgt_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        
                        # Convert to GeoTIFF
                        tif_path = os.path.join(temp_dir, f"tile_{lat}_{lon}.tif")
                        hgt_to_geotiff(hgt_path, tif_path, lat, lon)
                        
                        tile_files.append(tif_path)
                        logger.info(f"Downloaded and converted tile for lat={lat}, lon={lon}")
                    else:
                        logger.warning(f"Tile not available: {url} (status {response.status_code})")
                except Exception as e:
                    logger.warning(f"Failed to download tile for lat={lat}, lon={lon}: {str(e)}")
        
        if not tile_files:
            raise Exception("No SRTM tiles could be downloaded for the specified area")
        
        logger.info(f"Downloaded {len(tile_files)} tiles")
        
        # Merge tiles if multiple
        if len(tile_files) == 1:
            merged_vrt = tile_files[0]
        else:
            # Create VRT to merge tiles
            vrt_path = os.path.join(temp_dir, "merged.vrt")
            vrt_options = gdal.BuildVRTOptions(resampleAlg='bilinear')
            vrt_ds = gdal.BuildVRT(vrt_path, tile_files, options=vrt_options)
            vrt_ds = None
            merged_vrt = vrt_path
        
        logger.info(f"Merging tiles and clipping to bounds...")
        
        # Clip to exact bounds and save as GeoTIFF
        warp_options = gdal.WarpOptions(
            format='GTiff',
            outputBounds=[min_lon, min_lat, max_lon, max_lat],
            dstSRS='EPSG:4326',
            resampleAlg='bilinear',
            outputType=gdal.GDT_Float32,
            creationOptions=['COMPRESS=LZW', 'TILED=YES']
        )
        
        result = gdal.Warp(output_path, merged_vrt, options=warp_options)
        
        if result is None:
            raise Exception("GDAL Warp failed")
        
        result = None  # Close dataset
        
        logger.info(f"DEM downloaded and clipped successfully to {output_path}")
        
        # Verify the output
        ds = gdal.Open(output_path)
        if ds is None:
            raise Exception("Output file is not a valid GeoTIFF")
        
        logger.info(f"DEM verification successful - Size: {ds.RasterXSize}x{ds.RasterYSize}")
        ds = None
        
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error downloading DEM: {str(e)}")
        raise
