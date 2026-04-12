"""
Hierarchical Sample Plot Generator for forest inventory.
Generates sample plots with 2% sampling intensity and minimum 5 plots per SUB-COMPARTMENT.
Works with hierarchical compartment/sub-compartment structure.
"""

import json
import logging
import random
from typing import Dict, List
from shapely.geometry import Point, shape, Polygon
from pathlib import Path

logger = logging.getLogger(__name__)


class HierarchicalSamplePlotGenerator:
    """Generates sample plots for sub-compartments with specified sampling intensity."""

    def __init__(self, export_dir: str):
        """
        Initialize the hierarchical sample plot generator.
        
        Args:
            export_dir: Directory to store generated sample plot files
        """
        self.export_dir = export_dir
        self.plot_counter = 0

    def generate_sample_plots(
        self,
        compartment_geometry_path: str,
        analysis_id: str,
        sampling_intensity: float = 0.02,
        min_plots_per_subcompartment: int = 5,
        distribution_method: str = "systematic"
    ) -> str:
        """
        Generate sample plots for sub-compartments.
        
        Args:
            compartment_geometry_path: Path to compartment GeoJSON file (with hierarchical structure)
            analysis_id: Analysis ID for output file naming
            sampling_intensity: Sampling intensity as fraction (default 0.02 = 2%)
            min_plots_per_subcompartment: Minimum plots per SUB-COMPARTMENT (default 5)
            distribution_method: "systematic" or "random" point distribution
            
        Returns:
            Path to generated sample plot GeoJSON file
            
        Raises:
            ValueError: If compartment file is invalid or generation fails
        """
        try:
            logger.info(f"Generating sample plots for analysis: {analysis_id}")
            logger.info(f"Sampling intensity: {sampling_intensity}, Min plots per sub-compartment: {min_plots_per_subcompartment}")
            
            # Load compartment geometries from GeoJSON
            with open(compartment_geometry_path, 'r') as f:
                geojson_data = json.load(f)
            
            features = geojson_data.get('features', [])
            if not features:
                raise ValueError("Compartment file is empty")
            
            # Filter to get only sub-compartments (level = 1)
            sub_compartments = [f for f in features if f.get('properties', {}).get('level') == 1]
            
            if not sub_compartments:
                logger.warning("No sub-compartments found, using all features")
                sub_compartments = features
            
            logger.info(f"Found {len(sub_compartments)} sub-compartments")
            
            # Generate sample plots
            sample_plots = []
            self.plot_counter = 0
            
            for feature in sub_compartments:
                props = feature.get('properties', {})
                sub_compartment_label = props.get('label', props.get('id', f'C1S{len(sample_plots)+1}'))
                parent_label = props.get('parentLabel', sub_compartment_label.split('S')[0] if 'S' in sub_compartment_label else 'C1')
                
                geometry = shape(feature['geometry'])
                
                # Calculate number of plots for this sub-compartment
                area = geometry.area  # Area in square degrees or meters depending on CRS
                num_plots = max(
                    min_plots_per_subcompartment,
                    int(round(area * sampling_intensity * 10000))  # Adjust for area units
                )
                
                logger.info(f"Generating {num_plots} plots for {sub_compartment_label} (area: {area:.6f})")
                
                # Generate plots for this sub-compartment
                plots = self._generate_plots_for_subcompartment(
                    geometry,
                    sub_compartment_label,
                    parent_label,
                    num_plots,
                    distribution_method
                )
                sample_plots.extend(plots)
            
            # Create GeoJSON output
            output_features = []
            for plot in sample_plots:
                output_features.append({
                    'type': 'Feature',
                    'properties': {
                        'plot_id': plot['plot_id'],
                        'compartment_label': plot['compartment_label'],
                        'subcompartment_label': plot['subcompartment_label'],
                        'latitude': plot['latitude'],
                        'longitude': plot['longitude']
                    },
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [plot['geometry'].x, plot['geometry'].y]
                    }
                })
            
            output_geojson = {
                'type': 'FeatureCollection',
                'features': output_features
            }
            
            # Save to GeoJSON
            output_dir = Path(self.export_dir) / analysis_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"sample_plots_{analysis_id}.geojson"
            
            with open(output_path, 'w') as f:
                json.dump(output_geojson, f, indent=2)
            
            logger.info(f"Generated {len(sample_plots)} sample plots across {len(sub_compartments)} sub-compartments")
            logger.info(f"Saved to: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating sample plots: {str(e)}")
            raise ValueError(f"Failed to generate sample plots: {str(e)}")

    def _generate_plots_for_subcompartment(
        self,
        geometry: Polygon,
        subcompartment_label: str,
        compartment_label: str,
        num_plots: int,
        distribution_method: str
    ) -> List[Dict]:
        """
        Generate sample plots for a single sub-compartment.
        
        Args:
            geometry: Shapely Polygon for the sub-compartment
            subcompartment_label: Label of the sub-compartment (e.g., "C1S3")
            compartment_label: Label of the parent compartment (e.g., "C1")
            num_plots: Number of plots to generate
            distribution_method: "systematic" or "random"
            
        Returns:
            List of sample plot dictionaries with geometry
        """
        if distribution_method == "systematic":
            return self._generate_systematic_plots(
                geometry,
                subcompartment_label,
                compartment_label,
                num_plots
            )
        else:  # random
            return self._generate_random_plots(
                geometry,
                subcompartment_label,
                compartment_label,
                num_plots
            )

    def _generate_systematic_plots(
        self,
        geometry: Polygon,
        subcompartment_label: str,
        compartment_label: str,
        num_plots: int
    ) -> List[Dict]:
        """
        Generate systematically distributed sample plots using grid method.
        
        Args:
            geometry: Shapely Polygon for the sub-compartment
            subcompartment_label: Label of the sub-compartment
            compartment_label: Label of the parent compartment
            num_plots: Number of plots to generate
            
        Returns:
            List of sample plot dictionaries
        """
        plots = []
        
        # Get bounding box
        minx, miny, maxx, maxy = geometry.bounds
        
        # Calculate grid spacing
        grid_size = int((num_plots ** 0.5) + 1)
        x_step = (maxx - minx) / grid_size
        y_step = (maxy - miny) / grid_size
        
        # Generate grid points
        for i in range(grid_size):
            for j in range(grid_size):
                if len(plots) >= num_plots:
                    break
                
                x = minx + (i + 0.5) * x_step
                y = miny + (j + 0.5) * y_step
                
                point = Point(x, y)
                
                # Check if point is within sub-compartment
                if geometry.contains(point):
                    self.plot_counter += 1
                    plot_id = f"SP-{self.plot_counter:03d}"
                    
                    plots.append({
                        'plot_id': plot_id,
                        'compartment_label': compartment_label,
                        'subcompartment_label': subcompartment_label,
                        'geometry': point,
                        'latitude': y,
                        'longitude': x
                    })
            
            if len(plots) >= num_plots:
                break
        
        # If we didn't get enough plots with grid method, fill with random
        if len(plots) < num_plots:
            logger.warning(f"Grid method only generated {len(plots)}/{num_plots} plots for {subcompartment_label}, filling with random")
            additional_plots = self._generate_random_plots(
                geometry,
                subcompartment_label,
                compartment_label,
                num_plots - len(plots)
            )
            plots.extend(additional_plots)
        
        return plots

    def _generate_random_plots(
        self,
        geometry: Polygon,
        subcompartment_label: str,
        compartment_label: str,
        num_plots: int
    ) -> List[Dict]:
        """
        Generate randomly distributed sample plots.
        
        Args:
            geometry: Shapely Polygon for the sub-compartment
            subcompartment_label: Label of the sub-compartment
            compartment_label: Label of the parent compartment
            num_plots: Number of plots to generate
            
        Returns:
            List of sample plot dictionaries
        """
        plots = []
        
        # Get bounding box
        minx, miny, maxx, maxy = geometry.bounds
        
        # Generate random points until we have enough valid ones
        max_attempts = num_plots * 20  # Increased attempts for small polygons
        attempts = 0
        
        while len(plots) < num_plots and attempts < max_attempts:
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            
            point = Point(x, y)
            
            # Check if point is within sub-compartment
            if geometry.contains(point):
                self.plot_counter += 1
                plot_id = f"SP-{self.plot_counter:03d}"
                
                plots.append({
                    'plot_id': plot_id,
                    'compartment_label': compartment_label,
                    'subcompartment_label': subcompartment_label,
                    'geometry': point,
                    'latitude': y,
                    'longitude': x
                })
            
            attempts += 1
        
        if len(plots) < num_plots:
            logger.warning(
                f"Could not generate {num_plots} plots for {subcompartment_label}. "
                f"Generated {len(plots)} plots instead after {attempts} attempts."
            )
        
        return plots

    def get_sample_plot_statistics(self, sample_plot_path: str) -> Dict:
        """
        Calculate statistics for generated sample plots.
        
        Args:
            sample_plot_path: Path to sample plot GeoJSON file
            
        Returns:
            Dictionary with statistics
        """
        try:
            # Read GeoJSON
            with open(sample_plot_path, 'r') as f:
                geojson_data = json.load(f)
            
            features = geojson_data.get('features', [])
            
            # Group by compartment and sub-compartment
            compartment_stats = {}
            subcompartment_stats = {}
            
            for feature in features:
                props = feature.get('properties', {})
                compartment_label = props.get('compartment_label', 'Unknown')
                subcompartment_label = props.get('subcompartment_label', 'Unknown')
                
                compartment_stats[compartment_label] = compartment_stats.get(compartment_label, 0) + 1
                subcompartment_stats[subcompartment_label] = subcompartment_stats.get(subcompartment_label, 0) + 1
            
            stats = {
                'total_plots': len(features),
                'total_compartments': len(compartment_stats),
                'total_subcompartments': len(subcompartment_stats),
                'plots_per_compartment': compartment_stats,
                'plots_per_subcompartment': subcompartment_stats,
                'min_plots_per_subcompartment': min(subcompartment_stats.values()) if subcompartment_stats else 0,
                'max_plots_per_subcompartment': max(subcompartment_stats.values()) if subcompartment_stats else 0,
                'avg_plots_per_subcompartment': len(features) / len(subcompartment_stats) if subcompartment_stats else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating sample plot statistics: {str(e)}")
            raise ValueError(f"Failed to calculate statistics: {str(e)}")
