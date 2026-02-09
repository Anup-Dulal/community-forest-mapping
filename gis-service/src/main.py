"""
Main entry point for GIS Processing Microservice.
Provides REST API endpoints for GIS operations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_DIR', './uploads')
app.config['DEM_CACHE_DIR'] = os.getenv('DEM_CACHE_DIR', './dem_cache')
app.config['EXPORT_DIR'] = os.getenv('EXPORT_DIR', './exports')

# Create necessary directories
for directory in [app.config['UPLOAD_FOLDER'], app.config['DEM_CACHE_DIR'], app.config['EXPORT_DIR']]:
    os.makedirs(directory, exist_ok=True)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'GIS Processing Microservice'}), 200


@app.route('/api/shapefile/parse', methods=['POST'])
def parse_shapefile():
    """
    Parse uploaded shapefile and extract boundary geometry.
    Expects JSON with shapefile directory path.
    """
    try:
        from src.shapefile_parser import ShapefileParser
        
        data = request.get_json()
        shapefile_dir = data.get('shapefileDir')
        
        if not shapefile_dir:
            return jsonify({'error': 'Missing shapefileDir parameter'}), 400
        
        result = ShapefileParser.parse_shapefile(shapefile_dir)
        return jsonify(result), 200
        
    except FileNotFoundError as e:
        logger.error(f"Shapefile not found: {str(e)}")
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        logger.error(f"Invalid shapefile: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error parsing shapefile: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dem/download', methods=['POST'])
def download_dem():
    """
    Download DEM data for given bounding box.
    Expects JSON with bounding box coordinates and source.
    """
    try:
        from src.dem_downloader import DEMDownloader
        from src.dem_clipper import DEMClipper
        
        data = request.get_json()
        bbox = data.get('bbox')
        source = data.get('source', 'SRTM')
        dem_id = data.get('demId')
        
        if not bbox:
            return jsonify({'error': 'Missing bbox parameter'}), 400
        
        # Download DEM
        downloader = DEMDownloader(app.config['DEM_CACHE_DIR'])
        dem_path = downloader.download_dem(bbox, source)
        
        logger.info(f"DEM downloaded successfully: {dem_path}")
        return jsonify({
            'status': 'success',
            'demId': dem_id,
            'rasterPath': dem_path,
            'source': source
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid DEM download request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error downloading DEM: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dem/clip', methods=['POST'])
def clip_dem():
    """
    Clip DEM raster to boundary polygon.
    Expects JSON with DEM path and boundary geometry.
    """
    try:
        from src.dem_clipper import DEMClipper
        
        data = request.get_json()
        dem_path = data.get('demPath')
        boundary_geometry = data.get('boundaryGeometry')
        
        if not dem_path or not boundary_geometry:
            return jsonify({'error': 'Missing demPath or boundaryGeometry'}), 400
        
        # Clip DEM
        clipper = DEMClipper(app.config['EXPORT_DIR'])
        clipped_path = clipper.clip_dem(dem_path, boundary_geometry)
        
        # Validate clipping
        is_valid = clipper.validate_clipped_dem(clipped_path, boundary_geometry)
        
        logger.info(f"DEM clipped successfully: {clipped_path}")
        return jsonify({
            'status': 'success',
            'clippedRasterPath': clipped_path,
            'isValid': is_valid
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid DEM clipping request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error clipping DEM: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terrain/slope', methods=['POST'])
def calculate_slope():
    """
    Calculate slope from DEM and classify into categories.
    Expects JSON with DEM path.
    """
    try:
        from src.slope_calculator import SlopeCalculator
        
        data = request.get_json()
        dem_path = data.get('demPath')
        analysis_id = data.get('analysisId')
        
        if not dem_path:
            return jsonify({'error': 'Missing demPath parameter'}), 400
        
        # Calculate slope
        calculator = SlopeCalculator(app.config['EXPORT_DIR'])
        slope_path = calculator.calculate_slope(dem_path)
        
        # Classify slope
        classified_path = calculator.classify_slope(slope_path)
        
        logger.info(f"Slope calculation successful: {classified_path}")
        return jsonify({
            'status': 'success',
            'analysisId': analysis_id,
            'slopeRasterPath': classified_path
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid slope calculation request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error calculating slope: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/terrain/aspect', methods=['POST'])
def calculate_aspect():
    """
    Calculate aspect from DEM and classify into cardinal directions.
    Expects JSON with DEM path.
    """
    try:
        from src.aspect_calculator import AspectCalculator
        
        data = request.get_json()
        dem_path = data.get('demPath')
        analysis_id = data.get('analysisId')
        
        if not dem_path:
            return jsonify({'error': 'Missing demPath parameter'}), 400
        
        # Calculate aspect
        calculator = AspectCalculator(app.config['EXPORT_DIR'])
        aspect_path = calculator.calculate_aspect(dem_path)
        
        # Classify aspect
        classified_path = calculator.classify_aspect(aspect_path)
        
        logger.info(f"Aspect calculation successful: {classified_path}")
        return jsonify({
            'status': 'success',
            'analysisId': analysis_id,
            'aspectRasterPath': classified_path
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid aspect calculation request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error calculating aspect: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compartments/generate', methods=['POST'])
def generate_compartments():
    """
    Generate equal-area compartments from boundary polygon.
    Expects JSON with boundary geometry and compartment count.
    """
    try:
        from src.compartment_generator import CompartmentGenerator
        
        data = request.get_json()
        boundary_geometry = data.get('boundaryGeometry')
        num_compartments = data.get('numCompartments', 4)
        analysis_id = data.get('analysisId')
        
        if not boundary_geometry:
            return jsonify({'error': 'Missing boundaryGeometry parameter'}), 400
        
        # Generate compartments
        generator = CompartmentGenerator(app.config['EXPORT_DIR'])
        compartment_path = generator.generate_compartments(boundary_geometry, num_compartments)
        
        # Get statistics
        stats = generator.get_compartment_statistics(compartment_path)
        
        logger.info(f"Compartment generation successful: {compartment_path}")
        return jsonify({
            'status': 'success',
            'analysisId': analysis_id,
            'compartmentGeometryPath': compartment_path,
            'statistics': stats
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid compartment generation request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating compartments: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sample-plots/generate', methods=['POST'])
def generate_sample_plots():
    """
    Generate sample plots for compartments.
    Expects JSON with compartment geometries and sampling parameters.
    """
    try:
        from src.sample_plot_generator import SamplePlotGenerator
        
        data = request.get_json()
        compartment_geometry_path = data.get('compartmentGeometryPath')
        sampling_intensity = data.get('samplingIntensity', 0.02)
        min_plots = data.get('minPlotsPerCompartment', 5)
        distribution_method = data.get('distributionMethod', 'systematic')
        analysis_id = data.get('analysisId')
        
        if not compartment_geometry_path:
            return jsonify({'error': 'Missing compartmentGeometryPath parameter'}), 400
        
        # Generate sample plots
        generator = SamplePlotGenerator(app.config['EXPORT_DIR'])
        sample_plot_path = generator.generate_sample_plots(
            compartment_geometry_path,
            sampling_intensity,
            min_plots,
            distribution_method
        )
        
        # Get statistics
        stats = generator.get_sample_plot_statistics(sample_plot_path)
        
        logger.info(f"Sample plot generation successful: {sample_plot_path}")
        return jsonify({
            'status': 'success',
            'analysisId': analysis_id,
            'samplePlotGeometryPath': sample_plot_path,
            'statistics': stats
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid sample plot generation request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating sample plots: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/coordinates/convert', methods=['POST'])
def convert_coordinates():
    """
    Convert coordinates between lat/lon and UTM/UPS systems.
    Expects JSON with coordinates and target system.
    """
    try:
        from src.coordinate_converter import CoordinateConverter
        
        data = request.get_json()
        conversion_type = data.get('conversionType')  # 'lat_lon_to_utm' or 'utm_to_lat_lon'
        
        converter = CoordinateConverter()
        
        if conversion_type == 'lat_lon_to_utm':
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude is None or longitude is None:
                return jsonify({'error': 'Missing latitude or longitude'}), 400
            
            result = converter.lat_lon_to_utm(latitude, longitude)
            
        elif conversion_type == 'utm_to_lat_lon':
            easting = data.get('easting')
            northing = data.get('northing')
            utm_zone = data.get('utmZone')
            is_southern = data.get('isSouthern', False)
            
            if easting is None or northing is None or utm_zone is None:
                return jsonify({'error': 'Missing easting, northing, or utmZone'}), 400
            
            result = converter.utm_to_lat_lon(easting, northing, utm_zone, is_southern)
            
        elif conversion_type == 'validate_round_trip':
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            tolerance = data.get('toleranceMeters', 1.0)
            
            if latitude is None or longitude is None:
                return jsonify({'error': 'Missing latitude or longitude'}), 400
            
            result = converter.validate_round_trip(latitude, longitude, tolerance)
            
        else:
            return jsonify({'error': 'Invalid conversionType parameter'}), 400
        
        logger.info(f"Coordinate conversion successful: {conversion_type}")
        return jsonify({
            'status': 'success',
            'conversionType': conversion_type,
            'result': result
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid coordinate conversion request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error converting coordinates: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/maps/render', methods=['POST'])
def render_map():
    """
    Render map with forestry-standard layout.
    Expects JSON with map data and export format.
    """
    try:
        from src.map_renderer import MapRenderer
        
        data = request.get_json()
        map_type = data.get('mapType')  # 'slope', 'aspect', 'compartment', 'sample_plots'
        boundary_path = data.get('boundaryPath')
        output_format = data.get('outputFormat', 'png')
        analysis_id = data.get('analysisId')
        
        if not boundary_path or not map_type:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        renderer = MapRenderer(app.config['EXPORT_DIR'])
        
        if map_type == 'slope':
            slope_raster_path = data.get('slopeRasterPath')
            compartment_path = data.get('compartmentPath')
            map_path = renderer.render_slope_map(
                boundary_path,
                slope_raster_path,
                compartment_path,
                output_format=output_format
            )
        elif map_type == 'aspect':
            aspect_raster_path = data.get('aspectRasterPath')
            compartment_path = data.get('compartmentPath')
            map_path = renderer.render_aspect_map(
                boundary_path,
                aspect_raster_path,
                compartment_path,
                output_format=output_format
            )
        elif map_type == 'compartment':
            compartment_path = data.get('compartmentPath')
            map_path = renderer.render_compartment_map(
                boundary_path,
                compartment_path,
                output_format=output_format
            )
        elif map_type == 'sample_plots':
            compartment_path = data.get('compartmentPath')
            sample_plot_path = data.get('samplePlotPath')
            map_path = renderer.render_sample_plot_map(
                boundary_path,
                compartment_path,
                sample_plot_path,
                output_format=output_format
            )
        else:
            return jsonify({'error': 'Invalid map type'}), 400
        
        logger.info(f"Map rendered successfully: {map_path}")
        return jsonify({
            'status': 'success',
            'analysisId': analysis_id,
            'mapType': map_type,
            'mapPath': map_path,
            'outputFormat': output_format
        }), 200
        
    except ValueError as e:
        logger.error(f"Invalid map rendering request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error rendering map: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
