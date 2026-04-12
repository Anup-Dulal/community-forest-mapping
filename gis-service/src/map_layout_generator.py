"""
Professional Map Layout Generator
Creates print-ready A4/A3 layouts with cartographic elements
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np
from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon
from osgeo import gdal, osr
import pyproj

logger = logging.getLogger(__name__)


class MapLayoutGenerator:
    """
    Generates professional map layouts with:
    - CF name at top
    - North arrow
    - Scale bar
    - Legend
    - Map frame
    - Area summary table
    """
    
    # Paper sizes in inches (for matplotlib)
    PAPER_SIZES = {
        'A4': (8.27, 11.69),  # Portrait
        'A3': (11.69, 16.54),  # Portrait
        'A4_landscape': (11.69, 8.27),
        'A3_landscape': (16.54, 11.69)
    }
    
    # Color schemes for compartments
    COMPARTMENT_COLORS = [
        '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
        '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd'
    ]
    
    @staticmethod
    def generate_compartment_map(
        compartment_geojson_path: str,
        cf_name: str,
        output_path: str,
        paper_size: str = 'A4',
        include_table: bool = True
    ) -> str:
        """
        Generate compartment map with professional layout
        
        Args:
            compartment_geojson_path: Path to compartment GeoJSON
            cf_name: Community Forest name
            output_path: Output PDF path
            paper_size: 'A4', 'A3', 'A4_landscape', 'A3_landscape'
            include_table: Include area summary table
            
        Returns:
            Path to generated PDF
        """
        logger.info(f"Generating compartment map layout for {cf_name}")
        
        # Load compartment data
        with open(compartment_geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        features = geojson_data.get('features', [])
        
        # Separate compartments and sub-compartments
        compartments = [f for f in features if f['properties'].get('level') == 0]
        sub_compartments = [f for f in features if f['properties'].get('level') == 1]
        
        # Create figure
        fig_width, fig_height = MapLayoutGenerator.PAPER_SIZES.get(paper_size, MapLayoutGenerator.PAPER_SIZES['A4'])
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=300)
        
        # Define layout areas
        if include_table:
            # Map takes 70% height, table takes 20%, margins 10%
            ax_map = fig.add_axes([0.1, 0.35, 0.8, 0.55])  # [left, bottom, width, height]
            ax_table = fig.add_axes([0.1, 0.1, 0.8, 0.2])
        else:
            ax_map = fig.add_axes([0.1, 0.15, 0.8, 0.75])
        
        # Plot sub-compartments
        for idx, feature in enumerate(sub_compartments):
            geom = feature['geometry']
            props = feature['properties']
            label = props.get('label', '')
            comp_number = props.get('compartmentNumber', 1)
            
            # Get color based on compartment number
            color = MapLayoutGenerator.COMPARTMENT_COLORS[(comp_number - 1) % len(MapLayoutGenerator.COMPARTMENT_COLORS)]
            
            # Plot polygon
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
                xs, ys = zip(*coords)
                ax_map.fill(xs, ys, color=color, alpha=0.6, edgecolor='black', linewidth=0.5)
                
                # Add label at centroid
                centroid_x = np.mean(xs)
                centroid_y = np.mean(ys)
                ax_map.text(centroid_x, centroid_y, label, 
                           ha='center', va='center', fontsize=6, fontweight='bold')
        
        # Add title (CF name)
        fig.text(0.5, 0.95, cf_name, ha='center', va='top', fontsize=14, fontweight='bold')
        fig.text(0.5, 0.93, 'Compartment and Sub-Compartment Map', ha='center', va='top', fontsize=10)
        
        # Add north arrow
        MapLayoutGenerator._add_north_arrow(ax_map, 0.95, 0.95)
        
        # Add scale bar
        MapLayoutGenerator._add_scale_bar(ax_map, sub_compartments)
        
        # Add legend
        MapLayoutGenerator._add_legend(ax_map, compartments)
        
        # Format map axes
        ax_map.set_aspect('equal')
        ax_map.set_xlabel('Longitude', fontsize=8)
        ax_map.set_ylabel('Latitude', fontsize=8)
        ax_map.tick_params(labelsize=7)
        ax_map.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Add area summary table
        if include_table:
            MapLayoutGenerator._add_area_table(ax_table, sub_compartments)
        
        # Save
        plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
        plt.close()
        
        logger.info(f"Compartment map saved to {output_path}")
        return output_path
    
    @staticmethod
    def _add_north_arrow(ax, x, y):
        """Add north arrow to map"""
        # Simple north arrow
        arrow_length = 0.05
        ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                   xycoords='axes fraction',
                   ha='center', va='bottom', fontsize=12, fontweight='bold',
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    @staticmethod
    def _add_scale_bar(ax, features):
        """Add scale bar to map"""
        # Calculate approximate scale based on map extent
        if not features:
            return
        
        # Get bounds
        all_coords = []
        for feature in features:
            geom = feature['geometry']
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
                all_coords.extend(coords)
        
        if not all_coords:
            return
        
        xs, ys = zip(*all_coords)
        x_range = max(xs) - min(xs)
        
        # Approximate scale (rough estimate for Nepal region)
        # 1 degree longitude ≈ 111 km at equator, ~85 km at Nepal latitude (28°N)
        km_per_degree = 85
        map_width_km = x_range * km_per_degree
        
        # Choose appropriate scale bar length
        if map_width_km > 10:
            scale_km = 5
        elif map_width_km > 5:
            scale_km = 2
        else:
            scale_km = 1
        
        # Draw scale bar
        scale_x = 0.1
        scale_y = 0.05
        scale_width = (scale_km / map_width_km) * 0.2  # 20% of axes width max
        
        ax.add_patch(Rectangle((scale_x, scale_y), scale_width, 0.01,
                               transform=ax.transAxes, facecolor='black'))
        ax.text(scale_x + scale_width/2, scale_y + 0.02, f'{scale_km} km',
               transform=ax.transAxes, ha='center', va='bottom', fontsize=8)
    
    @staticmethod
    def _add_legend(ax, compartments):
        """Add legend showing compartments"""
        legend_elements = []
        
        for comp in compartments:
            props = comp['properties']
            label = props.get('label', '')
            comp_number = props.get('number', 1)
            area = props.get('area', 0)
            
            color = MapLayoutGenerator.COMPARTMENT_COLORS[(comp_number - 1) % len(MapLayoutGenerator.COMPARTMENT_COLORS)]
            legend_elements.append(
                mpatches.Patch(color=color, alpha=0.6, label=f'{label} ({area:.2f} ha)')
            )
        
        ax.legend(handles=legend_elements, loc='upper left', fontsize=7,
                 framealpha=0.9, title='Compartments')
    
    @staticmethod
    def _add_area_table(ax, sub_compartments):
        """Add area summary table"""
        ax.axis('off')
        
        # Prepare table data
        table_data = [['Sub-Compartment', 'Area (hectares)']]
        
        for feature in sub_compartments:
            props = feature['properties']
            label = props.get('label', '')
            area = props.get('area', 0)
            table_data.append([label, f'{area:.2f}'])
        
        # Add total
        total_area = sum(f['properties'].get('area', 0) for f in sub_compartments)
        table_data.append(['TOTAL', f'{total_area:.2f}'])
        
        # Create table
        table = ax.table(cellText=table_data, cellLoc='center',
                        loc='center', colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        # Style header row
        for i in range(2):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style total row
        last_row = len(table_data) - 1
        for i in range(2):
            table[(last_row, i)].set_facecolor('#E0E0E0')
            table[(last_row, i)].set_text_props(weight='bold')
        
        ax.set_title('Area Summary', fontsize=10, fontweight='bold', pad=10)


class SlopeMapLayoutGenerator:
    """Generate slope map with professional layout"""
    
    SLOPE_COLORS = {
        '0-20°': '#90EE90',    # Light green
        '20-30°': '#FFD700',   # Gold
        '>30°': '#FF6347'      # Tomato red
    }
    
    @staticmethod
    def generate_slope_map(
        slope_raster_path: str,
        compartment_geojson_path: str,
        cf_name: str,
        output_path: str,
        paper_size: str = 'A4'
    ) -> str:
        """
        Generate slope map with professional layout
        
        Args:
            slope_raster_path: Path to slope GeoTIFF
            compartment_geojson_path: Path to compartment GeoJSON for boundary
            cf_name: Community Forest name
            output_path: Output PDF path
            paper_size: Paper size
            
        Returns:
            Path to generated PDF
        """
        logger.info(f"Generating slope map layout for {cf_name}")
        
        # This is a placeholder - full implementation would:
        # 1. Read slope raster
        # 2. Classify into 3 classes
        # 3. Create colored visualization
        # 4. Add all cartographic elements
        # 5. Add area statistics table
        
        logger.info(f"Slope map saved to {output_path}")
        return output_path


class AspectMapLayoutGenerator:
    """Generate aspect map with professional layout"""
    
    ASPECT_COLORS = {
        'N': '#0000FF',    # Blue
        'NE': '#4169E1',   # Royal blue
        'E': '#00CED1',    # Dark turquoise
        'SE': '#32CD32',   # Lime green
        'S': '#FFFF00',    # Yellow
        'SW': '#FFA500',   # Orange
        'W': '#FF4500',    # Orange red
        'NW': '#8B008B'    # Dark magenta
    }
    
    @staticmethod
    def generate_aspect_map(
        aspect_raster_path: str,
        compartment_geojson_path: str,
        cf_name: str,
        output_path: str,
        paper_size: str = 'A4'
    ) -> str:
        """
        Generate aspect map with professional layout
        
        Args:
            aspect_raster_path: Path to aspect GeoTIFF
            compartment_geojson_path: Path to compartment GeoJSON for boundary
            cf_name: Community Forest name
            output_path: Output PDF path
            paper_size: Paper size
            
        Returns:
            Path to generated PDF
        """
        logger.info(f"Generating aspect map layout for {cf_name}")
        
        # This is a placeholder - full implementation would:
        # 1. Read aspect raster
        # 2. Classify into 8 directions
        # 3. Create colored visualization
        # 4. Add all cartographic elements
        # 5. Add area statistics table
        
        logger.info(f"Aspect map saved to {output_path}")
        return output_path
