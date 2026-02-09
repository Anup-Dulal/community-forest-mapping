"""
Bounding box extractor module.
Extracts and validates bounding boxes from geometries.
"""

import logging
from typing import Dict, Tuple
from shapely.geometry import shape

logger = logging.getLogger(__name__)


class BoundingBoxExtractor:
    """Extracts bounding boxes from geometries."""

    @staticmethod
    def extract_bbox(geometry_dict: Dict) -> Dict:
        """
        Extract bounding box from geometry.
        
        Property 3: Bounding Box Containment
        For any boundary polygon, the extracted bounding box coordinates 
        SHALL fully contain all vertices of the polygon.
        
        Args:
            geometry_dict: GeoJSON geometry dictionary
            
        Returns:
            Dictionary with bounding box coordinates
            
        Raises:
            ValueError: If geometry is invalid
        """
        try:
            geom = shape(geometry_dict)
            
            if not geom.is_valid:
                raise ValueError("Invalid geometry")
            
            bounds = geom.bounds  # (minx, miny, maxx, maxy)
            
            bbox = {
                'minLon': float(bounds[0]),
                'minLat': float(bounds[1]),
                'maxLon': float(bounds[2]),
                'maxLat': float(bounds[3])
            }
            
            logger.info(f"Extracted bounding box: {bbox}")
            return bbox
            
        except Exception as e:
            logger.error(f"Error extracting bounding box: {str(e)}")
            raise ValueError(f"Failed to extract bounding box: {str(e)}")
    
    @staticmethod
    def validate_bbox_containment(geometry_dict: Dict, bbox: Dict) -> bool:
        """
        Validate that bounding box contains all geometry vertices.
        
        Args:
            geometry_dict: GeoJSON geometry dictionary
            bbox: Bounding box dictionary
            
        Returns:
            True if bbox contains all vertices, False otherwise
        """
        try:
            geom = shape(geometry_dict)
            
            # Get all coordinates
            if hasattr(geom, 'exterior'):
                coords = list(geom.exterior.coords)
            elif hasattr(geom, 'geoms'):
                coords = []
                for sub_geom in geom.geoms:
                    if hasattr(sub_geom, 'exterior'):
                        coords.extend(list(sub_geom.exterior.coords))
            else:
                coords = list(geom.coords)
            
            # Check if all coordinates are within bbox
            for lon, lat in coords:
                if not (bbox['minLon'] <= lon <= bbox['maxLon'] and 
                        bbox['minLat'] <= lat <= bbox['maxLat']):
                    logger.warning(f"Coordinate ({lon}, {lat}) outside bbox")
                    return False
            
            logger.info("Bounding box containment validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating bbox containment: {str(e)}")
            return False
    
    @staticmethod
    def expand_bbox(bbox: Dict, margin: float = 0.01) -> Dict:
        """
        Expand bounding box by a margin (useful for DEM download).
        
        Args:
            bbox: Bounding box dictionary
            margin: Expansion margin in degrees
            
        Returns:
            Expanded bounding box
        """
        return {
            'minLon': bbox['minLon'] - margin,
            'minLat': bbox['minLat'] - margin,
            'maxLon': bbox['maxLon'] + margin,
            'maxLat': bbox['maxLat'] + margin
        }
