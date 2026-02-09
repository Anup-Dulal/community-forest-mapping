package com.cfm.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Global exception handler for REST API endpoints.
 * Provides consistent error responses with descriptive messages and logging.
 */
@RestControllerAdvice
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * Handle shapefile validation errors.
     */
    @ExceptionHandler(ShapefileValidationException.class)
    public ResponseEntity<Map<String, Object>> handleShapefileValidationException(
            ShapefileValidationException ex, WebRequest request) {
        logger.warn("Shapefile validation error: {}", ex.getMessage());
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "SHAPEFILE_VALIDATION_ERROR",
            ex.getMessage(),
            HttpStatus.BAD_REQUEST
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }

    /**
     * Handle DEM download errors.
     */
    @ExceptionHandler(DEMDownloadException.class)
    public ResponseEntity<Map<String, Object>> handleDEMDownloadException(
            DEMDownloadException ex, WebRequest request) {
        logger.error("DEM download error: {}", ex.getMessage(), ex);
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "DEM_DOWNLOAD_ERROR",
            ex.getMessage() + ". Please try again or contact support.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /**
     * Handle terrain analysis errors.
     */
    @ExceptionHandler(TerrainAnalysisException.class)
    public ResponseEntity<Map<String, Object>> handleTerrainAnalysisException(
            TerrainAnalysisException ex, WebRequest request) {
        logger.error("Terrain analysis error: {}", ex.getMessage(), ex);
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "TERRAIN_ANALYSIS_ERROR",
            ex.getMessage() + ". Please verify your input data and try again.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /**
     * Handle compartment generation errors.
     */
    @ExceptionHandler(CompartmentGenerationException.class)
    public ResponseEntity<Map<String, Object>> handleCompartmentGenerationException(
            CompartmentGenerationException ex, WebRequest request) {
        logger.error("Compartment generation error: {}", ex.getMessage(), ex);
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "COMPARTMENT_GENERATION_ERROR",
            ex.getMessage() + ". Please try again.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /**
     * Handle sample plot generation errors.
     */
    @ExceptionHandler(SamplePlotGenerationException.class)
    public ResponseEntity<Map<String, Object>> handleSamplePlotGenerationException(
            SamplePlotGenerationException ex, WebRequest request) {
        logger.error("Sample plot generation error: {}", ex.getMessage(), ex);
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "SAMPLE_PLOT_GENERATION_ERROR",
            ex.getMessage() + ". Please try again.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /**
     * Handle export errors.
     */
    @ExceptionHandler(ExportException.class)
    public ResponseEntity<Map<String, Object>> handleExportException(
            ExportException ex, WebRequest request) {
        logger.error("Export error: {}", ex.getMessage(), ex);
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "EXPORT_ERROR",
            ex.getMessage() + ". Please check available disk space and try again.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /**
     * Handle resource not found errors.
     */
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleResourceNotFoundException(
            ResourceNotFoundException ex, WebRequest request) {
        logger.warn("Resource not found: {}", ex.getMessage());
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "RESOURCE_NOT_FOUND",
            ex.getMessage(),
            HttpStatus.NOT_FOUND
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.NOT_FOUND);
    }

    /**
     * Handle generic exceptions.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGenericException(
            Exception ex, WebRequest request) {
        logger.error("Unexpected error: {}", ex.getMessage(), ex);
        
        Map<String, Object> errorResponse = buildErrorResponse(
            "INTERNAL_SERVER_ERROR",
            "An unexpected error occurred. Please try again or contact support.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
        
        return new ResponseEntity<>(errorResponse, HttpStatus.INTERNAL_SERVER_ERROR);
    }

    /**
     * Build a standardized error response.
     */
    private Map<String, Object> buildErrorResponse(String errorCode, String message, HttpStatus status) {
        Map<String, Object> response = new HashMap<>();
        response.put("error", true);
        response.put("errorCode", errorCode);
        response.put("message", message);
        response.put("status", status.value());
        response.put("timestamp", LocalDateTime.now());
        return response;
    }
}
