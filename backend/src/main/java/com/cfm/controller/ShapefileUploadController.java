package com.cfm.controller;

import com.cfm.dto.UploadResponse;
import com.cfm.dto.ValidationResult;
import com.cfm.service.ShapefileUploadService;
import com.cfm.service.GeometryValidationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.UUID;

/**
 * REST Controller for shapefile upload and validation.
 * Handles multipart file uploads for community forest boundary shapefiles.
 */
@RestController
@RequestMapping("/api/shapefile")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*", allowedHeaders = "*")
@Tag(name = "Shapefile Upload", description = "Endpoints for uploading and validating shapefiles")
public class ShapefileUploadController {

    private final ShapefileUploadService shapefileUploadService;
    private final GeometryValidationService geometryValidationService;

    /**
     * Upload shapefile components (.shp, .shx, .dbf, .prj) or compressed archives (ZIP, RAR).
     * Validates file completeness and stores files for processing.
     * Supports both individual files and compressed archives containing shapefile components.
     *
     * @param files Array of uploaded files (individual components or archives)
     * @return UploadResponse with shapefile metadata
     */
    @PostMapping("/upload")
    @Operation(summary = "Upload shapefile components or archives", description = "Upload .shp, .shx, .dbf, .prj files or ZIP/RAR archives containing them")
    public ResponseEntity<UploadResponse> uploadShapefile(@RequestParam("files") MultipartFile[] files) {
        try {
            log.info("Received shapefile upload with {} files", files.length);
            UploadResponse response = shapefileUploadService.uploadAndValidate(files);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            log.warn("Validation error during shapefile upload: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                UploadResponse.builder()
                    .status("error")
                    .message(e.getMessage())
                    .build()
            );
        } catch (Exception e) {
            log.error("Error uploading shapefile", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                UploadResponse.builder()
                    .status("error")
                    .message("Error uploading shapefile: " + e.getMessage())
                    .build()
            );
        }
    }

    /**
     * Validate shapefile geometry for self-intersections, projection, and area.
     * Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8
     *
     * @param shapefileId ID of the shapefile to validate
     * @return ValidationResult with warnings and status
     */
    @PostMapping("/{shapefileId}/validate")
    @Operation(summary = "Validate shapefile geometry", description = "Validate geometry for self-intersections, projection, and area")
    public ResponseEntity<ValidationResult> validateGeometry(@PathVariable UUID shapefileId) {
        try {
            log.info("Validating geometry for shapefile: {}", shapefileId);
            ValidationResult result = shapefileUploadService.validateShapefileGeometry(shapefileId);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            log.warn("Validation error: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                ValidationResult.builder()
                    .isValid(false)
                    .status("error")
                    .message(e.getMessage())
                    .build()
            );
        } catch (Exception e) {
            log.error("Error validating geometry", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                ValidationResult.builder()
                    .isValid(false)
                    .status("error")
                    .message("Error validating geometry: " + e.getMessage())
                    .build()
            );
        }
    }

    /**
     * Auto-repair self-intersecting geometries.
     * Requirements: 17.2, 17.6
     *
     * @param shapefileId ID of the shapefile to repair
     * @return ValidationResult after repair attempt
     */
    @PostMapping("/{shapefileId}/auto-repair")
    @Operation(summary = "Auto-repair self-intersecting geometry", description = "Attempt to repair self-intersecting geometries")
    public ResponseEntity<ValidationResult> autoRepairGeometry(@PathVariable UUID shapefileId) {
        try {
            log.info("Auto-repairing geometry for shapefile: {}", shapefileId);
            ValidationResult result = shapefileUploadService.autoRepairShapefileGeometry(shapefileId);
            return ResponseEntity.ok(result);
        } catch (IllegalArgumentException e) {
            log.warn("Auto-repair error: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                ValidationResult.builder()
                    .isValid(false)
                    .status("error")
                    .message(e.getMessage())
                    .build()
            );
        } catch (Exception e) {
            log.error("Error auto-repairing geometry", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                ValidationResult.builder()
                    .isValid(false)
                    .status("error")
                    .message("Error auto-repairing geometry: " + e.getMessage())
                    .build()
            );
        }
    }

    /**
     * Get shapefile by ID with geometry.
     * 
     * @param shapefileId ID of the shapefile
     * @return Shapefile data with geometry
     */
    @GetMapping("/{shapefileId}")
    @Operation(summary = "Get shapefile by ID", description = "Retrieve shapefile data including geometry")
    public ResponseEntity<?> getShapefileById(@PathVariable UUID shapefileId) {
        try {
            log.info("Fetching shapefile: {}", shapefileId);
            var shapefileData = shapefileUploadService.getShapefileDataById(shapefileId);
            return ResponseEntity.ok(shapefileData);
        } catch (IllegalArgumentException e) {
            log.warn("Shapefile fetch error: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                java.util.Map.of(
                    "status", "error",
                    "message", e.getMessage()
                )
            );
        } catch (Exception e) {
            log.error("Error fetching shapefile", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                java.util.Map.of(
                    "status", "error",
                    "message", "Error fetching shapefile: " + e.getMessage()
                )
            );
        }
    }

    /**
     * Get boundary geometry for a shapefile.
     * Requirements: 13.1, 13.2, 13.4
     *
     * @param shapefileId ID of the shapefile
     * @return Boundary geometry as GeoJSON with area and bounding box
     */
    @GetMapping("/{shapefileId}/boundary")
    @Operation(summary = "Get boundary geometry", description = "Retrieve boundary geometry as GeoJSON with area and bounding box")
    public ResponseEntity<?> getBoundaryGeometry(@PathVariable UUID shapefileId) {
        try {
            log.info("Fetching boundary geometry for shapefile: {}", shapefileId);
            var boundaryData = shapefileUploadService.getBoundaryGeometry(shapefileId);
            return ResponseEntity.ok(boundaryData);
        } catch (IllegalArgumentException e) {
            log.warn("Boundary fetch error: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                java.util.Map.of(
                    "status", "error",
                    "message", e.getMessage()
                )
            );
        } catch (Exception e) {
            log.error("Error fetching boundary geometry", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                java.util.Map.of(
                    "status", "error",
                    "message", "Error fetching boundary geometry: " + e.getMessage()
                )
            );
        }
    }
}
