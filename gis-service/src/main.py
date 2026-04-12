from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict
import os
import logging
from pathlib import Path
import json
import pandas as pd

# Import our modules
from src.dem_downloader import download_dem
from src.slope_calculator import SlopeCalculator
from src.aspect_calculator import AspectCalculator
from src.shapefile_parser import ShapefileParser
from src.compartment_generator import CompartmentGenerator
from src.sample_plot_generator import SamplePlotGenerator
from src.tile_server import TerrainTileServer
from src.hierarchical_compartment_generator import HierarchicalCompartmentGenerator
from src.hierarchical_sample_plot_generator import HierarchicalSamplePlotGenerator
from src.map_layout_generator import MapLayoutGenerator, SlopeMapLayoutGenerator, AspectMapLayoutGenerator
from src.professional_map_layout import ProfessionalMapLayout, ProfessionalSlopeMapLayout, ProfessionalAspectMapLayout
from src.zonal_statistics import ZonalStatisticsCalculator
from src.export_utilities import GPXExporter, PolygonVertexExporter, EnhancedSamplePlotExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="GIS Service API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
BASE_DIR = Path("/app")
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"Uploads directory: {UPLOADS_DIR}")
logger.info(f"Exports directory: {EXPORTS_DIR}")

# Initialize calculators
slope_calculator = SlopeCalculator(export_dir=str(EXPORTS_DIR))
aspect_calculator = AspectCalculator(export_dir=str(EXPORTS_DIR))
compartment_generator = CompartmentGenerator(export_dir=str(EXPORTS_DIR))
sample_plot_generator = SamplePlotGenerator(export_dir=str(EXPORTS_DIR))
hierarchical_sample_plot_generator = HierarchicalSamplePlotGenerator(export_dir=str(EXPORTS_DIR))

# Pydantic models
class DEMRequest(BaseModel):
    analysisId: str
    bounds: Dict[str, float]

class TerrainRequest(BaseModel):
    analysisId: str

class ShapefileParseRequest(BaseModel):
    shapefileDir: str

class CompartmentRequest(BaseModel):
    analysisId: str
    boundaryGeometry: Dict
    numCompartments: int

class SamplePlotRequest(BaseModel):
    analysisId: str
    compartmentGeometryPath: str
    samplingIntensity: float = 0.01
    minPlotsPerCompartment: int = 5
    distributionMethod: str = "systematic"

class WKTToGeoJSONRequest(BaseModel):
    wkt: str

class HierarchicalCompartmentRequest(BaseModel):
    boundaryWkt: str
    analysisId: str
    compartments: list  # List of {compartmentNumber: int, subCompartmentCount: int}

@app.get("/")
async def root():
    return {"message": "GIS Service API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/shapefile/parse")
async def parse_shapefile(request: ShapefileParseRequest):
    try:
        logger.info(f"Shapefile parse request for directory: {request.shapefileDir}")
        
        # Parse shapefile
        result = ShapefileParser.parse_shapefile(request.shapefileDir)
        
        logger.info(f"Shapefile parsed successfully")
        
        return result
    except FileNotFoundError as e:
        logger.error(f"Shapefile not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid shapefile: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error parsing shapefile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/shapefile/wkt-to-geojson")
async def wkt_to_geojson(request: WKTToGeoJSONRequest):
    try:
        from shapely import wkt
        from shapely.geometry import mapping
        
        logger.info(f"WKT to GeoJSON conversion request")
        
        # Parse WKT
        geometry = wkt.loads(request.wkt)
        
        # Convert to GeoJSON
        geojson_geometry = mapping(geometry)
        
        # Get bounding box
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        bbox = [bounds[0], bounds[1], bounds[2], bounds[3]]
        
        logger.info(f"WKT converted to GeoJSON successfully")
        
        return {
            "geometry": geojson_geometry,
            "bbox": bbox
        }
    except Exception as e:
        logger.error(f"Error converting WKT to GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compartments/generate")
async def generate_compartments(request: CompartmentRequest):
    try:
        logger.info(f"Compartment generation request for analysis: {request.analysisId}")
        logger.info(f"Number of compartments: {request.numCompartments}")
        
        # Create output directory
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output path for compartments
        output_path = str(output_dir / f"compartments_{request.analysisId}.geojson")
        
        # Generate compartments
        result_path = compartment_generator.generate_compartments(
            boundary_geometry=request.boundaryGeometry,
            num_compartments=request.numCompartments,
            output_path=output_path
        )
        
        logger.info(f"Compartments generated successfully: {result_path}")
        
        return {
            "status": "success",
            "message": "Compartments generated successfully",
            "compartmentGeometryPath": result_path,
            "geometryPath": result_path,  # Also include for compatibility
            "analysisId": request.analysisId,
            "numCompartments": request.numCompartments,
            "statistics": {
                "num_compartments": request.numCompartments
            }
        }
    except Exception as e:
        logger.error(f"Error generating compartments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compartments/generate-hierarchical")
async def generate_hierarchical_compartments(request: HierarchicalCompartmentRequest):
    """
    Generate compartments with sub-compartments in hierarchical structure
    
    Example request:
    {
        "boundaryWkt": "POLYGON((...))",
        "analysisId": "uuid",
        "compartments": [
            {"compartmentNumber": 1, "subCompartmentCount": 8},
            {"compartmentNumber": 2, "subCompartmentCount": 4}
        ]
    }
    """
    try:
        logger.info(f"Hierarchical compartment generation request for analysis: {request.analysisId}")
        logger.info(f"Compartment specs: {request.compartments}")
        
        # Generate hierarchical compartments
        result = HierarchicalCompartmentGenerator.generate(
            boundary_wkt=request.boundaryWkt,
            analysis_id=request.analysisId,
            compartment_specs=request.compartments,
            exports_dir=EXPORTS_DIR
        )
        
        # Convert to dict format for JSON response
        compartments_dict = HierarchicalCompartmentGenerator.convert_to_dict_list(
            result.compartments
        )
        
        logger.info(f"Hierarchical compartments generated successfully")
        
        return {
            "status": "success",
            "message": "Hierarchical compartments generated successfully",
            "compartments": compartments_dict,
            "statistics": result.statistics,
            "compartmentGeometryPath": result.output_path,
            "geometryPath": result.output_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error generating hierarchical compartments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sample-plots/generate")
async def generate_sample_plots(request: SamplePlotRequest):
    try:
        logger.info(f"Sample plot generation request for analysis: {request.analysisId}")
        logger.info(f"Compartment geometry path: {request.compartmentGeometryPath}")
        logger.info(f"Sampling intensity: {request.samplingIntensity}")
        
        # Output path for sample plots
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"sample_plots_{request.analysisId}.geojson")
        
        # Generate sample plots
        result_path = sample_plot_generator.generate_sample_plots(
            compartment_geometry_path=request.compartmentGeometryPath,
            sampling_intensity=request.samplingIntensity,
            min_plots_per_compartment=request.minPlotsPerCompartment,
            distribution_method=request.distributionMethod
        )
        
        logger.info(f"Sample plots generated successfully: {result_path}")
        
        # Get statistics
        stats = sample_plot_generator.get_sample_plot_statistics(result_path)
        
        return {
            "status": "success",
            "message": "Sample plots generated successfully",
            "samplePlotGeometryPath": result_path,
            "analysisId": request.analysisId,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error generating sample plots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sample-plots/generate-hierarchical")
async def generate_hierarchical_sample_plots(request: SamplePlotRequest):
    """
    Generate sample plots for hierarchical compartments (sub-compartments).
    Ensures minimum 5 plots per SUB-COMPARTMENT (not compartment).
    """
    try:
        logger.info(f"Hierarchical sample plot generation request for analysis: {request.analysisId}")
        logger.info(f"Compartment geometry path: {request.compartmentGeometryPath}")
        logger.info(f"Sampling intensity: {request.samplingIntensity}")
        logger.info(f"Min plots per sub-compartment: {request.minPlotsPerCompartment}")
        
        # Generate sample plots using hierarchical generator
        result_path = hierarchical_sample_plot_generator.generate_sample_plots(
            compartment_geometry_path=request.compartmentGeometryPath,
            analysis_id=request.analysisId,
            sampling_intensity=request.samplingIntensity,
            min_plots_per_subcompartment=request.minPlotsPerCompartment,
            distribution_method=request.distributionMethod
        )
        
        logger.info(f"Hierarchical sample plots generated successfully: {result_path}")
        
        # Get statistics
        stats = hierarchical_sample_plot_generator.get_sample_plot_statistics(result_path)
        
        return {
            "status": "success",
            "message": "Hierarchical sample plots generated successfully",
            "samplePlotGeometryPath": result_path,
            "analysisId": request.analysisId,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error generating hierarchical sample plots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class DEMDownloadRequest(BaseModel):
    demId: str
    source: str
    bbox: Dict[str, float]

@app.post("/api/dem/download")
async def download_dem_api_endpoint(request: DEMDownloadRequest):
    """Backend-compatible DEM download endpoint"""
    try:
        logger.info(f"DEM download request for DEM ID: {request.demId}")
        logger.info(f"Source: {request.source}, Bounds: {request.bbox}")
        
        # Create output directory using demId
        output_dir = EXPORTS_DIR / request.demId
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output path for DEM
        output_path = str(output_dir / f"dem_clipped_{request.demId}.tif")
        
        # Convert bbox to bounds format
        bounds_dict = {
            'minLon': request.bbox['minLon'],
            'minLat': request.bbox['minLat'],
            'maxLon': request.bbox['maxLon'],
            'maxLat': request.bbox['maxLat']
        }
        
        # Download DEM
        result_path = download_dem(bounds_dict, output_path)
        
        logger.info(f"DEM downloaded successfully: {result_path}")
        
        return {
            "status": "success",
            "message": "DEM downloaded successfully",
            "rasterPath": result_path,
            "demId": request.demId
        }
    except Exception as e:
        logger.error(f"Error downloading DEM: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/download-dem")
async def download_dem_endpoint(request: DEMRequest):
    try:
        logger.info(f"DEM download request for analysis: {request.analysisId}")
        logger.info(f"Bounds: {request.bounds}")
        
        # Create output directory
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output path for DEM
        output_path = str(output_dir / f"dem_clipped_{request.analysisId}.tif")
        
        # Convert bounds to dict format expected by download_dem
        bounds_dict = {
            'minLon': request.bounds['minLon'],
            'minLat': request.bounds['minLat'],
            'maxLon': request.bounds['maxLon'],
            'maxLat': request.bounds['maxLat']
        }
        
        # Download DEM
        result_path = download_dem(bounds_dict, output_path)
        
        logger.info(f"DEM downloaded successfully: {result_path}")
        
        return {
            "message": "DEM downloaded successfully",
            "path": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error downloading DEM: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-slope")
async def calculate_slope_endpoint(request: TerrainRequest):
    try:
        logger.info(f"Slope calculation request for analysis: {request.analysisId}")
        
        # Find DEM file - try analysis directory first, then check all directories
        dem_dir = EXPORTS_DIR / request.analysisId
        dem_path = dem_dir / f"dem_clipped_{request.analysisId}.tif"
        
        if not dem_path.exists():
            # DEM might be in a different directory (demId), search for it
            logger.warning(f"DEM not found in analysis directory, searching...")
            for subdir in EXPORTS_DIR.iterdir():
                if subdir.is_dir():
                    potential_dem = subdir / f"dem_clipped_{subdir.name}.tif"
                    if potential_dem.exists():
                        logger.info(f"Found DEM in {subdir.name}, copying to analysis directory...")
                        dem_dir.mkdir(parents=True, exist_ok=True)
                        import shutil
                        shutil.copy(potential_dem, dem_path)
                        break
        
        if not dem_path.exists():
            raise HTTPException(status_code=404, detail="DEM file not found")
        
        # Output path for slope
        slope_path = str(dem_dir / f"slope_{request.analysisId}.tif")
        
        # Calculate slope
        result_path = slope_calculator.calculate_slope(str(dem_path), slope_path)
        
        logger.info(f"Slope calculated successfully: {result_path}")
        
        return {
            "status": "success",
            "message": "Slope calculated successfully",
            "slopeRasterPath": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error calculating slope: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-aspect")
async def calculate_aspect_endpoint(request: TerrainRequest):
    try:
        logger.info(f"Aspect calculation request for analysis: {request.analysisId}")
        
        # Find DEM file - try analysis directory first, then check all directories
        dem_dir = EXPORTS_DIR / request.analysisId
        dem_path = dem_dir / f"dem_clipped_{request.analysisId}.tif"
        
        if not dem_path.exists():
            # DEM might be in a different directory (demId), search for it
            logger.warning(f"DEM not found in analysis directory, searching...")
            for subdir in EXPORTS_DIR.iterdir():
                if subdir.is_dir():
                    potential_dem = subdir / f"dem_clipped_{subdir.name}.tif"
                    if potential_dem.exists():
                        logger.info(f"Found DEM in {subdir.name}, copying to analysis directory...")
                        dem_dir.mkdir(parents=True, exist_ok=True)
                        import shutil
                        shutil.copy(potential_dem, dem_path)
                        break
        
        if not dem_path.exists():
            raise HTTPException(status_code=404, detail="DEM file not found")
        
        # Output path for aspect
        aspect_path = str(dem_dir / f"aspect_{request.analysisId}.tif")
        
        # Calculate aspect
        result_path = aspect_calculator.calculate_aspect(str(dem_path), aspect_path)
        
        logger.info(f"Aspect calculated successfully: {result_path}")
        
        return {
            "status": "success",
            "message": "Aspect calculated successfully",
            "aspectRasterPath": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error calculating aspect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/shapefile/{shapefile_id}/boundary")
async def get_boundary(shapefile_id: str):
    """Get boundary GeoJSON for a shapefile"""
    try:
        logger.info(f"Boundary request for shapefile: {shapefile_id}")
        
        # Look for shapefile in uploads directory
        shapefile_dir = UPLOADS_DIR / shapefile_id
        
        if not shapefile_dir.exists():
            logger.error(f"Shapefile directory not found: {shapefile_dir}")
            raise HTTPException(status_code=404, detail="Shapefile not found")
        
        # Parse shapefile to get boundary
        result = ShapefileParser.parse_shapefile(str(shapefile_dir))
        
        if 'boundaryGeometry' not in result:
            raise HTTPException(status_code=404, detail="Boundary geometry not found")
        
        logger.info(f"Boundary retrieved successfully for shapefile: {shapefile_id}")
        
        return {
            "type": "Feature",
            "geometry": result['boundaryGeometry'],
            "properties": {
                "shapefileId": shapefile_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting boundary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/geojson/compartment")
async def get_compartment_geojson(analysisId: str):
    """Get compartment GeoJSON for an analysis"""
    try:
        logger.info(f"Compartment GeoJSON request for analysis: {analysisId}")
        
        # Find compartment file
        compartment_path = EXPORTS_DIR / analysisId / f"compartments_{analysisId}.geojson"
        
        if not compartment_path.exists():
            logger.error(f"Compartment file not found: {compartment_path}")
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Read and return GeoJSON
        import json
        with open(compartment_path, 'r') as f:
            geojson_data = json.load(f)
        
        logger.info(f"Compartment GeoJSON retrieved successfully")
        
        return geojson_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compartment GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/geojson/samplePlot")
async def get_sample_plot_geojson(analysisId: str):
    """Get sample plot GeoJSON for an analysis"""
    try:
        logger.info(f"Sample plot GeoJSON request for analysis: {analysisId}")
        
        # Find sample plot file
        sample_plot_path = EXPORTS_DIR / analysisId / f"sample_plots_{analysisId}.geojson"
        
        if not sample_plot_path.exists():
            logger.error(f"Sample plot file not found: {sample_plot_path}")
            raise HTTPException(status_code=404, detail="Sample plot data not found")
        
        # Read and return GeoJSON
        import json
        with open(sample_plot_path, 'r') as f:
            geojson_data = json.load(f)
        
        logger.info(f"Sample plot GeoJSON retrieved successfully")
        
        return geojson_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sample plot GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/geojson/dem")
async def get_dem_geojson(analysisId: str):
    """Get DEM as GeoJSON - returns metadata since raster-to-vector conversion is complex"""
    try:
        logger.info(f"DEM GeoJSON request for analysis: {analysisId}")
        
        # Find DEM file
        dem_path = EXPORTS_DIR / analysisId / f"dem_clipped_{analysisId}.tif"
        
        if not dem_path.exists():
            logger.warning(f"DEM file not found: {dem_path} - returning empty GeoJSON")
            return {
                "type": "FeatureCollection",
                "features": [],
                "properties": {
                    "message": "DEM data not available. Click 'Generate Maps' to download.",
                    "available": False
                }
            }
        
        # Get file stats
        file_size = dem_path.stat().st_size
        
        # Return metadata indicating DEM is available
        logger.info(f"DEM file found: {dem_path} ({file_size} bytes)")
        return {
            "type": "FeatureCollection",
            "features": [],
            "properties": {
                "message": "DEM raster available",
                "available": True,
                "fileSizeBytes": file_size,
                "note": "DEM is stored as raster (GeoTIFF). Use raster tile server for visualization."
            }
        }
    except Exception as e:
        logger.error(f"Error getting DEM GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/geojson/slope")
async def get_slope_geojson(analysisId: str):
    """Get slope as GeoJSON - returns metadata since raster-to-vector conversion is complex"""
    try:
        logger.info(f"Slope GeoJSON request for analysis: {analysisId}")
        
        # Find slope file
        slope_path = EXPORTS_DIR / analysisId / f"slope_{analysisId}.tif"
        
        if not slope_path.exists():
            logger.warning(f"Slope file not found: {slope_path} - returning empty GeoJSON")
            return {
                "type": "FeatureCollection",
                "features": [],
                "properties": {
                    "message": "Slope data not available. Click 'Generate Maps' to calculate.",
                    "available": False
                }
            }
        
        # Get file stats
        file_size = slope_path.stat().st_size
        
        # Return metadata indicating slope is available
        logger.info(f"Slope file found: {slope_path} ({file_size} bytes)")
        return {
            "type": "FeatureCollection",
            "features": [],
            "properties": {
                "message": "Slope raster available",
                "available": True,
                "fileSizeBytes": file_size,
                "note": "Slope is stored as raster (GeoTIFF). Use raster tile server for visualization."
            }
        }
    except Exception as e:
        logger.error(f"Error getting slope GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/geojson/aspect")
async def get_aspect_geojson(analysisId: str):
    """Get aspect as GeoJSON - returns metadata since raster-to-vector conversion is complex"""
    try:
        logger.info(f"Aspect GeoJSON request for analysis: {analysisId}")
        
        # Find aspect file
        aspect_path = EXPORTS_DIR / analysisId / f"aspect_{analysisId}.tif"
        
        if not aspect_path.exists():
            logger.warning(f"Aspect file not found: {aspect_path} - returning empty GeoJSON")
            return {
                "type": "FeatureCollection",
                "features": [],
                "properties": {
                    "message": "Aspect data not available. Click 'Generate Maps' to calculate.",
                    "available": False
                }
            }
        
        # Get file stats
        file_size = aspect_path.stat().st_size
        
        # Return metadata indicating aspect is available
        logger.info(f"Aspect file found: {aspect_path} ({file_size} bytes)")
        return {
            "type": "FeatureCollection",
            "features": [],
            "properties": {
                "message": "Aspect raster available",
                "available": True,
                "fileSizeBytes": file_size,
                "note": "Aspect is stored as raster (GeoTIFF). Use raster tile server for visualization."
            }
        }
    except Exception as e:
        logger.error(f"Error getting aspect GeoJSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TILE SERVER ENDPOINTS - Professional raster visualization using GDAL
# ============================================================================

def get_raster_info(raster_path: str):
    """Get raster metadata using GDAL"""
    from osgeo import gdal
    
    ds = gdal.Open(raster_path)
    if ds is None:
        raise ValueError(f"Could not open raster: {raster_path}")
    
    # Get bounds
    transform = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize
    
    minx = transform[0]
    maxy = transform[3]
    maxx = minx + width * transform[1]
    miny = maxy + height * transform[5]
    
    # Get statistics
    band = ds.GetRasterBand(1)
    stats = band.GetStatistics(True, True)
    
    return {
        "bounds": [minx, miny, maxx, maxy],
        "width": width,
        "height": height,
        "statistics": {
            "min": stats[0],
            "max": stats[1],
            "mean": stats[2],
            "stddev": stats[3]
        }
    }

@app.get("/api/terrain/{analysis_id}/metadata")
async def get_terrain_metadata(analysis_id: str):
    """Get metadata for all terrain layers"""
    try:
        metadata = {
            "analysisId": analysis_id,
            "layers": {}
        }
        
        # Check DEM
        dem_path = EXPORTS_DIR / analysis_id / f"dem_clipped_{analysis_id}.tif"
        if dem_path.exists():
            try:
                info = get_raster_info(str(dem_path))
                metadata["layers"]["dem"] = {
                    "available": True,
                    "bounds": info["bounds"],
                    "statistics": info["statistics"],
                    "fileSizeBytes": dem_path.stat().st_size
                }
            except Exception as e:
                logger.error(f"Error getting DEM info: {str(e)}")
                metadata["layers"]["dem"] = {"available": False, "error": str(e)}
        
        # Check Slope
        slope_path = EXPORTS_DIR / analysis_id / f"slope_{analysis_id}.tif"
        if slope_path.exists():
            try:
                info = get_raster_info(str(slope_path))
                metadata["layers"]["slope"] = {
                    "available": True,
                    "bounds": info["bounds"],
                    "statistics": info["statistics"],
                    "fileSizeBytes": slope_path.stat().st_size
                }
            except Exception as e:
                logger.error(f"Error getting slope info: {str(e)}")
                metadata["layers"]["slope"] = {"available": False, "error": str(e)}
        
        # Check Aspect
        aspect_path = EXPORTS_DIR / analysis_id / f"aspect_{analysis_id}.tif"
        if aspect_path.exists():
            try:
                info = get_raster_info(str(aspect_path))
                metadata["layers"]["aspect"] = {
                    "available": True,
                    "bounds": info["bounds"],
                    "statistics": info["statistics"],
                    "fileSizeBytes": aspect_path.stat().st_size
                }
            except Exception as e:
                logger.error(f"Error getting aspect info: {str(e)}")
                metadata["layers"]["aspect"] = {"available": False, "error": str(e)}
        
        return metadata
    except Exception as e:
        logger.error(f"Error getting terrain metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GOOGLE MAPS-STYLE TILE ENDPOINTS
# ============================================================================

@app.get("/api/tiles/dem/{analysis_id}/{z}/{x}/{y}.png")
async def get_dem_tile(analysis_id: str, z: int, x: int, y: int):
    """Get DEM tile in Google Maps format (z/x/y)"""
    try:
        dem_path = EXPORTS_DIR / analysis_id / f"dem_clipped_{analysis_id}.tif"
        
        if not dem_path.exists():
            raise HTTPException(status_code=404, detail="DEM not found")
        
        tile_data = TerrainTileServer.get_dem_tile(str(dem_path), z, x, y)
        
        return Response(content=tile_data, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating DEM tile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tiles/slope/{analysis_id}/{z}/{x}/{y}.png")
async def get_slope_tile(analysis_id: str, z: int, x: int, y: int):
    """Get slope tile in Google Maps format (z/x/y)"""
    try:
        slope_path = EXPORTS_DIR / analysis_id / f"slope_{analysis_id}.tif"
        
        if not slope_path.exists():
            raise HTTPException(status_code=404, detail="Slope not found")
        
        tile_data = TerrainTileServer.get_slope_tile(str(slope_path), z, x, y)
        
        return Response(content=tile_data, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating slope tile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tiles/aspect/{analysis_id}/{z}/{x}/{y}.png")
async def get_aspect_tile(analysis_id: str, z: int, x: int, y: int):
    """Get aspect tile in Google Maps format (z/x/y)"""
    try:
        aspect_path = EXPORTS_DIR / analysis_id / f"aspect_{analysis_id}.tif"
        
        if not aspect_path.exists():
            raise HTTPException(status_code=404, detail="Aspect not found")
        
        tile_data = TerrainTileServer.get_aspect_tile(str(aspect_path), z, x, y)
        
        return Response(content=tile_data, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating aspect tile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route("/api/tiles/{layer_type}/{analysis_id}/bounds", methods=["GET", "HEAD"])
async def get_layer_bounds(layer_type: str, analysis_id: str):
    """Get bounds for a terrain layer"""
    try:
        layer_map = {
            "dem": f"dem_clipped_{analysis_id}.tif",
            "slope": f"slope_{analysis_id}.tif",
            "aspect": f"aspect_{analysis_id}.tif"
        }
        
        if layer_type not in layer_map:
            raise HTTPException(status_code=400, detail="Invalid layer type")
        
        raster_path = EXPORTS_DIR / analysis_id / layer_map[layer_type]
        
        if not raster_path.exists():
            raise HTTPException(status_code=404, detail=f"{layer_type.upper()} not found")
        
        bounds = TerrainTileServer.get_bounds(str(raster_path))
        stats = TerrainTileServer.get_statistics(str(raster_path))
        
        return {
            "bounds": bounds,
            "statistics": stats,
            "tileUrl": f"/api/tiles/{layer_type}/{analysis_id}/{{z}}/{{x}}/{{y}}.png"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting layer bounds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROFESSIONAL MAP LAYOUT ENDPOINTS
# ============================================================================

class MapLayoutRequest(BaseModel):
    analysisId: str
    cfName: str
    paperSize: str = 'A4'
    includeTable: bool = True

@app.post("/api/maps/layout/compartment")
async def generate_compartment_layout(request: MapLayoutRequest):
    """Generate professional compartment map layout"""
    try:
        logger.info(f"Generating compartment map layout for {request.cfName}")
        
        # Find compartment GeoJSON
        compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_path = str(output_dir / f"compartment_map_{request.analysisId}.pdf")
        
        # Generate layout
        result_path = MapLayoutGenerator.generate_compartment_map(
            compartment_geojson_path=str(compartment_path),
            cf_name=request.cfName,
            output_path=output_path,
            paper_size=request.paperSize,
            include_table=request.includeTable
        )
        
        logger.info(f"Compartment map layout generated: {result_path}")
        
        return {
            "status": "success",
            "message": "Compartment map layout generated",
            "outputPath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating compartment layout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ZONAL STATISTICS ENDPOINTS
# ============================================================================

class ZonalStatsRequest(BaseModel):
    analysisId: str
    utmEpsg: str = "EPSG:32644"

@app.post("/api/statistics/slope")
async def calculate_slope_statistics(request: ZonalStatsRequest):
    """Calculate slope area statistics"""
    try:
        logger.info(f"Calculating slope statistics for analysis {request.analysisId}")
        
        # Find files
        slope_path = EXPORTS_DIR / request.analysisId / f"slope_{request.analysisId}.tif"
        compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        
        if not slope_path.exists():
            raise HTTPException(status_code=404, detail="Slope data not found")
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Calculate statistics
        stats = ZonalStatisticsCalculator.calculate_slope_areas(
            slope_raster_path=str(slope_path),
            compartment_geojson_path=str(compartment_path),
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"Slope statistics calculated successfully")
        
        return {
            "status": "success",
            "statistics": stats,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating slope statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/statistics/aspect")
async def calculate_aspect_statistics(request: ZonalStatsRequest):
    """Calculate aspect area statistics"""
    try:
        logger.info(f"Calculating aspect statistics for analysis {request.analysisId}")
        
        # Find files
        aspect_path = EXPORTS_DIR / request.analysisId / f"aspect_{request.analysisId}.tif"
        compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        
        if not aspect_path.exists():
            raise HTTPException(status_code=404, detail="Aspect data not found")
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Calculate statistics
        stats = ZonalStatisticsCalculator.calculate_aspect_areas(
            aspect_raster_path=str(aspect_path),
            compartment_geojson_path=str(compartment_path),
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"Aspect statistics calculated successfully")
        
        return {
            "status": "success",
            "statistics": stats,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating aspect statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENHANCED EXPORT ENDPOINTS
# ============================================================================

class ExportRequest(BaseModel):
    analysisId: str
    utmEpsg: str = "EPSG:32644"

@app.post("/api/export/gpx")
async def export_sample_plots_gpx(request: ExportRequest):
    """Export sample plots to GPX format"""
    try:
        logger.info(f"Exporting sample plots to GPX for analysis {request.analysisId}")
        
        # Find sample plot file
        sample_plot_path = EXPORTS_DIR / request.analysisId / f"sample_plots_{request.analysisId}.geojson"
        
        if not sample_plot_path.exists():
            raise HTTPException(status_code=404, detail="Sample plot data not found")
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_path = str(output_dir / f"sample_plots_{request.analysisId}.gpx")
        
        # Export to GPX
        result_path = GPXExporter.export_sample_points_to_gpx(
            sample_plot_geojson_path=str(sample_plot_path),
            output_path=output_path,
            cf_name="Community Forest"
        )
        
        logger.info(f"GPX export completed: {result_path}")
        
        return {
            "status": "success",
            "message": "Sample plots exported to GPX",
            "outputPath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to GPX: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/vertices/excel")
async def export_polygon_vertices_excel(request: ExportRequest):
    """Export polygon vertices to Excel"""
    try:
        logger.info(f"Exporting polygon vertices to Excel for analysis {request.analysisId}")
        
        # Find compartment file
        compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_path = str(output_dir / f"polygon_vertices_{request.analysisId}.xlsx")
        
        # Export vertices
        result_path = PolygonVertexExporter.export_vertices_to_excel(
            compartment_geojson_path=str(compartment_path),
            output_path=output_path,
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"Polygon vertices exported to Excel: {result_path}")
        
        return {
            "status": "success",
            "message": "Polygon vertices exported to Excel",
            "outputPath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting vertices to Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/vertices/csv")
async def export_polygon_vertices_csv(request: ExportRequest):
    """Export polygon vertices to CSV"""
    try:
        logger.info(f"Exporting polygon vertices to CSV for analysis {request.analysisId}")
        
        # Find compartment file
        compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_path = str(output_dir / f"polygon_vertices_{request.analysisId}.csv")
        
        # Export vertices
        result_path = PolygonVertexExporter.export_vertices_to_csv(
            compartment_geojson_path=str(compartment_path),
            output_path=output_path,
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"Polygon vertices exported to CSV: {result_path}")
        
        return {
            "status": "success",
            "message": "Polygon vertices exported to CSV",
            "outputPath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting vertices to CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/sample-plots/enhanced")
async def export_sample_plots_enhanced(request: ExportRequest):
    """Export sample plots with enhanced format (includes sub-compartment info)"""
    try:
        logger.info(f"Exporting enhanced sample plots for analysis {request.analysisId}")
        
        # Find sample plot file
        sample_plot_path = EXPORTS_DIR / request.analysisId / f"sample_plots_{request.analysisId}.geojson"
        
        if not sample_plot_path.exists():
            raise HTTPException(status_code=404, detail="Sample plot data not found")
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_path = str(output_dir / f"sample_plots_enhanced_{request.analysisId}.xlsx")
        
        # Export with enhanced format
        result_path = EnhancedSamplePlotExporter.export_to_excel(
            sample_plot_geojson_path=str(sample_plot_path),
            output_path=output_path,
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"Enhanced sample plots exported: {result_path}")
        
        return {
            "status": "success",
            "message": "Sample plots exported with enhanced format",
            "outputPath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting enhanced sample plots: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional export endpoints for backend integration

class MapExportRequest(BaseModel):
    analysisId: str
    compartmentGeometryPath: str
    cfName: str = "Community Forest"
    mapTitle: str = "Compartment Map"
    language: str = "english"  # english or nepali
    format: str = "pdf"  # pdf or png

@app.post("/api/export/map/layout")
async def export_map_layout(request: MapExportRequest):
    """
    Export map with professional layout (PDF or PNG).
    Uses new professional map layout generator with language support.
    """
    try:
        logger.info(f"Map layout export request for analysis: {request.analysisId}")
        logger.info(f"Format: {request.format}, CF Name: {request.cfName}, Language: {request.language}")
        
        # Create output directory
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine output format
        extension = 'pdf' if request.format == 'pdf' else 'png'
        output_path = str(output_dir / f"compartment_map_{request.analysisId}.{extension}")
        
        # Generate map using professional layout
        result_path = ProfessionalMapLayout.generate_compartment_map(
            compartment_geojson_path=request.compartmentGeometryPath,
            cf_name=request.cfName,
            output_path=output_path,
            language=request.language
        )
        
        logger.info(f"Map layout generated: {result_path}")
        
        return {
            "status": "success",
            "message": f"Map exported as {request.format.upper()}",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting map layout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class CoordinateExportRequest(BaseModel):
    analysisId: str
    compartmentGeometryPath: str
    utmEpsg: str = "EPSG:32644"

@app.post("/api/export/coordinates/excel")
async def export_coordinates_excel(request: CoordinateExportRequest):
    """Export polygon vertices to Excel with UTM coordinates."""
    try:
        logger.info(f"Excel coordinate export for analysis: {request.analysisId}")
        
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"coordinates_{request.analysisId}.xlsx")
        
        result_path = PolygonVertexExporter.export_to_excel(
            compartment_geojson_path=request.compartmentGeometryPath,
            output_path=output_path,
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"Excel coordinates exported: {result_path}")
        
        return {
            "status": "success",
            "message": "Coordinates exported to Excel",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting Excel coordinates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/coordinates/csv")
async def export_coordinates_csv(request: CoordinateExportRequest):
    """Export polygon vertices to CSV with UTM coordinates."""
    try:
        logger.info(f"CSV coordinate export for analysis: {request.analysisId}")
        
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"coordinates_{request.analysisId}.csv")
        
        result_path = PolygonVertexExporter.export_to_csv(
            compartment_geojson_path=request.compartmentGeometryPath,
            output_path=output_path,
            utm_epsg=request.utmEpsg
        )
        
        logger.info(f"CSV coordinates exported: {result_path}")
        
        return {
            "status": "success",
            "message": "Coordinates exported to CSV",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting CSV coordinates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class GPXExportRequest(BaseModel):
    analysisId: str
    samplePlotGeometryPath: str

@app.post("/api/export/gpx")
async def export_gpx_file(request: GPXExportRequest):
    """Export sample plots to GPX format for GPS devices."""
    try:
        logger.info(f"GPX export for analysis: {request.analysisId}")
        
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"sample_plots_{request.analysisId}.gpx")
        
        result_path = GPXExporter.export_to_gpx(
            sample_plot_geojson_path=request.samplePlotGeometryPath,
            output_path=output_path
        )
        
        logger.info(f"GPX exported: {result_path}")
        
        return {
            "status": "success",
            "message": "Sample plots exported to GPX",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting GPX: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class TerrainStatisticsRequest(BaseModel):
    analysisId: str
    compartmentGeometryPath: str
    slopeRasterPath: str
    aspectRasterPath: str

@app.get("/api/statistics/terrain")
async def get_terrain_statistics(
    analysisId: str,
    compartmentGeometryPath: str,
    slopeRasterPath: str,
    aspectRasterPath: str
):
    """Calculate slope and aspect statistics for compartments."""
    try:
        logger.info(f"Terrain statistics request for analysis: {analysisId}")
        
        # Calculate slope statistics
        slope_stats = ZonalStatisticsCalculator.calculate_slope_statistics(
            slope_raster_path=slopeRasterPath,
            compartment_geojson_path=compartmentGeometryPath
        )
        
        # Calculate aspect statistics
        aspect_stats = ZonalStatisticsCalculator.calculate_aspect_statistics(
            aspect_raster_path=aspectRasterPath,
            compartment_geojson_path=compartmentGeometryPath
        )
        
        logger.info("Terrain statistics calculated successfully")
        
        return {
            "status": "success",
            "analysisId": analysisId,
            "slopeStatistics": slope_stats,
            "aspectStatistics": aspect_stats
        }
    except Exception as e:
        logger.error(f"Error calculating terrain statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AREA SUMMARY EXPORT ENDPOINTS
# ============================================================================

class AreaExportRequest(BaseModel):
    analysisId: str
    compartmentGeometryPath: str
    slopeRasterPath: str = None
    aspectRasterPath: str = None

@app.post("/api/export/areas/compartments")
async def export_compartment_areas(request: AreaExportRequest):
    """Export compartment and sub-compartment areas to Excel."""
    try:
        logger.info(f"Exporting compartment areas for analysis: {request.analysisId}")
        
        # Read compartment GeoJSON
        import json
        import pandas as pd
        from pathlib import Path
        
        with open(request.compartmentGeometryPath, 'r') as f:
            geojson_data = json.load(f)
        
        # Extract area data
        areas = []
        for feature in geojson_data['features']:
            props = feature['properties']
            areas.append({
                'Compartment': props.get('compartment_number', ''),
                'Sub-Compartment': props.get('label', ''),
                'Level': 'Parent' if props.get('level') == 0 else 'Sub-Compartment',
                'Area (hectares)': round(props.get('area', 0), 2)
            })
        
        # Create DataFrame
        df = pd.DataFrame(areas)
        
        # Sort by compartment and sub-compartment
        df = df.sort_values(['Compartment', 'Sub-Compartment'])
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"compartment_areas_{request.analysisId}.xlsx")
        
        # Export to Excel
        df.to_excel(output_path, index=False, sheet_name='Compartment Areas')
        
        logger.info(f"Compartment areas exported: {output_path}")
        
        return {
            "status": "success",
            "message": "Compartment areas exported to Excel",
            "filePath": output_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting compartment areas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/areas/slope")
async def export_slope_areas(request: AreaExportRequest):
    """Export slope area summary to Excel."""
    try:
        logger.info(f"Exporting slope areas for analysis: {request.analysisId}")
        
        # Calculate slope statistics
        slope_stats = ZonalStatisticsCalculator.calculate_slope_areas(
            slope_raster_path=request.slopeRasterPath,
            compartment_geojson_path=request.compartmentGeometryPath
        )
        
        # Convert to DataFrame
        import pandas as pd
        
        data = []
        for class_name, area in slope_stats.items():
            data.append({
                'Slope Class': class_name,
                'Area (hectares)': round(area, 2)
            })
        
        df = pd.DataFrame(data)
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"slope_areas_{request.analysisId}.xlsx")
        
        # Export to Excel
        df.to_excel(output_path, index=False, sheet_name='Slope Areas')
        
        logger.info(f"Slope areas exported: {output_path}")
        
        return {
            "status": "success",
            "message": "Slope areas exported to Excel",
            "filePath": output_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting slope areas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/areas/aspect")
async def export_aspect_areas(request: AreaExportRequest):
    """Export aspect area summary to Excel."""
    try:
        logger.info(f"Exporting aspect areas for analysis: {request.analysisId}")
        
        # Calculate aspect statistics
        aspect_stats = ZonalStatisticsCalculator.calculate_aspect_areas(
            aspect_raster_path=request.aspectRasterPath,
            compartment_geojson_path=request.compartmentGeometryPath
        )
        
        # Convert to DataFrame
        import pandas as pd
        
        data = []
        for direction, area in aspect_stats.items():
            data.append({
                'Aspect Direction': direction,
                'Area (hectares)': round(area, 2)
            })
        
        df = pd.DataFrame(data)
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"aspect_areas_{request.analysisId}.xlsx")
        
        # Export to Excel
        df.to_excel(output_path, index=False, sheet_name='Aspect Areas')
        
        logger.info(f"Aspect areas exported: {output_path}")
        
        return {
            "status": "success",
            "message": "Aspect areas exported to Excel",
            "filePath": output_path,
            "analysisId": request.analysisId
        }
    except Exception as e:
        logger.error(f"Error exporting aspect areas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# PROFESSIONAL MAP LAYOUT ENDPOINTS (A4, Clean, No Base Map)
# ============================================================================

class ProfessionalMapRequest(BaseModel):
    analysisId: str
    cfName: str
    compartmentGeometryPath: str = None
    slopeRasterPath: str = None
    aspectRasterPath: str = None

@app.post("/api/maps/professional/compartment")
async def generate_professional_compartment_map(request: ProfessionalMapRequest):
    """
    Generate professional A4 compartment map
    - Clean layout, no base map
    - CF name at top center
    - Legend at lower right
    - Area table at lower left
    - North arrow and scale bar
    - UTM coordinate labels
    """
    try:
        logger.info(f"Generating professional compartment map for {request.cfName}")
        
        # Find compartment file if not provided
        if not request.compartmentGeometryPath:
            compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        else:
            compartment_path = Path(request.compartmentGeometryPath)
        
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"compartment_map_professional_{request.analysisId}.pdf")
        
        # Generate map
        result_path = ProfessionalMapLayout.generate_compartment_map(
            compartment_geojson_path=str(compartment_path),
            cf_name=request.cfName,
            output_path=output_path
        )
        
        logger.info(f"Professional compartment map generated: {result_path}")
        
        return {
            "status": "success",
            "message": "Professional compartment map generated",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating professional compartment map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maps/professional/slope")
async def generate_professional_slope_map(request: ProfessionalMapRequest):
    """
    Generate professional A4 slope map
    - A4 format only
    - NO base map, NO satellite imagery
    - Clean dataframe-style layout
    - CF name at top center
    - Legend at lower right (0-20°, 20-30°, >30°)
    - Area summary table at lower left
    - North arrow and scale bar
    - UTM coordinate labels
    """
    try:
        logger.info(f"Generating professional slope map for {request.cfName}")
        
        # Find files
        if not request.slopeRasterPath:
            slope_path = EXPORTS_DIR / request.analysisId / f"slope_{request.analysisId}.tif"
        else:
            slope_path = Path(request.slopeRasterPath)
        
        if not request.compartmentGeometryPath:
            compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        else:
            compartment_path = Path(request.compartmentGeometryPath)
        
        if not slope_path.exists():
            raise HTTPException(status_code=404, detail="Slope data not found")
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Calculate slope statistics
        slope_stats = ZonalStatisticsCalculator.calculate_slope_areas(
            slope_raster_path=str(slope_path),
            compartment_geojson_path=str(compartment_path)
        )
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"slope_map_professional_{request.analysisId}.pdf")
        
        # Generate map
        result_path = ProfessionalSlopeMapLayout.generate_slope_map(
            slope_raster_path=str(slope_path),
            compartment_geojson_path=str(compartment_path),
            cf_name=request.cfName,
            output_path=output_path,
            slope_stats=slope_stats
        )
        
        logger.info(f"Professional slope map generated: {result_path}")
        
        return {
            "status": "success",
            "message": "Professional slope map generated",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating professional slope map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/maps/professional/aspect")
async def generate_professional_aspect_map(request: ProfessionalMapRequest):
    """
    Generate professional A4 aspect map
    - A4 format only
    - NO base map, NO satellite imagery
    - Clean dataframe-style layout
    - CF name at top center
    - Legend at lower right (N, NE, E, SE, S, SW, W, NW)
    - Area summary table at lower left
    - North arrow and scale bar
    - UTM coordinate labels
    """
    try:
        logger.info(f"Generating professional aspect map for {request.cfName}")
        
        # Find files
        if not request.aspectRasterPath:
            aspect_path = EXPORTS_DIR / request.analysisId / f"aspect_{request.analysisId}.tif"
        else:
            aspect_path = Path(request.aspectRasterPath)
        
        if not request.compartmentGeometryPath:
            compartment_path = EXPORTS_DIR / request.analysisId / f"compartments_{request.analysisId}.geojson"
        else:
            compartment_path = Path(request.compartmentGeometryPath)
        
        if not aspect_path.exists():
            raise HTTPException(status_code=404, detail="Aspect data not found")
        if not compartment_path.exists():
            raise HTTPException(status_code=404, detail="Compartment data not found")
        
        # Calculate aspect statistics
        aspect_stats = ZonalStatisticsCalculator.calculate_aspect_areas(
            aspect_raster_path=str(aspect_path),
            compartment_geojson_path=str(compartment_path)
        )
        
        # Output path
        output_dir = EXPORTS_DIR / request.analysisId
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"aspect_map_professional_{request.analysisId}.pdf")
        
        # Generate map
        result_path = ProfessionalAspectMapLayout.generate_aspect_map(
            aspect_raster_path=str(aspect_path),
            compartment_geojson_path=str(compartment_path),
            cf_name=request.cfName,
            output_path=output_path,
            aspect_stats=aspect_stats
        )
        
        logger.info(f"Professional aspect map generated: {result_path}")
        
        return {
            "status": "success",
            "message": "Professional aspect map generated",
            "filePath": result_path,
            "analysisId": request.analysisId
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating professional aspect map: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
