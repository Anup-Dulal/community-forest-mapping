"""
Map Renderer for generating forestry-standard map layouts.
Creates maps with slope, aspect, compartments, and sample plots with proper legends and annotations.
"""

import logging
from typing import Dict, Optional
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class MapRenderer:
    """Renders maps with forestry-standard layout including legends, scale, and annotations."""

    # Color schemes
    SLOPE_COLORS = {
        '0-20': '#90EE90',      # Light green
        '20-30': '#FFD700',     # Gold
        '>30': '#FF6347'        # Tomato red
    }

    ASPECT_COLORS = {
        'N': '#4169E1',         # Royal blue
        'NE': '#87CEEB',        # Sky blue
        'E': '#90EE90',         # Light green
        'SE': '#FFD700',        # Gold
        'S': '#FF8C00',         # Dark orange
        'SW': '#FF6347',        # Tomato red
        'W': '#9370DB',         # Medium purple
        'NW': '#20B2AA'         # Light sea green
    }

    def __init__(self, export_dir: str):
        """
        Initialize the map renderer.
        
        Args:
            export_dir: Directory to store generated map files
        """
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def render_slope_map(
        self,
        boundary_path: str,
        slope_raster_path: str,
        compartment_path: Optional[str] = None,
        title: str = "Slope Classification Map",
        output_format: str = "png"
    ) -> str:
        """
        Render slope classification map with legend and annotations.
        
        Args:
            boundary_path: Path to boundary GeoJSON
            slope_raster_path: Path to slope raster GeoTIFF
            compartment_path: Optional path to compartment GeoJSON
            title: Map title
            output_format: "png" or "pdf"
            
        Returns:
            Path to generated map file
        """
        try:
            # Load data
            gdf_boundary = gpd.read_file(boundary_path)
            gdf_slope = gpd.read_file(slope_raster_path) if Path(slope_raster_path).exists() else None
            gdf_compartments = gpd.read_file(compartment_path) if compartment_path else None

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 10))

            # Plot boundary
            gdf_boundary.plot(ax=ax, alpha=0.3, edgecolor='black', linewidth=2)

            # Plot slope data if available
            if gdf_slope is not None:
                gdf_slope.plot(ax=ax, alpha=0.6, edgecolor='none')

            # Plot compartments if available
            if gdf_compartments is not None:
                gdf_compartments.plot(ax=ax, alpha=0, edgecolor='blue', linewidth=1.5)

            # Add title
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

            # Add legend
            self._add_slope_legend(ax)

            # Add map elements
            self._add_north_arrow(ax)
            self._add_scale_bar(ax)
            self._add_grid_labels(ax)

            # Set labels
            ax.set_xlabel('Longitude', fontsize=10)
            ax.set_ylabel('Latitude', fontsize=10)

            # Save map
            output_path = self._save_map(fig, title, output_format)

            logger.info(f"Slope map rendered: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error rendering slope map: {str(e)}")
            raise ValueError(f"Failed to render slope map: {str(e)}")

    def render_aspect_map(
        self,
        boundary_path: str,
        aspect_raster_path: str,
        compartment_path: Optional[str] = None,
        title: str = "Aspect Direction Map",
        output_format: str = "png"
    ) -> str:
        """
        Render aspect direction map with compass legend and annotations.
        
        Args:
            boundary_path: Path to boundary GeoJSON
            aspect_raster_path: Path to aspect raster GeoTIFF
            compartment_path: Optional path to compartment GeoJSON
            title: Map title
            output_format: "png" or "pdf"
            
        Returns:
            Path to generated map file
        """
        try:
            # Load data
            gdf_boundary = gpd.read_file(boundary_path)
            gdf_aspect = gpd.read_file(aspect_raster_path) if Path(aspect_raster_path).exists() else None
            gdf_compartments = gpd.read_file(compartment_path) if compartment_path else None

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 10))

            # Plot boundary
            gdf_boundary.plot(ax=ax, alpha=0.3, edgecolor='black', linewidth=2)

            # Plot aspect data if available
            if gdf_aspect is not None:
                gdf_aspect.plot(ax=ax, alpha=0.6, edgecolor='none')

            # Plot compartments if available
            if gdf_compartments is not None:
                gdf_compartments.plot(ax=ax, alpha=0, edgecolor='blue', linewidth=1.5)

            # Add title
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

            # Add legend
            self._add_aspect_legend(ax)

            # Add map elements
            self._add_north_arrow(ax)
            self._add_scale_bar(ax)
            self._add_grid_labels(ax)

            # Set labels
            ax.set_xlabel('Longitude', fontsize=10)
            ax.set_ylabel('Latitude', fontsize=10)

            # Save map
            output_path = self._save_map(fig, title, output_format)

            logger.info(f"Aspect map rendered: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error rendering aspect map: {str(e)}")
            raise ValueError(f"Failed to render aspect map: {str(e)}")

    def render_compartment_map(
        self,
        boundary_path: str,
        compartment_path: str,
        title: str = "Compartment Division Map",
        output_format: str = "png"
    ) -> str:
        """
        Render compartment division map with boundaries and IDs.
        
        Args:
            boundary_path: Path to boundary GeoJSON
            compartment_path: Path to compartment GeoJSON
            title: Map title
            output_format: "png" or "pdf"
            
        Returns:
            Path to generated map file
        """
        try:
            # Load data
            gdf_boundary = gpd.read_file(boundary_path)
            gdf_compartments = gpd.read_file(compartment_path)

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 10))

            # Plot boundary
            gdf_boundary.plot(ax=ax, alpha=0.1, edgecolor='black', linewidth=2.5)

            # Plot compartments with different colors
            gdf_compartments.plot(ax=ax, alpha=0.3, edgecolor='darkblue', linewidth=2)

            # Add compartment labels
            for idx, row in gdf_compartments.iterrows():
                centroid = row.geometry.centroid
                compartment_id = row.get('compartment_id', f'C{idx+1}')
                ax.text(centroid.x, centroid.y, compartment_id,
                       fontsize=12, fontweight='bold', ha='center', va='center')

            # Add title
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

            # Add map elements
            self._add_north_arrow(ax)
            self._add_scale_bar(ax)
            self._add_grid_labels(ax)

            # Set labels
            ax.set_xlabel('Longitude', fontsize=10)
            ax.set_ylabel('Latitude', fontsize=10)

            # Save map
            output_path = self._save_map(fig, title, output_format)

            logger.info(f"Compartment map rendered: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error rendering compartment map: {str(e)}")
            raise ValueError(f"Failed to render compartment map: {str(e)}")

    def render_sample_plot_map(
        self,
        boundary_path: str,
        compartment_path: str,
        sample_plot_path: str,
        title: str = "Sample Plot Distribution Map",
        output_format: str = "png"
    ) -> str:
        """
        Render sample plot distribution map with plot markers and IDs.
        
        Args:
            boundary_path: Path to boundary GeoJSON
            compartment_path: Path to compartment GeoJSON
            sample_plot_path: Path to sample plot GeoJSON
            title: Map title
            output_format: "png" or "pdf"
            
        Returns:
            Path to generated map file
        """
        try:
            # Load data
            gdf_boundary = gpd.read_file(boundary_path)
            gdf_compartments = gpd.read_file(compartment_path)
            gdf_plots = gpd.read_file(sample_plot_path)

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 10))

            # Plot boundary
            gdf_boundary.plot(ax=ax, alpha=0.1, edgecolor='black', linewidth=2.5)

            # Plot compartments
            gdf_compartments.plot(ax=ax, alpha=0.2, edgecolor='darkblue', linewidth=1.5)

            # Plot sample plots
            gdf_plots.plot(ax=ax, alpha=0.8, color='red', markersize=50, marker='o')

            # Add plot labels
            for idx, row in gdf_plots.iterrows():
                plot_id = row.get('plot_id', f'SP-{idx+1:02d}')
                ax.text(row.geometry.x, row.geometry.y, plot_id,
                       fontsize=8, ha='center', va='center', color='white', fontweight='bold')

            # Add title
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

            # Add legend
            red_patch = mpatches.Patch(color='red', label='Sample Plots')
            ax.legend(handles=[red_patch], loc='upper right')

            # Add map elements
            self._add_north_arrow(ax)
            self._add_scale_bar(ax)
            self._add_grid_labels(ax)

            # Set labels
            ax.set_xlabel('Longitude', fontsize=10)
            ax.set_ylabel('Latitude', fontsize=10)

            # Save map
            output_path = self._save_map(fig, title, output_format)

            logger.info(f"Sample plot map rendered: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error rendering sample plot map: {str(e)}")
            raise ValueError(f"Failed to render sample plot map: {str(e)}")

    def _add_slope_legend(self, ax):
        """Add slope classification legend to map."""
        legend_elements = [
            mpatches.Patch(facecolor=self.SLOPE_COLORS['0-20'], edgecolor='black', label='0-20°'),
            mpatches.Patch(facecolor=self.SLOPE_COLORS['20-30'], edgecolor='black', label='20-30°'),
            mpatches.Patch(facecolor=self.SLOPE_COLORS['>30'], edgecolor='black', label='>30°')
        ]
        ax.legend(handles=legend_elements, loc='upper left', title='Slope Classes')

    def _add_aspect_legend(self, ax):
        """Add aspect direction legend to map."""
        legend_elements = [
            mpatches.Patch(facecolor=self.ASPECT_COLORS[direction], edgecolor='black', label=direction)
            for direction in ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        ]
        ax.legend(handles=legend_elements, loc='upper left', title='Aspect Directions', ncol=2)

    def _add_north_arrow(self, ax):
        """Add north arrow to map."""
        # Get axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Position in upper right
        x = xlim[1] - (xlim[1] - xlim[0]) * 0.1
        y = ylim[1] - (ylim[1] - ylim[0]) * 0.1

        # Draw arrow
        arrow = FancyArrowPatch((x, y), (x, y + (ylim[1] - ylim[0]) * 0.05),
                              arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
        ax.add_patch(arrow)

        # Add label
        ax.text(x, y + (ylim[1] - ylim[0]) * 0.07, 'N', fontsize=12, fontweight='bold', ha='center')

    def _add_scale_bar(self, ax):
        """Add scale bar to map."""
        # Get axis limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Position in lower left
        x = xlim[0] + (xlim[1] - xlim[0]) * 0.05
        y = ylim[0] + (ylim[1] - ylim[0]) * 0.05

        # Draw scale bar (simplified - assumes degrees)
        scale_length = (xlim[1] - xlim[0]) * 0.1
        ax.plot([x, x + scale_length], [y, y], 'k-', linewidth=2)
        ax.text(x + scale_length / 2, y - (ylim[1] - ylim[0]) * 0.02, '10 km',
               fontsize=10, ha='center')

    def _add_grid_labels(self, ax):
        """Add grid labels to map."""
        # Get current ticks
        xticks = ax.get_xticks()
        yticks = ax.get_yticks()

        # Format labels
        ax.set_xticklabels([f'{x:.2f}°' for x in xticks], fontsize=8)
        ax.set_yticklabels([f'{y:.2f}°' for y in yticks], fontsize=8)

    def _save_map(self, fig, title: str, output_format: str) -> str:
        """
        Save map to file.
        
        Args:
            fig: Matplotlib figure
            title: Map title for filename
            output_format: "png" or "pdf"
            
        Returns:
            Path to saved file
        """
        # Create filename
        safe_title = title.replace(' ', '_').lower()
        filename = f"{safe_title}.{output_format}"
        filepath = Path(self.export_dir) / filename

        # Save figure
        plt.tight_layout()
        fig.savefig(str(filepath), dpi=300, format=output_format, bbox_inches='tight')
        plt.close(fig)

        return str(filepath)
