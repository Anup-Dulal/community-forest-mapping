"""
Error handling utilities for GIS microservice.
Provides consistent error responses and logging for GIS operations.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standard error codes for GIS operations."""
    SHAPEFILE_PARSING_ERROR = "SHAPEFILE_PARSING_ERROR"
    BOUNDING_BOX_ERROR = "BOUNDING_BOX_ERROR"
    DEM_DOWNLOAD_ERROR = "DEM_DOWNLOAD_ERROR"
    DEM_CLIPPING_ERROR = "DEM_CLIPPING_ERROR"
    SLOPE_CALCULATION_ERROR = "SLOPE_CALCULATION_ERROR"
    ASPECT_CALCULATION_ERROR = "ASPECT_CALCULATION_ERROR"
    COMPARTMENT_GENERATION_ERROR = "COMPARTMENT_GENERATION_ERROR"
    SAMPLE_PLOT_GENERATION_ERROR = "SAMPLE_PLOT_GENERATION_ERROR"
    COORDINATE_CONVERSION_ERROR = "COORDINATE_CONVERSION_ERROR"
    MAP_RENDERING_ERROR = "MAP_RENDERING_ERROR"
    INVALID_INPUT_ERROR = "INVALID_INPUT_ERROR"
    FILE_SYSTEM_ERROR = "FILE_SYSTEM_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class GISException(Exception):
    """Base exception for GIS operations."""
    
    def __init__(self, error_code: ErrorCode, message: str, details: str = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": True,
            "errorCode": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "timestamp": datetime.now().isoformat()
        }


class ShapefileParsingException(GISException):
    """Exception thrown when shapefile parsing fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.SHAPEFILE_PARSING_ERROR, message, details)
        logger.error(f"Shapefile parsing error: {message}", exc_info=True)


class BoundingBoxException(GISException):
    """Exception thrown when bounding box extraction fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.BOUNDING_BOX_ERROR, message, details)
        logger.error(f"Bounding box error: {message}", exc_info=True)


class DEMDownloadException(GISException):
    """Exception thrown when DEM download fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.DEM_DOWNLOAD_ERROR, message, details)
        logger.error(f"DEM download error: {message}", exc_info=True)


class DEMClippingException(GISException):
    """Exception thrown when DEM clipping fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.DEM_CLIPPING_ERROR, message, details)
        logger.error(f"DEM clipping error: {message}", exc_info=True)


class SlopeCalculationException(GISException):
    """Exception thrown when slope calculation fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.SLOPE_CALCULATION_ERROR, message, details)
        logger.error(f"Slope calculation error: {message}", exc_info=True)


class AspectCalculationException(GISException):
    """Exception thrown when aspect calculation fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.ASPECT_CALCULATION_ERROR, message, details)
        logger.error(f"Aspect calculation error: {message}", exc_info=True)


class CompartmentGenerationException(GISException):
    """Exception thrown when compartment generation fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.COMPARTMENT_GENERATION_ERROR, message, details)
        logger.error(f"Compartment generation error: {message}", exc_info=True)


class SamplePlotGenerationException(GISException):
    """Exception thrown when sample plot generation fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.SAMPLE_PLOT_GENERATION_ERROR, message, details)
        logger.error(f"Sample plot generation error: {message}", exc_info=True)


class CoordinateConversionException(GISException):
    """Exception thrown when coordinate conversion fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.COORDINATE_CONVERSION_ERROR, message, details)
        logger.error(f"Coordinate conversion error: {message}", exc_info=True)


class MapRenderingException(GISException):
    """Exception thrown when map rendering fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.MAP_RENDERING_ERROR, message, details)
        logger.error(f"Map rendering error: {message}", exc_info=True)


class InvalidInputException(GISException):
    """Exception thrown when input validation fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.INVALID_INPUT_ERROR, message, details)
        logger.warning(f"Invalid input: {message}")


class FileSystemException(GISException):
    """Exception thrown when file system operations fail."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(ErrorCode.FILE_SYSTEM_ERROR, message, details)
        logger.error(f"File system error: {message}", exc_info=True)


def handle_gis_exception(exception: Exception, error_code: ErrorCode, message: str) -> Dict[str, Any]:
    """
    Handle a GIS exception and return a standardized error response.
    
    Args:
        exception: The exception that occurred
        error_code: The error code to use
        message: The error message
    
    Returns:
        Dictionary with error information
    """
    details = str(exception) if exception else None
    gis_exception = GISException(error_code, message, details)
    return gis_exception.to_dict()


def log_operation_start(operation_name: str, **kwargs):
    """Log the start of a GIS operation."""
    logger.info(f"Starting {operation_name} with parameters: {kwargs}")


def log_operation_success(operation_name: str, **kwargs):
    """Log successful completion of a GIS operation."""
    logger.info(f"Successfully completed {operation_name}. Results: {kwargs}")


def log_operation_error(operation_name: str, error: Exception, **kwargs):
    """Log an error during a GIS operation."""
    logger.error(f"Error during {operation_name}: {str(error)}", exc_info=True)
