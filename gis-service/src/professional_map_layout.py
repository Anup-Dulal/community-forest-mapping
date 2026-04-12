"""
Professional A4 Map Layout Generator
Creates clean, dataframe-style cartographic layouts for official forestry documentation
NO base maps, NO satellite imagery - only processed thematic data
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.gridspec as gridspec
import numpy as np
from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon, shape
from osgeo import gdal, osr
import pyproj
import pandas as pd

logger = logging.getLogger(__name__)


class ProfessionalMapLayout:
    """
    Professional A4 map layout generator following cartographic standards
    
    Layout structure:
    - Top center: CF name (title)
    - Main area: Clean thematic map (NO base map)
    - Lower right: Legend
    - Lower left: Area summary table
    - North arrow and scale bar
    - UTM coordinate labels on borders (no heavy gridlines)
    """
    
    # A4 size in inches (portrait)
    A4_SIZE = (8.27, 11.69)
    
    # Color schemes
    COMPARTMENT_COLORS = [
        '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
        '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd'
    ]
    
    SLOPE_COLORS = {
        '0-20°': '#90EE90',    # Light green
        '20-30°': '#FFD700',   # Gold
        '>30°': '#FF6347'      # Tomato red
    }
    
    ASPECT_COLORS = {
        'North': '#0000FF',
        'Northeast': '#4169E1',
        'East': '#00CED1',
        'Southeast': '#32CD32',
        'South': '#FFFF00',
        'Southwest': '#FFA500',
        'West': '#FF4500',
        'Northwest': '#8B008B'
    }
    
    @staticmethod
    def generate_compartment_map(
        compartment_geojson_path: str,
        cf_name: str,
        output_path: str,
        language: str = "english",
        utm_epsg: str = "EPSG:32644"
    ) -> str:
        """
        Generate professional A4 compartment map matching reference style
        
        Args:
            compartment_geojson_path: Path to compartment GeoJSON file
            cf_name: Community Forest name (in selected language)
            output_path: Output file path
            language: "english" or "nepali"
            utm_epsg: UTM EPSG code for coordinate conversion
        
        Layout:
        - Title at top center (supports Nepali)
        - Clean map with UTM coordinates (no base map)
        - Legend at bottom right
        - Area table on right side
        - North arrow with cardinal directions
        - Scale bar at bottom
        """
        logger.info(f"Generating professional compartment map for {cf_name} in {language}")
        
        # Translations
        translations = {
            "english": {
                "subtitle": "Compartment and Sub-Compartment Map",
                "legend": "Legend",
                "areas_title": "Sub-Compartment Areas (ha)",
                "north": "N",
                "south": "S",
                "east": "E",
                "west": "W",
                "meters": "Meters",
                "scale": "Scale"
            },
            "nepali": {
                "subtitle": "खण्ड र उप-खण्ड नक्सा",
                "legend": "किंवदन्ती",
                "areas_title": "उप-खण्ड क्षेत्रफल (हेक्टर)",
                "north": "उ",
                "south": "द",
                "east": "पू",
                "west": "प",
                "meters": "मिटर",
                "scale": "मापन"
            }
        }
        
        t = translations.get(language, translations["english"])
        
        # Set font based on language
        font_prop = None
        if language == "nepali":
            try:
                from matplotlib.font_manager import FontProperties
                
                # Use FontProperties to directly specify the font file
                devanagari_font = '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf'
                font_prop = FontProperties(fname=devanagari_font)
                
                logger.info("Using Nepali font: Noto Sans Devanagari")
            except Exception as e:
                logger.warning(f"Nepali font setup failed: {e}, using default")
                font_prop = None
        
        # Set default font for non-text elements
        plt.rcParams['font.family'] = 'DejaVu Sans'
        
        # Load data
        with open(compartment_geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        features = geojson_data.get('features', [])
        sub_compartments = [f for f in features if f['properties'].get('level') == 1]
        
        if not sub_compartments:
            sub_compartments = features  # Fallback to all features
        
        # Create figure with A4 dimensions
        fig = plt.figure(figsize=ProfessionalMapLayout.A4_SIZE, dpi=300)
        fig.patch.set_facecolor('white')
        
        # Create coordinate transformer for UTM conversion
        transformer = pyproj.Transformer.from_crs("EPSG:4326", utm_epsg, always_xy=True)
        
        # Main map axes
        ax_map = fig.add_axes([0.15, 0.15, 0.6, 0.7])
        
        # Plot compartments and collect bounds
        all_x, all_y = [], []
        
        for idx, feature in enumerate(sub_compartments):
            geom_dict = feature['geometry']
            props = feature['properties']
            label = props.get('label', '')
            comp_number = props.get('compartment_number', props.get('compartmentNumber', 1))
            
            # Get color
            color = ProfessionalMapLayout.COMPARTMENT_COLORS[(comp_number - 1) % len(ProfessionalMapLayout.COMPARTMENT_COLORS)]
            
            # Convert to shapely geometry
            geom = shape(geom_dict)
            
            # Plot polygon
            if geom.geom_type == 'Polygon':
                xs, ys = geom.exterior.xy
                # Convert to UTM for plotting
                xs_utm, ys_utm = transformer.transform(list(xs), list(ys))
                all_x.extend(xs_utm)
                all_y.extend(ys_utm)
                
                ax_map.fill(xs_utm, ys_utm, color=color, alpha=0.7, edgecolor='black', linewidth=0.8)
                
                # Add label at centroid - ALWAYS use Latin font for compartment IDs
                # Never apply Nepali font to C1S1 style labels
                centroid = geom.centroid
                cx_utm, cy_utm = transformer.transform(centroid.x, centroid.y)
                ax_map.text(cx_utm, cy_utm, label, 
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           fontfamily='DejaVu Sans', fontproperties=None)
        
        # Format map - clean, no base map
        ax_map.set_aspect('equal')
        ax_map.set_facecolor('#FFFACD')  # Light yellow background like reference
        
        # Format UTM coordinates on axes
        def format_utm_coord(value, axis='x'):
            """Format coordinate as UTM (e.g., 0485000 E)"""
            direction = t["east"] if axis == 'x' else t["north"]
            return f"{int(value):07d} {direction}"
        
        # Set UTM coordinate labels
        ax_map.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_utm_coord(x, 'x')))
        ax_map.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, p: format_utm_coord(y, 'y')))
        ax_map.tick_params(labelsize=6, rotation=0)
        
        # Add title at top
        title_kwargs = {'ha': 'center', 'va': 'top', 'fontsize': 14, 'fontweight': 'bold'}
        subtitle_kwargs = {'ha': 'center', 'va': 'top', 'fontsize': 10}
        
        if font_prop:
            title_kwargs['fontproperties'] = font_prop
            subtitle_kwargs['fontproperties'] = font_prop
        
        fig.text(0.5, 0.95, cf_name, **title_kwargs)
        fig.text(0.5, 0.92, t["subtitle"], **subtitle_kwargs)
        
        # Add north arrow (upper right)
        arrow_ax = fig.add_axes([0.82, 0.75, 0.08, 0.08])
        arrow_ax.set_xlim(0, 1)
        arrow_ax.set_ylim(0, 1)
        arrow_ax.axis('off')
        arrow = FancyArrowPatch((0.5, 0.2), (0.5, 0.8),
                               arrowstyle='->', mutation_scale=30,
                               linewidth=2, color='black')
        arrow_ax.add_patch(arrow)
        
        text_kwargs = {'ha': 'center', 'fontsize': 14, 'fontweight': 'bold'}
        if font_prop:
            text_kwargs['fontproperties'] = font_prop
        arrow_ax.text(0.5, 0.9, t["north"], va='bottom', **text_kwargs)
        
        text_kwargs_small = {'ha': 'center', 'va': 'center', 'fontsize': 10}
        if font_prop:
            text_kwargs_small['fontproperties'] = font_prop
        arrow_ax.text(0.2, 0.5, t["west"], **text_kwargs_small)
        arrow_ax.text(0.8, 0.5, t["east"], **text_kwargs_small)
        arrow_ax.text(0.5, 0.1, t["south"], ha='center', va='top', fontsize=10,
                     fontproperties=font_prop if font_prop else None)
        
        # Add area table (right side)
        table_ax = fig.add_axes([0.78, 0.35, 0.2, 0.35])
        table_ax.axis('off')
        
        # Prepare table data
        table_data = []
        for f in sub_compartments:
            props = f['properties']
            comp_num = props.get('compartment_number', props.get('compartmentNumber', ''))
            label = props.get('label', '')
            area = props.get('area', 0)
            table_data.append([label, f"{area:.2f}"])
        
        if table_data:
            # Add header
            header_kwargs = {'ha': 'center', 'va': 'top', 'fontsize': 8, 'fontweight': 'bold',
                           'transform': table_ax.transAxes}
            if font_prop:
                header_kwargs['fontproperties'] = font_prop
            
            table_ax.text(0.5, 0.98, t["areas_title"], **header_kwargs)
            
            # Create table
            df = pd.DataFrame(table_data, columns=['Label', 'Area (ha)'])
            table = table_ax.table(cellText=df.values,
                                  cellLoc='center', loc='center',
                                  bbox=[0.0, 0.0, 1.0, 0.9])
            table.auto_set_font_size(False)
            table.set_fontsize(6)
            table.scale(1, 1.5)
            
            # Style cells - use Latin font for labels (C1S1, etc.)
            from matplotlib.font_manager import FontProperties
            latin_font = FontProperties(family='DejaVu Sans')
            
            for i in range(len(df)):
                for j in range(2):
                    cell = table[(i, j)]
                    cell.set_edgecolor('black')
                    cell.set_linewidth(0.5)
                    # Force Latin font for compartment labels
                    cell.set_text_props(fontproperties=latin_font)
        
        # Add legend (bottom right)
        legend_ax = fig.add_axes([0.78, 0.15, 0.2, 0.15])
        legend_ax.axis('off')
        
        legend_kwargs = {'ha': 'center', 'va': 'top', 'fontsize': 9, 'fontweight': 'bold',
                        'transform': legend_ax.transAxes}
        if font_prop:
            legend_kwargs['fontproperties'] = font_prop
        
        legend_ax.text(0.5, 0.95, t["legend"], **legend_kwargs)
        
        # Get unique compartments
        compartments = set()
        for f in sub_compartments:
            props = f['properties']
            comp_num = props.get('compartment_number', props.get('compartmentNumber', 1))
            compartments.add(comp_num)
        
        y_pos = 0.75
        for comp_num in sorted(compartments):
            color = ProfessionalMapLayout.COMPARTMENT_COLORS[(comp_num - 1) % len(ProfessionalMapLayout.COMPARTMENT_COLORS)]
            rect = Rectangle((0.1, y_pos - 0.08), 0.15, 0.12,
                           transform=legend_ax.transAxes, facecolor=color,
                           edgecolor='black', linewidth=0.5)
            legend_ax.add_patch(rect)
            
            # Show compartment label (C1, C2, etc.)
            comp_label = f'C{comp_num}'
            text_kwargs = {'transform': legend_ax.transAxes, 'va': 'center', 'fontsize': 7}
            if font_prop:
                text_kwargs['fontproperties'] = font_prop
            legend_ax.text(0.3, y_pos - 0.02, comp_label, **text_kwargs)
            y_pos -= 0.2
        
        # Add scale bar at bottom
        scale_ax = fig.add_axes([0.15, 0.08, 0.3, 0.03])
        scale_ax.set_xlim(0, 1)
        scale_ax.set_ylim(0, 1)
        scale_ax.axis('off')
        
        # Calculate scale from map bounds
        all_coords = []
        for f in sub_compartments:
            geom = shape(f['geometry'])
            bounds = geom.bounds
            all_coords.extend([bounds[0], bounds[2]])
        
        if all_coords:
            map_width = max(all_coords) - min(all_coords)
            scale_length_m = map_width / 5
            
            # Round to nice number
            if scale_length_m > 1000:
                scale_length_m = round(scale_length_m / 1000) * 1000
                scale_label = f"{int(scale_length_m)} Meters"
            else:
                scale_length_m = round(scale_length_m / 100) * 100
                scale_label = f"{int(scale_length_m)} Meters"
            
            # Draw scale bar with segments
            segment_width = 0.8 / 5
            for i in range(5):
                color = 'black' if i % 2 == 0 else 'white'
                rect = Rectangle((0.1 + i * segment_width, 0.4), segment_width, 0.2,
                               facecolor=color, edgecolor='black', linewidth=0.5)
                scale_ax.add_patch(rect)
            
            scale_ax.text(0.5, 0.1, scale_label, ha='center', va='top', fontsize=8)
        
        # Save
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   pad_inches=0.3, facecolor='white', edgecolor='none')
        plt.close()
        
        logger.info(f"Professional compartment map saved: {output_path}")
        return output_path
    
    @staticmethod
    def _add_north_arrow(ax, x, y):
        """Add professional north arrow"""
        # Arrow in axes coordinates
        arrow = FancyArrowPatch((x, y-0.05), (x, y), 
                               transform=ax.transAxes,
                               arrowstyle='->', mutation_scale=20, 
                               linewidth=2, color='black')
        ax.add_patch(arrow)
        ax.text(x, y+0.02, 'N', transform=ax.transAxes,
               ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    @staticmethod
    def _add_scale_bar(ax, features):
        """Add scale bar to map"""
        # Calculate approximate scale
        if not features:
            return
        
        # Get bounds
        all_coords = []
        for f in features:
            geom = shape(f['geometry'])
            bounds = geom.bounds
            all_coords.extend([bounds[0], bounds[2]])
        
        if not all_coords:
            return
        
        map_width = max(all_coords) - min(all_coords)
        scale_length = map_width / 5  # 20% of map width
        
        # Round to nice number
        if scale_length > 1000:
            scale_length = round(scale_length / 1000) * 1000
        elif scale_length > 100:
            scale_length = round(scale_length / 100) * 100
        else:
            scale_length = round(scale_length / 10) * 10
        
        # Draw scale bar
        x_start = 0.05
        y_pos = 0.05
        bar_width = 0.15
        
        ax.plot([x_start, x_start + bar_width], [y_pos, y_pos],
               transform=ax.transAxes, color='black', linewidth=2)
        ax.plot([x_start, x_start], [y_pos - 0.01, y_pos + 0.01],
               transform=ax.transAxes, color='black', linewidth=2)
        ax.plot([x_start + bar_width, x_start + bar_width], [y_pos - 0.01, y_pos + 0.01],
               transform=ax.transAxes, color='black', linewidth=2)
        
        # Label
        if scale_length >= 1000:
            label = f"{int(scale_length/1000)} km"
        else:
            label = f"{int(scale_length)} m"
        
        ax.text(x_start + bar_width/2, y_pos - 0.03, label,
               transform=ax.transAxes, ha='center', va='top', fontsize=7)
    
    @staticmethod
    def _add_compartment_legend(ax, features):
        """Add legend showing compartments"""
        ax.axis('off')
        ax.text(0.5, 0.95, 'Legend', transform=ax.transAxes,
               ha='center', va='top', fontsize=9, fontweight='bold')
        
        # Get unique compartments
        compartments = {}
        for f in features:
            props = f['properties']
            comp_num = props.get('compartment_number', props.get('compartmentNumber', 1))
            label = props.get('label', f'C{comp_num}')
            if comp_num not in compartments:
                compartments[comp_num] = label
        
        # Draw legend items
        y_pos = 0.85
        for comp_num in sorted(compartments.keys()):
            color = ProfessionalMapLayout.COMPARTMENT_COLORS[(comp_num - 1) % len(ProfessionalMapLayout.COMPARTMENT_COLORS)]
            
            # Color box
            rect = Rectangle((0.1, y_pos - 0.03), 0.1, 0.05, 
                           transform=ax.transAxes, facecolor=color, 
                           edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # Label
            ax.text(0.25, y_pos, f'Compartment {comp_num}', 
                   transform=ax.transAxes, va='center', fontsize=7)
            
            y_pos -= 0.08
    
    @staticmethod
    def _add_area_table(ax, features):
        """Add area summary table"""
        ax.axis('off')
        ax.text(0.5, 0.95, 'Area Summary', transform=ax.transAxes,
               ha='center', va='top', fontsize=9, fontweight='bold')
        
        # Prepare data
        data = []
        for f in features:
            props = f['properties']
            comp_num = props.get('compartment_number', props.get('compartmentNumber', ''))
            label = props.get('label', '')
            area = props.get('area', 0)
            data.append([comp_num, label, f"{area:.2f}"])
        
        # Create table
        if data:
            df = pd.DataFrame(data, columns=['Comp', 'Sub-Comp', 'Area (ha)'])
            
            # Display as table
            table = ax.table(cellText=df.values, colLabels=df.columns,
                           cellLoc='center', loc='center',
                           bbox=[0.05, 0.1, 0.9, 0.8])
            table.auto_set_font_size(False)
            table.set_fontsize(6)
            table.scale(1, 1.5)
            
            # Style header
            for i in range(len(df.columns)):
                table[(0, i)].set_facecolor('#4CAF50')
                table[(0, i)].set_text_props(weight='bold', color='white')


class ProfessionalSlopeMapLayout:
    """
    Professional A4 slope map layout matching reference style
    
    Features:
    - Continuous color gradient (green → yellow → red)
    - Coordinate system info box on left
    - Legend with continuous scale on right
    - Scale bar at bottom
    - North arrow
    - Nepali title support
    """
    
    @staticmethod
    def generate_slope_map(
        slope_raster_path: str,
        compartment_geojson_path: str,
        cf_name: str,
        output_path: str,
        slope_stats: Dict = None,
        nepali_title: str = None
    ) -> str:
        """
        Generate professional A4 slope map with continuous gradient
        
        Args:
            slope_raster_path: Path to slope GeoTIFF
            compartment_geojson_path: Path to boundary GeoJSON
            cf_name: Community Forest name
            output_path: Output PDF path
            slope_stats: Pre-calculated slope statistics
            nepali_title: Optional Nepali title
        """
        logger.info(f"Generating professional slope map for {cf_name}")
        
        # Load slope raster
        ds = gdal.Open(slope_raster_path)
        if ds is None:
            raise ValueError(f"Could not open slope raster: {slope_raster_path}")
        
        band = ds.GetRasterBand(1)
        slope_array = band.ReadAsArray()
        
        # Mask invalid values
        slope_array = np.ma.masked_where(slope_array < 0, slope_array)
        slope_array = np.ma.masked_where(slope_array > 90, slope_array)
        
        # Get geotransform and projection
        gt = ds.GetGeoTransform()
        proj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=proj)
        
        # Calculate extent
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        minx = gt[0]
        maxy = gt[3]
        maxx = minx + cols * gt[1]
        miny = maxy + rows * gt[5]
        extent = [minx, maxx, miny, maxy]
        
        # Create figure
        fig = plt.figure(figsize=ProfessionalMapLayout.A4_SIZE, dpi=300)
        fig.patch.set_facecolor('white')
        
        # Create main axes for map
        ax_map = fig.add_axes([0.15, 0.15, 0.7, 0.7])
        
        # Plot slope with continuous color gradient (green → yellow → red)
        from matplotlib.colors import LinearSegmentedColormap
        colors = ['#00FF00', '#90EE90', '#FFFF00', '#FFA500', '#FF0000', '#8B0000']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('slope', colors, N=n_bins)
        
        im = ax_map.imshow(slope_array, extent=extent, cmap=cmap,
                          interpolation='bilinear', origin='upper',
                          vmin=0, vmax=np.nanmax(slope_array))
        
        # Format map
        ax_map.set_aspect('equal')
        ax_map.tick_params(labelsize=7)
        ax_map.set_xlabel('', fontsize=8)
        ax_map.set_ylabel('', fontsize=8)
        
        # Add title at top
        title_text = nepali_title if nepali_title else cf_name
        fig.text(0.5, 0.95, title_text, ha='center', va='top',
                fontsize=14, fontweight='bold')
        fig.text(0.5, 0.92, 'Slope Map',
                ha='center', va='top', fontsize=11)
        
        # Add north arrow
        arrow_ax = fig.add_axes([0.88, 0.75, 0.08, 0.08])
        arrow_ax.set_xlim(0, 1)
        arrow_ax.set_ylim(0, 1)
        arrow_ax.axis('off')
        arrow = FancyArrowPatch((0.5, 0.2), (0.5, 0.8),
                               arrowstyle='->', mutation_scale=30,
                               linewidth=2, color='black')
        arrow_ax.add_patch(arrow)
        arrow_ax.text(0.5, 0.9, 'N', ha='center', va='bottom',
                     fontsize=14, fontweight='bold')
        
        # Add colorbar legend (right side)
        cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.5])
        cbar = plt.colorbar(im, cax=cbar_ax)
        cbar.set_label('Slope (degrees)', fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        
        # Add legend box
        legend_ax = fig.add_axes([0.82, 0.05, 0.15, 0.08])
        legend_ax.axis('off')
        legend_ax.text(0.5, 0.8, 'Legend', ha='center', va='top',
                      fontsize=9, fontweight='bold', transform=legend_ax.transAxes)
        legend_ax.text(0.5, 0.4, '<VALUE>', ha='center', va='center',
                      fontsize=8, transform=legend_ax.transAxes)
        
        # Calculate value ranges for legend
        max_slope = np.nanmax(slope_array)
        ranges = [
            (0, 5, '#00FF00'),
            (5, 10, '#90EE90'),
            (10, 15, '#FFFF00'),
            (15, 20, '#FFA500'),
            (20, max_slope, '#FF0000')
        ]
        
        y_pos = 0.2
        for min_val, max_val, color in ranges:
            if max_val <= max_slope:
                rect = Rectangle((0.1, y_pos), 0.2, 0.08,
                               transform=legend_ax.transAxes,
                               facecolor=color, edgecolor='black', linewidth=0.5)
                legend_ax.add_patch(rect)
                label = f"{min_val} - {int(max_val)}" if max_val < max_slope else f"{min_val} - {max_slope:.2f}"
                legend_ax.text(0.35, y_pos + 0.04, label,
                             transform=legend_ax.transAxes,
                             va='center', fontsize=6)
                y_pos -= 0.12
        
        # Add scale bar at bottom
        scale_ax = fig.add_axes([0.15, 0.08, 0.3, 0.03])
        scale_ax.set_xlim(0, 1)
        scale_ax.set_ylim(0, 1)
        scale_ax.axis('off')
        
        # Calculate scale
        map_width = maxx - minx
        scale_length_m = map_width / 5
        
        # Round to nice number
        if scale_length_m > 1000:
            scale_length_m = round(scale_length_m / 1000) * 1000
            scale_label = f"{int(scale_length_m/1000)} km"
        else:
            scale_length_m = round(scale_length_m / 100) * 100
            scale_label = f"{int(scale_length_m)} m"
        
        # Draw scale bar
        scale_ax.plot([0.1, 0.9], [0.5, 0.5], 'k-', linewidth=2)
        scale_ax.plot([0.1, 0.1], [0.3, 0.7], 'k-', linewidth=2)
        scale_ax.plot([0.9, 0.9], [0.3, 0.7], 'k-', linewidth=2)
        scale_ax.text(0.5, 0.1, scale_label, ha='center', va='top', fontsize=8)
        
        # Add scale bar segments (black and white)
        segment_width = 0.8 / 5
        for i in range(5):
            color = 'black' if i % 2 == 0 else 'white'
            rect = Rectangle((0.1 + i * segment_width, 0.4), segment_width, 0.2,
                           facecolor=color, edgecolor='black', linewidth=0.5)
            scale_ax.add_patch(rect)
        
        # Save
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   pad_inches=0.3, facecolor='white', edgecolor='none')
        plt.close()
        
        logger.info(f"Professional slope map saved: {output_path}")
        return output_path


class ProfessionalAspectMapLayout:
    """Professional A4 aspect map layout"""
    
    @staticmethod
    def generate_aspect_map(
        aspect_raster_path: str,
        compartment_geojson_path: str,
        cf_name: str,
        output_path: str,
        aspect_stats: Dict = None
    ) -> str:
        """Generate professional A4 aspect map"""
        logger.info(f"Generating professional aspect map for {cf_name}")
        
        # Load aspect raster
        ds = gdal.Open(aspect_raster_path)
        if ds is None:
            raise ValueError(f"Could not open aspect raster: {aspect_raster_path}")
        
        band = ds.GetRasterBand(1)
        aspect_array = band.ReadAsArray()
        
        # Get geotransform
        gt = ds.GetGeoTransform()
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        minx = gt[0]
        maxy = gt[3]
        maxx = minx + cols * gt[1]
        miny = maxy + rows * gt[5]
        extent = [minx, maxx, miny, maxy]
        
        # Classify aspect into 8 directions
        aspect_classified = np.zeros_like(aspect_array)
        aspect_classified[(aspect_array >= 337.5) | (aspect_array < 22.5)] = 1  # N
        aspect_classified[(aspect_array >= 22.5) & (aspect_array < 67.5)] = 2   # NE
        aspect_classified[(aspect_array >= 67.5) & (aspect_array < 112.5)] = 3  # E
        aspect_classified[(aspect_array >= 112.5) & (aspect_array < 157.5)] = 4 # SE
        aspect_classified[(aspect_array >= 157.5) & (aspect_array < 202.5)] = 5 # S
        aspect_classified[(aspect_array >= 202.5) & (aspect_array < 247.5)] = 6 # SW
        aspect_classified[(aspect_array >= 247.5) & (aspect_array < 292.5)] = 7 # W
        aspect_classified[(aspect_array >= 292.5) & (aspect_array < 337.5)] = 8 # NW
        
        # Create figure
        fig = plt.figure(figsize=ProfessionalMapLayout.A4_SIZE, dpi=300)
        fig.patch.set_facecolor('white')
        
        gs = gridspec.GridSpec(20, 20, figure=fig, hspace=0.5, wspace=0.5)
        
        # Title
        ax_title = fig.add_subplot(gs[0:2, :])
        ax_title.axis('off')
        ax_title.text(0.5, 0.5, cf_name, ha='center', va='center',
                     fontsize=16, fontweight='bold', transform=ax_title.transAxes)
        ax_title.text(0.5, 0.1, 'Aspect Map', ha='center', va='center',
                     fontsize=10, transform=ax_title.transAxes)
        
        # Main map
        ax_map = fig.add_subplot(gs[2:16, 1:19])
        
        # Plot aspect with custom colors
        from matplotlib.colors import ListedColormap, BoundaryNorm
        colors = ['#0000FF', '#4169E1', '#00CED1', '#32CD32', 
                 '#FFFF00', '#FFA500', '#FF4500', '#8B008B']
        cmap = ListedColormap(colors)
        bounds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
        norm = BoundaryNorm(bounds, cmap.N)
        
        im = ax_map.imshow(aspect_classified, extent=extent, cmap=cmap, norm=norm,
                          interpolation='nearest', origin='upper')
        
        # Format map
        ax_map.set_aspect('equal')
        ax_map.tick_params(labelsize=6)
        ax_map.set_xlabel('Easting (UTM)', fontsize=8)
        ax_map.set_ylabel('Northing (UTM)', fontsize=8)
        ax_map.grid(True, alpha=0.2, linestyle=':', linewidth=0.5, color='gray')
        
        # North arrow
        ProfessionalMapLayout._add_north_arrow(ax_map, 0.95, 0.95)
        
        # Legend (lower right)
        ax_legend = fig.add_subplot(gs[16:20, 10:19])
        ax_legend.axis('off')
        ax_legend.text(0.5, 0.95, 'Aspect Direction', transform=ax_legend.transAxes,
                      ha='center', va='top', fontsize=9, fontweight='bold')
        
        directions = [
            ('North', '#0000FF'), ('Northeast', '#4169E1'),
            ('East', '#00CED1'), ('Southeast', '#32CD32'),
            ('South', '#FFFF00'), ('Southwest', '#FFA500'),
            ('West', '#FF4500'), ('Northwest', '#8B008B')
        ]
        
        y_pos = 0.85
        for label, color in directions:
            rect = Rectangle((0.05, y_pos - 0.03), 0.1, 0.05,
                           transform=ax_legend.transAxes, facecolor=color,
                           edgecolor='black', linewidth=0.5)
            ax_legend.add_patch(rect)
            ax_legend.text(0.2, y_pos, label, transform=ax_legend.transAxes,
                          va='center', fontsize=6)
            y_pos -= 0.09
        
        # Area table (lower left)
        ax_table = fig.add_subplot(gs[16:20, 1:9])
        ax_table.axis('off')
        ax_table.text(0.5, 0.95, 'Area Summary (hectares)', transform=ax_table.transAxes,
                     ha='center', va='top', fontsize=9, fontweight='bold')
        
        if aspect_stats:
            data = [[dir, f"{aspect_stats.get(dir, 0):.2f}"] 
                   for dir, _ in directions]
            
            table = ax_table.table(cellText=data, colLabels=['Direction', 'Area (ha)'],
                                  cellLoc='center', loc='center',
                                  bbox=[0.05, 0.05, 0.9, 0.85])
            table.auto_set_font_size(False)
            table.set_fontsize(5)
            table.scale(1, 1.2)
            
            for i in range(2):
                table[(0, i)].set_facecolor('#4CAF50')
                table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Save
        plt.savefig(output_path, dpi=300, bbox_inches='tight',
                   pad_inches=0.2, facecolor='white', edgecolor='none')
        plt.close()
        
        logger.info(f"Professional aspect map saved: {output_path}")
        return output_path
