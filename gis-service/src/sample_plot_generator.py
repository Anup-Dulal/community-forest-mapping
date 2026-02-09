"""
Sample Plot Generator for forest inventory.
Generates sample plots with 2% sampling intensity and minimum 5 plots per compartment.
"""

import json
import logging
import random
from typing import Dict, List, Tuple
import geopandas as gpd
from shapely.geometry import Point, shape, Polygon
from shapely.ops import unary_union

logger = logging.getLogger(__name__)


class SamplePlotGenerator:
    """Generates sample plots for compartments with specified sampling intensity."""

    def __init__(self, export_dir: str):
        """
        Initialize the sample plot generator.
        
        Args:
            export_dir: Directory to store generated sample plot files
        """
        self.export_dir = export_dir
        self.plot_counter = 0

    def generate_sample_plots(
        self,
        compartment_geometry_path: str,
        sampling_intensity: float = 0.02,
        min_plots_per_compartment: int = 5,
        distribution_method: str = "systematic"
    ) -> str:
        """
        Generate sample plots for compartments.
        
        Args:
            compartment_geometry_path: Path to compartment GeoJSON file
            sampling_intensity: Sampling intensity as fraction (default 0.02 = 2%)
            min_plots_per_compartment: Minimum plots per compartment (default 5)
            distribution_method: "systematic" or "random" point distribution
            
        Returns:
            Path to generated sample plot GeoJSON file
            
        Raises:
            ValueError: If compartment file is invalid or generation fails
        """
        try:
            # Load compartment geometries
            gdf_compartments = gpd.read_file(compartment_geometry_path)
            
            if gdf_compartments.empty:
                raise ValueError("Compartment file is empty")
            
            # Generate sample plots
            sample_plots = []
            self.plot_counter = 0
            
            for idx, row in gdf_compartments.iterrows():
                compartment_id = row.get('compartment_id', f'C{idx+1}')
                geometry = row.geometry
                
                # Calculate number of plots for this compartment
                area_m2 = geometry.area  # Area in square meters (assuming projected CRS)
                num_plots = max(
                    min_plots_per_compartment,
                    int(round(area_m2 * sampling_intensity / 10000))  # Convert to hectares
                )
                
                # Generate plots for this compartment
                plots = self._generate_plots_for_compartment(
                    geometry,
                    compartment_id,
                    num_plots,
                    distribution_method
                )
                sample_plots.extend(plots)
            
            # Create GeoDataFrame
            gdf_plots = gpd.GeoDataFrame(
                sample_plots,
                geometry='geometry',
                crs=gdf_compartments.crs
            )
            
            # Save to GeoJSON
            output_path = f"{self.export_dir}/sample_plots.geojson"
            gdf_plots.to_file(output_path, driver='GeoJSON')
            
            logger.info(f"Generated {len(sample_plots)} sample plots")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating sample plots: {str(e)}")
            raise ValueError(f"Failed to generate sample plots: {str(e)}")

    def _generate_plots_for_compartment(
        self,
        compartment_geometry: Polygon,
        compartment_id: str,
        num_plots: int,
        distribution_method: str
    ) -> List[Dict]:
        """
        Generate sample plots for a single compartment.
        
        Args:
            compartment_geometry: Shapely Polygon for the compartment
            compartment_id: ID of the compartment (e.g., "C1")
            num_plots: Number of plots to generate
            distribution_method: "systematic" or "random"
            
        Returns:
            List of sample plot dictionaries with geometry
        """
        plots = []
        
        if distribution_method == "systematic":
            plots = self._generate_systematic_plots(
                compartment_geometry,
                compartment_id,
                num_plots
            )
        else:  # random
            plots = self._generate_random_plots(
                compartment_geometry,
                compartment_id,
                num_plots
            )
        
        return plots

    def _generate_systematic_plots(
        self,
        compartment_geometry: Polygon,
        compartment_id: str,
        num_plots: int
    ) -> List[Dict]:
        """
        Generate systematically distributed sample plots using grid method.
        
        Args:
            compartment_geometry: Shapely Polygon for the compartment
            compartment_id: ID of the compartment
            num_plots: Number of plots to generate
            
        Returns:
            List of sample plot dictionaries
        """
        plots = []
        
        # Get bounding box
        minx, miny, maxx, maxy = compartment_geometry.bounds
        
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
                
                # Check if point is within compartment
                if compartment_geometry.contains(point):
                    self.plot_counter += 1
                    plot_id = f"SP-{self.plot_counter:02d}"
                    
                    plots.append({
                        'plot_id': plot_id,
                        'compartment_id': compartment_id,
                        'geometry': point,
                        'latitude': y,
                        'longitude': x
                    })
            
            if len(plots) >= num_plots:
                break
        
        return plots

    def _generate_random_plots(
        self,
        compartment_geometry: Polygon,
        compartment_id: str,
        num_plots: int
    ) -> List[Dict]:
        """
        Generate randomly distributed sample plots.
        
        Args:
            compartment_geometry: Shapely Polygon for the compartment
            compartment_id: ID of the compartment
            num_plots: Number of plots to generate
            
        Returns:
            List of sample plot dictionaries
        """
        plots = []
        
        # Get bounding box
        minx, miny, maxx, maxy = compartment_geometry.bounds
        
        # Generate random points until we have enough valid ones
        max_attempts = num_plots * 10
        attempts = 0
        
        while len(plots) < num_plots and attempts < max_attempts:
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            
            point = Point(x, y)
            
            # Check if point is within compartment
            if compartment_geometry.contains(point):
                self.plot_counter += 1
                plot_id = f"SP-{self.plot_counter:02d}"
                
                plots.append({
                    'plot_id': plot_id,
                    'compartment_id': compartment_id,
                    'geometry': point,
                    'latitude': y,
                    'longitude': x
                })
            
            attempts += 1
        
        if len(plots) < num_plots:
            logger.warning(
                f"Could not generate {num_plots} plots for {compartment_id}. "
                f"Generated {len(plots)} plots instead."
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
            gdf = gpd.read_file(sample_plot_path)
            
            # Group by compartment
            compartment_stats = gdf.groupby('compartment_id').size().to_dict()
            
            stats = {
                'total_plots': len(gdf),
                'plots_per_compartment': compartment_stats,
                'min_plots': min(compartment_stats.values()) if compartment_stats else 0,
                'max_plots': max(compartment_stats.values()) if compartment_stats else 0,
                'avg_plots': len(gdf) / len(compartment_stats) if compartment_stats else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating sample plot statistics: {str(e)}")
            raise ValueError(f"Failed to calculate statistics: {str(e)}")
