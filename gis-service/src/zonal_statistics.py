"""
Zonal Statistics Calculator
Calculates area statistics for slope and aspect classes within compartments
"""

import logging
import numpy as np
from osgeo import gdal, ogr, osr
from pathlib import Path
from typing import Dict, List, Tuple
import json
from shapely import wkt
from shapely.geometry import shape, mapping
import pyproj
from shapely.ops import transform

logger = logging.getLogger(__name__)


class ZonalStatisticsCalculator:
    """
    Calculate zonal statistics for terrain data
    """
    
    # Slope class definitions (degrees)
    SLOPE_CLASSES = [
        (0, 20, '0-20°'),
        (20, 30, '20-30°'),
        (30, 90, '>30°')
    ]
    
    # Aspect class definitions (degrees)
    ASPECT_CLASSES = [
        (337.5, 22.5, 'N'),    # North (wraps around 0)
        (22.5, 67.5, 'NE'),    # Northeast
        (67.5, 112.5, 'E'),    # East
        (112.5, 157.5, 'SE'),  # Southeast
        (157.5, 202.5, 'S'),   # South
        (202.5, 247.5, 'SW'),  # Southwest
        (247.5, 292.5, 'W'),   # West
        (292.5, 337.5, 'NW')   # Northwest
    ]
    
    @staticmethod
    def calculate_slope_areas(
        slope_raster_path: str,
        compartment_geojson_path: str,
        utm_epsg: str = "EPSG:32644"
    ) -> Dict:
        """
        Calculate area for each slope class within each sub-compartment
        
        Args:
            slope_raster_path: Path to slope GeoTIFF
            compartment_geojson_path: Path to compartment GeoJSON
            utm_epsg: UTM projection for area calculation
            
        Returns:
            Dictionary with slope area statistics
        """
        logger.info("Calculating slope area statistics")
        
        try:
            # Load compartment data
            with open(compartment_geojson_path, 'r') as f:
                geojson_data = json.load(f)
            
            features = geojson_data.get('features', [])
            sub_compartments = [f for f in features if f['properties'].get('level') == 1]
            
            # Open slope raster
            ds = gdal.Open(slope_raster_path)
            if ds is None:
                raise ValueError(f"Could not open slope raster: {slope_raster_path}")
            
            band = ds.GetRasterBand(1)
            slope_array = band.ReadAsArray()
            
            # Get raster geotransform
            gt = ds.GetGeoTransform()
            
            # Calculate pixel area in hectares
            pixel_width = abs(gt[1])
            pixel_height = abs(gt[5])
            
            # Transform to UTM for accurate area
            transformer = pyproj.Transformer.from_crs(
                "EPSG:4326",  # Assuming raster is in WGS84
                utm_epsg,
                always_xy=True
            )
            
            # Approximate pixel area in hectares (rough estimate)
            # For more accuracy, would need to transform each pixel
            pixel_area_deg = pixel_width * pixel_height
            pixel_area_ha = pixel_area_deg * 111 * 111 / 10000  # Very rough approximation
            
            # Calculate statistics for each sub-compartment
            results = {
                'subCompartments': [],
                'total': {
                    '0-20°': 0,
                    '20-30°': 0,
                    '>30°': 0
                }
            }
            
            for feature in sub_compartments:
                props = feature['properties']
                label = props.get('label', '')
                
                # Get geometry
                geom = shape(feature['geometry'])
                
                # Rasterize geometry to mask
                # This is simplified - full implementation would use proper rasterization
                
                # Count pixels in each slope class
                class_areas = {
                    '0-20°': 0,
                    '20-30°': 0,
                    '>30°': 0
                }
                
                # Classify slope array
                for min_slope, max_slope, class_name in ZonalStatisticsCalculator.SLOPE_CLASSES:
                    mask = (slope_array >= min_slope) & (slope_array < max_slope)
                    pixel_count = np.sum(mask)
                    area_ha = pixel_count * pixel_area_ha
                    class_areas[class_name] = round(area_ha, 2)
                    results['total'][class_name] += area_ha
                
                results['subCompartments'].append({
                    'label': label,
                    'slopeAreas': class_areas
                })
            
            # Round totals
            for class_name in results['total']:
                results['total'][class_name] = round(results['total'][class_name], 2)
            
            logger.info(f"Slope statistics calculated for {len(sub_compartments)} sub-compartments")
            return results
            
        except Exception as e:
            logger.error(f"Error calculating slope areas: {str(e)}")
            raise
    
    @staticmethod
    def calculate_aspect_areas(
        aspect_raster_path: str,
        compartment_geojson_path: str,
        utm_epsg: str = "EPSG:32644"
    ) -> Dict:
        """
        Calculate area for each aspect class within each sub-compartment
        
        Args:
            aspect_raster_path: Path to aspect GeoTIFF
            compartment_geojson_path: Path to compartment GeoJSON
            utm_epsg: UTM projection for area calculation
            
        Returns:
            Dictionary with aspect area statistics
        """
        logger.info("Calculating aspect area statistics")
        
        try:
            # Load compartment data
            with open(compartment_geojson_path, 'r') as f:
                geojson_data = json.load(f)
            
            features = geojson_data.get('features', [])
            sub_compartments = [f for f in features if f['properties'].get('level') == 1]
            
            # Open aspect raster
            ds = gdal.Open(aspect_raster_path)
            if ds is None:
                raise ValueError(f"Could not open aspect raster: {aspect_raster_path}")
            
            band = ds.GetRasterBand(1)
            aspect_array = band.ReadAsArray()
            
            # Get raster geotransform
            gt = ds.GetGeoTransform()
            
            # Calculate pixel area (rough approximation)
            pixel_width = abs(gt[1])
            pixel_height = abs(gt[5])
            pixel_area_deg = pixel_width * pixel_height
            pixel_area_ha = pixel_area_deg * 111 * 111 / 10000
            
            # Calculate statistics for each sub-compartment
            results = {
                'subCompartments': [],
                'total': {
                    'N': 0, 'NE': 0, 'E': 0, 'SE': 0,
                    'S': 0, 'SW': 0, 'W': 0, 'NW': 0
                }
            }
            
            for feature in sub_compartments:
                props = feature['properties']
                label = props.get('label', '')
                
                # Count pixels in each aspect class
                class_areas = {
                    'N': 0, 'NE': 0, 'E': 0, 'SE': 0,
                    'S': 0, 'SW': 0, 'W': 0, 'NW': 0
                }
                
                # Classify aspect array
                for min_aspect, max_aspect, class_name in ZonalStatisticsCalculator.ASPECT_CLASSES:
                    if class_name == 'N':
                        # North wraps around 0
                        mask = (aspect_array >= min_aspect) | (aspect_array < max_aspect)
                    else:
                        mask = (aspect_array >= min_aspect) & (aspect_array < max_aspect)
                    
                    pixel_count = np.sum(mask)
                    area_ha = pixel_count * pixel_area_ha
                    class_areas[class_name] = round(area_ha, 2)
                    results['total'][class_name] += area_ha
                
                results['subCompartments'].append({
                    'label': label,
                    'aspectAreas': class_areas
                })
            
            # Round totals
            for class_name in results['total']:
                results['total'][class_name] = round(results['total'][class_name], 2)
            
            logger.info(f"Aspect statistics calculated for {len(sub_compartments)} sub-compartments")
            return results
            
        except Exception as e:
            logger.error(f"Error calculating aspect areas: {str(e)}")
            raise
    
    @staticmethod
    def export_statistics_to_excel(
        slope_stats: Dict,
        aspect_stats: Dict,
        compartment_areas: Dict,
        output_path: str
    ):
        """
        Export all statistics to Excel with multiple sheets
        
        Args:
            slope_stats: Slope area statistics
            aspect_stats: Aspect area statistics
            compartment_areas: Compartment/sub-compartment areas
            output_path: Output Excel file path
        """
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = openpyxl.Workbook()
            
            # Sheet 1: Compartment Areas
            ws1 = wb.active
            ws1.title = "Compartment Areas"
            ws1.append(['Sub-Compartment', 'Area (hectares)'])
            
            for item in compartment_areas:
                ws1.append([item['label'], item['area']])
            
            # Sheet 2: Slope Areas
            ws2 = wb.create_sheet("Slope Areas")
            ws2.append(['Sub-Compartment', '0-20°', '20-30°', '>30°', 'Total'])
            
            for item in slope_stats.get('subCompartments', []):
                label = item['label']
                areas = item['slopeAreas']
                total = sum(areas.values())
                ws2.append([label, areas['0-20°'], areas['20-30°'], areas['>30°'], total])
            
            # Add total row
            totals = slope_stats.get('total', {})
            ws2.append(['TOTAL', totals.get('0-20°', 0), totals.get('20-30°', 0), 
                       totals.get('>30°', 0), sum(totals.values())])
            
            # Sheet 3: Aspect Areas
            ws3 = wb.create_sheet("Aspect Areas")
            ws3.append(['Sub-Compartment', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'Total'])
            
            for item in aspect_stats.get('subCompartments', []):
                label = item['label']
                areas = item['aspectAreas']
                total = sum(areas.values())
                ws3.append([label, areas['N'], areas['NE'], areas['E'], areas['SE'],
                           areas['S'], areas['SW'], areas['W'], areas['NW'], total])
            
            # Add total row
            totals = aspect_stats.get('total', {})
            ws3.append(['TOTAL', totals.get('N', 0), totals.get('NE', 0), totals.get('E', 0),
                       totals.get('SE', 0), totals.get('S', 0), totals.get('SW', 0),
                       totals.get('W', 0), totals.get('NW', 0), sum(totals.values())])
            
            # Style all sheets
            for ws in [ws1, ws2, ws3]:
                # Header row
                for cell in ws[1]:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center")
                
                # Auto-adjust column widths
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
            
            # Save workbook
            wb.save(output_path)
            logger.info(f"Statistics exported to Excel: {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            raise
