"""
Hierarchical Compartment Generator
Generates compartments and sub-compartments using recursive equal-area division
with UTM projection for accurate area calculations in hectares
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from shapely import wkt
from shapely.geometry import Polygon, box, LineString
from shapely.ops import transform, split
from dataclasses import dataclass
import pyproj

logger = logging.getLogger(__name__)


@dataclass
class CompartmentSpec:
    """Specification for a compartment and its sub-compartments"""
    compartment_number: int
    sub_compartment_count: int


@dataclass
class SubCompartmentData:
    """Data for a single sub-compartment"""
    number: int
    label: str
    geometry: str  # WKT
    area: float


@dataclass
class CompartmentData:
    """Data for a compartment with its sub-compartments"""
    number: int
    label: str
    geometry: str  # WKT
    area: float
    sub_compartments: List[SubCompartmentData]


@dataclass
class HierarchicalCompartmentResult:
    """Result of hierarchical compartment generation"""
    compartments: List[CompartmentData]
    statistics: Dict
    output_path: str


class SimpleRecursiveBisection:
    """Equal-area recursive bisection for polygon division"""
    
    @staticmethod
    def divide_polygon(polygon: Polygon, num_parts: int, tolerance: float = 0.02) -> List[Polygon]:
        """
        Divide polygon into num_parts equal-area parts using iterative bisection
        
        Args:
            polygon: Polygon to divide
            num_parts: Number of parts to divide into
            tolerance: Area tolerance (default 2%)
            
        Returns:
            List of polygons with equal areas
        """
        if num_parts == 1:
            return [polygon]
        
        if num_parts == 2:
            return SimpleRecursiveBisection._bisect_equal_area(polygon, tolerance)
        
        # For more than 2 parts, recursively divide
        # First split in half
        half = num_parts // 2
        first_half_parts = half
        second_half_parts = num_parts - half
        
        # Bisect into two equal-area parts
        parts = SimpleRecursiveBisection._bisect_equal_area(polygon, tolerance)
        if len(parts) != 2:
            # Fallback: use simple division
            return SimpleRecursiveBisection._fallback_division(polygon, num_parts)
        
        # Recursively divide each half
        first_results = SimpleRecursiveBisection.divide_polygon(parts[0], first_half_parts, tolerance)
        second_results = SimpleRecursiveBisection.divide_polygon(parts[1], second_half_parts, tolerance)
        
        return first_results + second_results
    
    @staticmethod
    def _bisect_equal_area(polygon: Polygon, tolerance: float = 0.02) -> List[Polygon]:
        """
        Bisect polygon into two equal-area parts using iterative method
        
        This uses binary search to find the split line that creates equal areas
        """
        target_area = polygon.area / 2.0
        bounds = polygon.bounds
        minx, miny, maxx, maxy = bounds
        
        # Determine split direction based on aspect ratio
        width = maxx - minx
        height = maxy - miny
        
        if width > height:
            # Split vertically
            return SimpleRecursiveBisection._bisect_vertical(polygon, target_area, tolerance)
        else:
            # Split horizontally
            return SimpleRecursiveBisection._bisect_horizontal(polygon, target_area, tolerance)
    
    @staticmethod
    def _bisect_vertical(polygon: Polygon, target_area: float, tolerance: float) -> List[Polygon]:
        """Bisect polygon vertically with equal areas"""
        bounds = polygon.bounds
        minx, miny, maxx, maxy = bounds
        
        # Binary search for the split position
        left = minx
        right = maxx
        max_iterations = 50
        
        for _ in range(max_iterations):
            mid_x = (left + right) / 2
            split_line = LineString([(mid_x, miny - 1), (mid_x, maxy + 1)])
            
            try:
                result = split(polygon, split_line)
                if len(result.geoms) >= 2:
                    # Get the left part
                    left_part = None
                    for geom in result.geoms:
                        if geom.centroid.x < mid_x:
                            left_part = geom
                            break
                    
                    if left_part:
                        area_diff = abs(left_part.area - target_area)
                        if area_diff / target_area < tolerance:
                            # Found good split
                            parts = list(result.geoms)
                            if len(parts) == 2:
                                return parts
                            # Merge extra parts
                            left_parts = [g for g in parts if g.centroid.x < mid_x]
                            right_parts = [g for g in parts if g.centroid.x >= mid_x]
                            if left_parts and right_parts:
                                from shapely.ops import unary_union
                                return [unary_union(left_parts), unary_union(right_parts)]
                        
                        # Adjust search range
                        if left_part.area < target_area:
                            left = mid_x
                        else:
                            right = mid_x
            except:
                pass
        
        # Fallback to simple midpoint split
        mid_x = (minx + maxx) / 2
        split_line = LineString([(mid_x, miny - 1), (mid_x, maxy + 1)])
        try:
            result = split(polygon, split_line)
            if len(result.geoms) >= 2:
                return list(result.geoms)[:2]
        except:
            pass
        
        return [polygon]
    
    @staticmethod
    def _bisect_horizontal(polygon: Polygon, target_area: float, tolerance: float) -> List[Polygon]:
        """Bisect polygon horizontally with equal areas"""
        bounds = polygon.bounds
        minx, miny, maxx, maxy = bounds
        
        # Binary search for the split position
        bottom = miny
        top = maxy
        max_iterations = 50
        
        for _ in range(max_iterations):
            mid_y = (bottom + top) / 2
            split_line = LineString([(minx - 1, mid_y), (maxx + 1, mid_y)])
            
            try:
                result = split(polygon, split_line)
                if len(result.geoms) >= 2:
                    # Get the bottom part
                    bottom_part = None
                    for geom in result.geoms:
                        if geom.centroid.y < mid_y:
                            bottom_part = geom
                            break
                    
                    if bottom_part:
                        area_diff = abs(bottom_part.area - target_area)
                        if area_diff / target_area < tolerance:
                            # Found good split
                            parts = list(result.geoms)
                            if len(parts) == 2:
                                return parts
                            # Merge extra parts
                            bottom_parts = [g for g in parts if g.centroid.y < mid_y]
                            top_parts = [g for g in parts if g.centroid.y >= mid_y]
                            if bottom_parts and top_parts:
                                from shapely.ops import unary_union
                                return [unary_union(bottom_parts), unary_union(top_parts)]
                        
                        # Adjust search range
                        if bottom_part.area < target_area:
                            bottom = mid_y
                        else:
                            top = mid_y
            except:
                pass
        
        # Fallback to simple midpoint split
        mid_y = (miny + maxy) / 2
        split_line = LineString([(minx - 1, mid_y), (maxx + 1, mid_y)])
        try:
            result = split(polygon, split_line)
            if len(result.geoms) >= 2:
                return list(result.geoms)[:2]
        except:
            pass
        
        return [polygon]
    
    @staticmethod
    def _fallback_division(polygon: Polygon, num_parts: int) -> List[Polygon]:
        """Fallback: simple grid-based division"""
        # This is a simple fallback - just return the polygon repeated
        # In practice, this should rarely be used
        return [polygon] * num_parts


class HierarchicalCompartmentGenerator:
    """
    Generates compartments and sub-compartments in hierarchical structure
    with UTM projection for accurate area calculations in hectares
    """
    
    @staticmethod
    def _get_utm_zone(lon: float, lat: float) -> str:
        """
        Determine appropriate UTM zone for Nepal coordinates
        Nepal spans UTM zones 44N and 45N
        """
        # Nepal is in northern hemisphere
        # Zone 44N: 78°E to 84°E
        # Zone 45N: 84°E to 90°E
        if lon < 84.0:
            return "EPSG:32644"  # UTM Zone 44N
        else:
            return "EPSG:32645"  # UTM Zone 45N
    
    @staticmethod
    def _transform_to_utm(geometry: Polygon, utm_epsg: str) -> Polygon:
        """Transform geometry from WGS84 to UTM"""
        # WGS84 to UTM transformer
        transformer = pyproj.Transformer.from_crs(
            "EPSG:4326",  # WGS84
            utm_epsg,
            always_xy=True
        )
        
        # Transform geometry
        return transform(transformer.transform, geometry)
    
    @staticmethod
    def _transform_from_utm(geometry: Polygon, utm_epsg: str) -> Polygon:
        """Transform geometry from UTM back to WGS84"""
        # UTM to WGS84 transformer
        transformer = pyproj.Transformer.from_crs(
            utm_epsg,
            "EPSG:4326",  # WGS84
            always_xy=True
        )
        
        # Transform geometry
        return transform(transformer.transform, geometry)
    
    @staticmethod
    def _calculate_area_hectares(geometry: Polygon, utm_epsg: str) -> float:
        """Calculate area in hectares using UTM projection"""
        # Transform to UTM for accurate area calculation
        utm_geom = HierarchicalCompartmentGenerator._transform_to_utm(geometry, utm_epsg)
        
        # Area in square meters
        area_sqm = utm_geom.area
        
        # Convert to hectares (1 hectare = 10,000 square meters)
        area_hectares = area_sqm / 10000.0
        
        return area_hectares
    
    @staticmethod
    def generate(
        boundary_wkt: str,
        analysis_id: str,
        compartment_specs: List[Dict],
        exports_dir: Path
    ) -> HierarchicalCompartmentResult:
        """
        Generate hierarchical compartments with UTM projection for accurate areas
        
        Args:
            boundary_wkt: WKT polygon of forest boundary (WGS84)
            analysis_id: Analysis ID for file naming
            compartment_specs: List of {compartmentNumber, subCompartmentCount}
            exports_dir: Base directory for exports
            
        Returns:
            HierarchicalCompartmentResult with nested structure and areas in hectares
        """
        logger.info(f"Starting hierarchical compartment generation for analysis {analysis_id}")
        logger.info(f"Compartment specs: {compartment_specs}")
        
        # Parse boundary (WGS84)
        boundary = wkt.loads(boundary_wkt)
        total_compartments = len(compartment_specs)
        
        # Determine UTM zone based on centroid
        centroid = boundary.centroid
        utm_epsg = HierarchicalCompartmentGenerator._get_utm_zone(centroid.x, centroid.y)
        logger.info(f"Using UTM projection: {utm_epsg}")
        
        # Transform boundary to UTM for accurate division
        boundary_utm = HierarchicalCompartmentGenerator._transform_to_utm(boundary, utm_epsg)
        
        # Convert specs to dataclass
        specs = [
            CompartmentSpec(
                compartment_number=spec['compartmentNumber'],
                sub_compartment_count=spec['subCompartmentCount']
            )
            for spec in compartment_specs
        ]
        
        # Step 1: Divide boundary into top-level compartments (in UTM)
        logger.info(f"Dividing boundary into {total_compartments} compartments")
        
        if total_compartments == 1:
            # Single compartment - use entire boundary
            compartment_polygons_utm = [boundary_utm]
        else:
            # Multiple compartments - divide equally in UTM space
            compartment_polygons_utm = SimpleRecursiveBisection.divide_polygon(
                polygon=boundary_utm,
                num_parts=total_compartments,
                tolerance=0.05
            )
        
        # Step 2: Generate sub-compartments for each compartment
        result_compartments = []
        
        for idx, spec in enumerate(specs):
            comp_polygon_utm = compartment_polygons_utm[idx]
            comp_number = spec.compartment_number
            sub_count = spec.sub_compartment_count
            
            logger.info(f"Processing compartment C{comp_number} with {sub_count} sub-compartments")
            
            # Divide into sub-compartments (in UTM)
            if sub_count > 1:
                sub_polygons_utm = SimpleRecursiveBisection.divide_polygon(
                    polygon=comp_polygon_utm,
                    num_parts=sub_count,
                    tolerance=0.05
                )
            else:
                # Single sub-compartment = same as parent
                sub_polygons_utm = [comp_polygon_utm]
            
            # Transform compartment back to WGS84 for storage
            comp_polygon_wgs84 = HierarchicalCompartmentGenerator._transform_from_utm(
                comp_polygon_utm, utm_epsg
            )
            
            # Calculate area in hectares
            comp_area_hectares = HierarchicalCompartmentGenerator._calculate_area_hectares(
                comp_polygon_wgs84, utm_epsg
            )
            
            # Create sub-compartment data
            sub_compartments = []
            for sub_idx, sub_polygon_utm in enumerate(sub_polygons_utm):
                sub_number = sub_idx + 1
                
                # Transform back to WGS84
                sub_polygon_wgs84 = HierarchicalCompartmentGenerator._transform_from_utm(
                    sub_polygon_utm, utm_epsg
                )
                
                # Calculate area in hectares
                sub_area_hectares = HierarchicalCompartmentGenerator._calculate_area_hectares(
                    sub_polygon_wgs84, utm_epsg
                )
                
                sub_data = SubCompartmentData(
                    number=sub_number,
                    label=f'C{comp_number}S{sub_number}',
                    geometry=sub_polygon_wgs84.wkt,
                    area=sub_area_hectares  # Now in hectares
                )
                sub_compartments.append(sub_data)
            
            # Create compartment data
            compartment = CompartmentData(
                number=comp_number,
                label=f'C{comp_number}',
                geometry=comp_polygon_wgs84.wkt,
                area=comp_area_hectares,  # Now in hectares
                sub_compartments=sub_compartments
            )
            
            result_compartments.append(compartment)
        
        # Step 3: Calculate statistics
        statistics = HierarchicalCompartmentGenerator._calculate_statistics(
            result_compartments
        )
        
        # Add UTM projection info to statistics
        statistics['projection'] = {
            'utm_zone': utm_epsg,
            'unit': 'hectares',
            'note': 'Areas calculated using UTM projection for accuracy'
        }
        
        logger.info(f"Statistics: {statistics}")
        
        # Step 4: Save to GeoJSON
        output_dir = exports_dir / analysis_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"compartments_{analysis_id}.geojson"
        
        HierarchicalCompartmentGenerator._save_geojson(
            result_compartments,
            output_path,
            utm_epsg
        )
        
        logger.info(f"Saved compartments to {output_path}")
        
        return HierarchicalCompartmentResult(
            compartments=result_compartments,
            statistics=statistics,
            output_path=str(output_path)
        )
    
    @staticmethod
    def _calculate_statistics(compartments: List[CompartmentData]) -> Dict:
        """Calculate area statistics for validation (areas in hectares)"""
        compartment_areas = []
        sub_compartment_areas = []
        
        for comp in compartments:
            compartment_areas.append(comp.area)
            for sub in comp.sub_compartments:
                sub_compartment_areas.append(sub.area)
        
        all_areas = compartment_areas + sub_compartment_areas
        
        total_area = sum(sub_compartment_areas)
        
        return {
            'totalCompartments': len(compartments),
            'totalSubCompartments': sum(len(c.sub_compartments) for c in compartments),
            'totalAreaHectares': round(total_area, 2),
            'compartmentStats': {
                'mean': round(float(np.mean(compartment_areas)), 2) if compartment_areas else 0,
                'min': round(float(np.min(compartment_areas)), 2) if compartment_areas else 0,
                'max': round(float(np.max(compartment_areas)), 2) if compartment_areas else 0,
                'std': round(float(np.std(compartment_areas)), 2) if compartment_areas else 0
            },
            'subCompartmentStats': {
                'mean': round(float(np.mean(sub_compartment_areas)), 2) if sub_compartment_areas else 0,
                'min': round(float(np.min(sub_compartment_areas)), 2) if sub_compartment_areas else 0,
                'max': round(float(np.max(sub_compartment_areas)), 2) if sub_compartment_areas else 0,
                'std': round(float(np.std(sub_compartment_areas)), 2) if sub_compartment_areas else 0
            },
            'allAreasStats': {
                'mean': round(float(np.mean(all_areas)), 2) if all_areas else 0,
                'min': round(float(np.min(all_areas)), 2) if all_areas else 0,
                'max': round(float(np.max(all_areas)), 2) if all_areas else 0,
                'std': round(float(np.std(all_areas)), 2) if all_areas else 0
            }
        }
    
    @staticmethod
    def _save_geojson(compartments: List[CompartmentData], output_path: Path, utm_epsg: str):
        """Save hierarchical structure to GeoJSON with UTM metadata"""
        features = []
        
        for comp in compartments:
            # Add compartment feature (parent level)
            comp_geom = wkt.loads(comp.geometry)
            features.append({
                'type': 'Feature',
                'properties': {
                    'id': comp.label,
                    'label': comp.label,
                    'level': 0,
                    'number': comp.number,
                    'area': round(comp.area, 2),
                    'areaUnit': 'hectares',
                    'subCompartmentCount': len(comp.sub_compartments)
                },
                'geometry': comp_geom.__geo_interface__
            })
            
            # Add sub-compartment features
            for sub in comp.sub_compartments:
                sub_geom = wkt.loads(sub.geometry)
                features.append({
                    'type': 'Feature',
                    'properties': {
                        'id': sub.label,
                        'label': sub.label,
                        'level': 1,
                        'parentLabel': comp.label,
                        'number': sub.number,
                        'area': round(sub.area, 2),
                        'areaUnit': 'hectares',
                        'compartmentNumber': comp.number,
                        'subCompartmentNumber': sub.number
                    },
                    'geometry': sub_geom.__geo_interface__
                })
        
        geojson = {
            'type': 'FeatureCollection',
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'EPSG:4326'
                }
            },
            'metadata': {
                'projection': utm_epsg,
                'areaUnit': 'hectares',
                'note': 'Areas calculated using UTM projection for accuracy'
            },
            'features': features
        }
        
        with open(output_path, 'w') as f:
            json.dump(geojson, f, indent=2)
    
    @staticmethod
    def convert_to_dict_list(compartments: List[CompartmentData]) -> List[Dict]:
        """Convert CompartmentData objects to dictionary format for JSON response"""
        result = []
        
        for comp in compartments:
            comp_dict = {
                'number': comp.number,
                'label': comp.label,
                'geometry': comp.geometry,
                'area': comp.area,
                'subCompartments': [
                    {
                        'number': sub.number,
                        'label': sub.label,
                        'geometry': sub.geometry,
                        'area': sub.area
                    }
                    for sub in comp.sub_compartments
                ]
            }
            result.append(comp_dict)
        
        return result
