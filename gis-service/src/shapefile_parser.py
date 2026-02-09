"""
Shapefile parser module.
Handles reading and parsing shapefile components using Fiona and GeoPandas.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import geopandas as gpd
import fiona
from shapely.geometry import mapping, shape
import json

logger = logging.getLogger(__name__)


class ShapefileParser:
    """Parser for ESRI shapefiles."""

    @staticmethod
    def parse_shapefile(shapefile_dir: str) -> Dict:
        """
        Parse shapefile components and extract boundary geometry.
        
        Property 2: Shapefile Parsing Round Trip
        For any valid shapefile, parsing it and then serializing it back 
        should produce a geometrically equivalent boundary polygon.
        
        Args:
            shapefile_dir: Directory containing shapefile components
            
        Returns:
            Dictionary with parsed geometry and metadata
            
        Raises:
            FileNotFoundError: If required shapefile components are missing
            ValueError: If shapefile is invalid
        """
        logger.info(f"Parsing shapefile from directory: {shapefile_dir}")
        
        # Find .shp file
        shp_file = ShapefileParser._find_file(shapefile_dir, '.shp')
        if not shp_file:
            raise FileNotFoundError(f"No .shp file found in {shapefile_dir}")
        
        try:
            # Read shapefile using GeoPandas
            gdf = gpd.read_file(shp_file)
            logger.info(f"Successfully read shapefile with {len(gdf)} features")
            
            # Validate geometry
            if gdf.empty:
                raise ValueError("Shapefile contains no features")
            
            # Get the first feature (boundary)
            boundary = gdf.iloc[0]
            geometry = boundary.geometry
            
            # Validate geometry type
            if geometry.geom_type not in ['Polygon', 'MultiPolygon']:
                raise ValueError(f"Expected Polygon or MultiPolygon, got {geometry.geom_type}")
            
            # Convert to GeoJSON
            geojson_geometry = mapping(geometry)
            
            # Extract bounding box
            bounds = geometry.bounds  # (minx, miny, maxx, maxy)
            bounding_box = {
                'minLon': bounds[0],
                'minLat': bounds[1],
                'maxLon': bounds[2],
                'maxLat': bounds[3]
            }
            
            # Get projection info
            projection = str(gdf.crs) if gdf.crs else "EPSG:4326"
            
            result = {
                'geometry': geojson_geometry,
                'boundingBox': bounding_box,
                'projection': projection,
                'featureCount': len(gdf),
                'geometryType': geometry.geom_type,
                'area': float(geometry.area),
                'status': 'parsed'
            }
            
            logger.info(f"Shapefile parsing successful. Projection: {projection}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing shapefile: {str(e)}")
            raise ValueError(f"Failed to parse shapefile: {str(e)}")
    
    @staticmethod
    def validate_geometry_integrity(geometry_dict: Dict) -> bool:
        """
        Validate geometry integrity.
        
        Args:
            geometry_dict: GeoJSON geometry dictionary
            
        Returns:
            True if geometry is valid, False otherwise
        """
        try:
            geom = shape(geometry_dict)
            return geom.is_valid
        except Exception as e:
            logger.error(f"Geometry validation failed: {str(e)}")
            return False
    
    @staticmethod
    def _find_file(directory: str, extension: str) -> Optional[str]:
        """
        Find file with given extension in directory.
        
        Args:
            directory: Directory to search
            extension: File extension (e.g., '.shp')
            
        Returns:
            Full path to file or None if not found
        """
        path = Path(directory)
        for file in path.glob(f'*{extension}'):
            return str(file)
        return None
    
    @staticmethod
    def extract_bounding_box(geometry_dict: Dict) -> Dict:
        """
        Extract bounding box from geometry.
        
        Property 3: Bounding Box Containment
        For any boundary polygon, the extracted bounding box coordinates 
        SHALL fully contain all vertices of the polygon.
        
        Args:
            geometry_dict: GeoJSON geometry dictionary
            
        Returns:
            Dictionary with bounding box coordinates
        """
        try:
            geom = shape(geometry_dict)
            bounds = geom.bounds  # (minx, miny, maxx, maxy)
            
            return {
                'minLon': bounds[0],
                'minLat': bounds[1],
                'maxLon': bounds[2],
                'maxLat': bounds[3]
            }
        except Exception as e:
            logger.error(f"Error extracting bounding box: {str(e)}")
            raise ValueError(f"Failed to extract bounding box: {str(e)}")
