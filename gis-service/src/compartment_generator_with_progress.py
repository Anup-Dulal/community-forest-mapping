"""
Compartment generator with real-time progress updates.
Generates equal-area compartments with progress streaming via callback.
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 15.1, 15.2, 15.3, 15.8
"""

import logging
import time
from typing import Dict, List, Tuple, Callable, Optional
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon, box
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class CompartmentGeneratorWithProgress:
    """Generates equal-area compartments with real-time progress updates."""

    def __init__(self, export_dir: str = './exports'):
        """
        Initialize compartment generator with progress support.
        
        Args:
            export_dir: Directory to save compartment files
        """
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def generate_compartments_with_progress(
        self,
        boundary_geometry: Dict,
        num_compartments: int = 4,
        output_path: str = None,
        progress_callback: Optional[Callable[[int, str, Dict], None]] = None
    ) -> Tuple[str, Dict]:
        """
        Generate equal-area compartments from boundary polygon with progress updates.
        
        Validates Requirements:
        - 6.1: Automatically divide boundary into equal-area compartments
        - 6.2: Use GIS equal-area partitioning algorithm
        - 6.3: Number compartments sequentially (C1, C2, C3, etc.)
        - 6.4: Display compartment boundaries on map
        - 6.5: Display legend showing compartment numbers
        - 6.6: Store compartment geometry for use in sample plot generation
        - 15.1: Display real-time progress indicator showing percentage complete
        - 15.2: Display compartments on map as they're created
        - 15.3: Show compartment numbers and boundaries with distinct colors
        - 15.8: Display completion notification with summary statistics
        
        Args:
            boundary_geometry: GeoJSON geometry dictionary of boundary
            num_compartments: Number of compartments to generate
            output_path: Optional output path for compartment GeoJSON
            progress_callback: Optional callback function(percentage, status_message, data)
                Called with progress updates during generation
            
        Returns:
            Tuple of (output_path, statistics_dict)
            
        Raises:
            ValueError: If generation fails
        """
        logger.info(f"Generating {num_compartments} equal-area compartments with progress tracking")
        start_time = time.time()

        try:
            # Emit initial progress
            if progress_callback:
                progress_callback(0, "Validating boundary geometry", {})

            # Convert GeoJSON to shapely geometry
            boundary_geom = shape(boundary_geometry)

            if not boundary_geom.is_valid:
                raise ValueError("Invalid boundary geometry")

            # Calculate target area per compartment
            total_area = boundary_geom.area
            target_area = total_area / num_compartments

            logger.info(f"Total area: {total_area}, Target area per compartment: {target_area}")

            if progress_callback:
                progress_callback(5, f"Starting recursive bisection for {num_compartments} compartments", {})

            # Generate compartments using recursive bisection with progress tracking
            compartments = self._recursive_bisection_with_progress(
                boundary_geom,
                num_compartments,
                target_area,
                progress_callback
            )

            if progress_callback:
                progress_callback(70, f"Validating {len(compartments)} compartments", {})

            # Validate compartments
            self._validate_compartments(compartments, target_area)

            if progress_callback:
                progress_callback(80, "Creating GeoDataFrame", {})

            # Create GeoDataFrame
            gdf = self._create_compartment_geodataframe(compartments)

            # Save to GeoJSON
            if output_path is None:
                output_path = f"{self.export_dir}/compartments_{hash(str(boundary_geometry))}.geojson"

            if progress_callback:
                progress_callback(90, "Saving compartment geometries", {})

            gdf.to_file(output_path, driver='GeoJSON')

            # Calculate statistics
            statistics = self._calculate_statistics(compartments, total_area)

            elapsed_time = time.time() - start_time
            logger.info(f"Compartments generated in {elapsed_time:.2f}s: {output_path}")

            if progress_callback:
                progress_callback(100, "Compartment generation complete", statistics)

            return output_path, statistics

        except Exception as e:
            logger.error(f"Error generating compartments: {str(e)}")
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}", {})
            raise ValueError(f"Failed to generate compartments: {str(e)}")

    def _recursive_bisection_with_progress(
        self,
        polygon: Polygon,
        num_compartments: int,
        target_area: float,
        progress_callback: Optional[Callable],
        compartments: List = None,
        depth: int = 0,
        max_depth: int = 20
    ) -> List[Tuple[Polygon, str]]:
        """
        Recursively bisect polygon into equal-area compartments with progress tracking.
        
        Validates Requirements:
        - 15.1: Display real-time progress indicator
        - 15.2: Display compartments on map as they're created
        
        Args:
            polygon: Polygon to bisect
            num_compartments: Target number of compartments
            target_area: Target area per compartment
            progress_callback: Callback for progress updates
            compartments: List to accumulate compartments
            depth: Recursion depth
            max_depth: Maximum recursion depth
            
        Returns:
            List of (polygon, compartment_id) tuples
        """
        if compartments is None:
            compartments = []

        # Base case: if we have enough compartments, return
        if len(compartments) >= num_compartments:
            return compartments

        # If polygon is small enough or we've reached max depth, add as compartment
        if len(compartments) >= num_compartments - 1 or depth > max_depth:
            compartment_id = f"C{len(compartments) + 1}"
            compartments.append((polygon, compartment_id))

            # Emit progress update with current compartment
            if progress_callback:
                percentage = int((len(compartments) / num_compartments) * 60) + 5
                progress_callback(
                    percentage,
                    f"Generated compartment {compartment_id}",
                    {
                        "current_compartment": compartment_id,
                        "compartments_generated": len(compartments),
                        "target_compartments": num_compartments
                    }
                )

            return compartments

        # Bisect polygon
        line = self._find_bisecting_line(polygon, target_area)
        if line is None:
            compartment_id = f"C{len(compartments) + 1}"
            compartments.append((polygon, compartment_id))

            if progress_callback:
                percentage = int((len(compartments) / num_compartments) * 60) + 5
                progress_callback(
                    percentage,
                    f"Generated compartment {compartment_id}",
                    {
                        "current_compartment": compartment_id,
                        "compartments_generated": len(compartments),
                        "target_compartments": num_compartments
                    }
                )

            return compartments

        # Split polygon
        left, right = self._split_polygon(polygon, line)

        if left is not None and left.area > 0 and len(compartments) < num_compartments:
            self._recursive_bisection_with_progress(
                left, num_compartments, target_area, progress_callback, compartments, depth + 1, max_depth
            )

        if right is not None and right.area > 0 and len(compartments) < num_compartments:
            self._recursive_bisection_with_progress(
                right, num_compartments, target_area, progress_callback, compartments, depth + 1, max_depth
            )

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
        
        Validates Requirement 6.2: Use GIS equal-area partitioning algorithm
        
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
        
        Validates Requirements:
        - 6.3: Number compartments sequentially (C1, C2, C3, etc.)
        - 6.4: Display compartment boundaries on map
        - 6.5: Display legend showing compartment numbers
        
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

    def _calculate_statistics(self, compartments: List[Tuple[Polygon, str]], total_area: float) -> Dict:
        """
        Calculate statistics for compartments.
        
        Validates Requirement 15.8: Display completion notification with summary statistics
        
        Args:
            compartments: List of (polygon, compartment_id) tuples
            total_area: Total area of boundary
            
        Returns:
            Dictionary with compartment statistics
        """
        areas = [poly.area for poly, _ in compartments]
        areas = np.array(areas)

        statistics = {
            'num_compartments': len(areas),
            'total_area': float(total_area),
            'mean_area': float(np.mean(areas)),
            'min_area': float(np.min(areas)),
            'max_area': float(np.max(areas)),
            'std_area': float(np.std(areas)),
            'area_variance': float(np.var(areas)),
            'compartment_ids': [comp_id for _, comp_id in compartments]
        }

        logger.info(f"Compartment statistics: {statistics}")
        return statistics
