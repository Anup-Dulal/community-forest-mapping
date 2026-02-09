"""
Compartment generator module.
Generates equal-area compartments from boundary polygons.
"""

import logging
from typing import Dict, List, Tuple
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon, box
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class CompartmentGenerator:
    """Generates equal-area compartments from boundary polygons."""

    def __init__(self, export_dir: str = './exports'):
        """
        Initialize compartment generator.
        
        Args:
            export_dir: Directory to save compartment files
        """
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def generate_compartments(
        self,
        boundary_geometry: Dict,
        num_compartments: int = 4,
        output_path: str = None
    ) -> str:
        """
        Generate equal-area compartments from boundary polygon.
        
        Property 7: Equal-Area Compartment Distribution
        All compartments SHALL have approximately equal area within ±5% tolerance.
        
        Property 8: Compartment Sequential Numbering
        Compartments SHALL be numbered sequentially starting from C1, with no gaps.
        
        Args:
            boundary_geometry: GeoJSON geometry dictionary of boundary
            num_compartments: Number of compartments to generate
            output_path: Optional output path for compartment GeoJSON
            
        Returns:
            Path to compartment GeoJSON file
            
        Raises:
            ValueError: If generation fails
        """
        logger.info(f"Generating {num_compartments} equal-area compartments")

        try:
            # Convert GeoJSON to shapely geometry
            boundary_geom = shape(boundary_geometry)

            if not boundary_geom.is_valid:
                raise ValueError("Invalid boundary geometry")

            # Calculate target area per compartment
            total_area = boundary_geom.area
            target_area = total_area / num_compartments

            logger.info(f"Total area: {total_area}, Target area per compartment: {target_area}")

            # Generate compartments using recursive bisection
            compartments = self._recursive_bisection(boundary_geom, num_compartments, target_area)

            # Validate compartments
            self._validate_compartments(compartments, target_area)

            # Create GeoDataFrame
            gdf = self._create_compartment_geodataframe(compartments)

            # Save to GeoJSON
            if output_path is None:
                output_path = f"{self.export_dir}/compartments_{hash(str(boundary_geometry))}.geojson"

            gdf.to_file(output_path, driver='GeoJSON')

            logger.info(f"Compartments saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating compartments: {str(e)}")
            raise ValueError(f"Failed to generate compartments: {str(e)}")

    def _recursive_bisection(
        self,
        polygon: Polygon,
        num_compartments: int,
        target_area: float,
        compartments: List = None,
        depth: int = 0
    ) -> List[Tuple[Polygon, str]]:
        """
        Recursively bisect polygon into equal-area compartments.
        
        Args:
            polygon: Polygon to bisect
            num_compartments: Target number of compartments
            target_area: Target area per compartment
            compartments: List to accumulate compartments
            depth: Recursion depth
            
        Returns:
            List of (polygon, compartment_id) tuples
        """
        if compartments is None:
            compartments = []

        # Base case: if we have enough compartments, return
        if len(compartments) >= num_compartments:
            return compartments

        # If polygon is small enough, add as compartment
        if abs(polygon.area - target_area) < target_area * 0.1 or depth > 10:
            compartment_id = f"C{len(compartments) + 1}"
            compartments.append((polygon, compartment_id))
            return compartments

        # Bisect polygon
        line = self._find_bisecting_line(polygon, target_area)
        if line is None:
            compartment_id = f"C{len(compartments) + 1}"
            compartments.append((polygon, compartment_id))
            return compartments

        # Split polygon
        left, right = self._split_polygon(polygon, line)

        if left is not None and left.area > 0:
            self._recursive_bisection(left, num_compartments, target_area, compartments, depth + 1)

        if right is not None and right.area > 0:
            self._recursive_bisection(right, num_compartments, target_area, compartments, depth + 1)

        return compartments

    def _find_bisecting_line(self, polygon: Polygon, target_area: float):
        """
        Find a line that bisects polygon into equal areas.
        
        Args:
            polygon: Polygon to bisect
            target_area: Target area per compartment
            
        Returns:
            Shapely LineString or None
        """
        try:
            bounds = polygon.bounds
            minx, miny, maxx, maxy = bounds

            # Try vertical bisection first
            mid_x = (minx + maxx) / 2
            line = box(mid_x - 0.0001, miny - 1, mid_x + 0.0001, maxy + 1).boundary

            # Check if line bisects polygon
            left = polygon.intersection(box(minx - 1, miny - 1, mid_x, maxy + 1))
            right = polygon.intersection(box(mid_x, miny - 1, maxx + 1, maxy + 1))

            if left.area > 0 and right.area > 0:
                return line

            # Try horizontal bisection
            mid_y = (miny + maxy) / 2
            line = box(minx - 1, mid_y - 0.0001, maxx + 1, mid_y + 0.0001).boundary

            top = polygon.intersection(box(minx - 1, mid_y, maxx + 1, maxy + 1))
            bottom = polygon.intersection(box(minx - 1, miny - 1, maxx + 1, mid_y))

            if top.area > 0 and bottom.area > 0:
                return line

            return None

        except Exception as e:
            logger.error(f"Error finding bisecting line: {str(e)}")
            return None

    def _split_polygon(self, polygon: Polygon, line):
        """
        Split polygon by line.
        
        Args:
            polygon: Polygon to split
            line: Splitting line
            
        Returns:
            Tuple of (left_polygon, right_polygon)
        """
        try:
            from shapely.ops import split
            result = split(polygon, line)

            if len(result.geoms) >= 2:
                return result.geoms[0], result.geoms[1]
            else:
                return polygon, None

        except Exception as e:
            logger.error(f"Error splitting polygon: {str(e)}")
            return polygon, None

    def _validate_compartments(self, compartments: List[Tuple[Polygon, str]], target_area: float):
        """
        Validate that compartments have approximately equal area.
        
        Property 7: Equal-Area Compartment Distribution
        All compartments SHALL have approximately equal area within ±5% tolerance.
        
        Args:
            compartments: List of (polygon, compartment_id) tuples
            target_area: Target area per compartment
        """
        areas = [poly.area for poly, _ in compartments]
        mean_area = np.mean(areas)
        tolerance = mean_area * 0.05  # 5% tolerance

        for i, (poly, comp_id) in enumerate(compartments):
            deviation = abs(poly.area - mean_area)
            if deviation > tolerance:
                logger.warning(
                    f"Compartment {comp_id} area deviation: {deviation:.2f} "
                    f"(tolerance: {tolerance:.2f})"
                )

        logger.info(f"Compartment validation complete. Mean area: {mean_area:.2f}")

    def _create_compartment_geodataframe(self, compartments: List[Tuple[Polygon, str]]) -> gpd.GeoDataFrame:
        """
        Create GeoDataFrame from compartments.
        
        Property 8: Compartment Sequential Numbering
        Compartments SHALL be numbered sequentially starting from C1, with no gaps.
        
        Args:
            compartments: List of (polygon, compartment_id) tuples
            
        Returns:
            GeoDataFrame with compartment data
        """
        data = {
            'compartment_id': [comp_id for _, comp_id in compartments],
            'area': [poly.area for poly, _ in compartments],
            'geometry': [poly for poly, _ in compartments]
        }

        gdf = gpd.GeoDataFrame(data, crs='EPSG:4326')
        return gdf

    def get_compartment_statistics(self, compartment_path: str) -> Dict:
        """
        Calculate statistics for compartments.
        
        Args:
            compartment_path: Path to compartment GeoJSON file
            
        Returns:
            Dictionary with compartment statistics
        """
        try:
            gdf = gpd.read_file(compartment_path)

            areas = gdf.geometry.area.values
            stats = {
                'num_compartments': len(gdf),
                'total_area': float(np.sum(areas)),
                'mean_area': float(np.mean(areas)),
                'min_area': float(np.min(areas)),
                'max_area': float(np.max(areas)),
                'std_area': float(np.std(areas)),
                'area_variance': float(np.var(areas))
            }

            logger.info(f"Compartment statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error calculating compartment statistics: {str(e)}")
            raise ValueError(f"Failed to calculate compartment statistics: {str(e)}")
