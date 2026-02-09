package com.cfm.controller;

import com.cfm.dto.UploadResponse;
import com.cfm.service.ShapefileUploadService;
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
@RequestMapping("/shapefile")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Shapefile Upload", description = "Endpoints for uploading and validating shapefiles")
public class ShapefileUploadController {

    private final ShapefileUploadService shapefileUploadService;

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
     * Get shapefile details by ID.
     *
     * @param id Shapefile UUID
     * @return Shapefile details
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get shapefile details", description = "Retrieve shapefile metadata and geometry")
    public ResponseEntity<?> getShapefile(@PathVariable UUID id) {
        try {
            var shapefile = shapefileUploadService.getShapefileById(id);
            return ResponseEntity.ok(shapefile);
        } catch (Exception e) {
            log.error("Error retrieving shapefile: {}", id, e);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(
                UploadResponse.builder()
                    .status("error")
                    .message("Shapefile not found")
                    .build()
            );
        }
    }
}
