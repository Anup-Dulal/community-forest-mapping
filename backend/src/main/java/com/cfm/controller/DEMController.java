package com.cfm.controller;

import com.cfm.dto.DEMStatusResponse;
import com.cfm.service.DEMDownloadService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * REST Controller for DEM download and management.
 * Handles automatic DEM download and status tracking.
 */
@RestController
@RequestMapping("/dem")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "DEM Management", description = "Endpoints for DEM download and processing")
public class DEMController {

    private final DEMDownloadService demDownloadService;

    /**
     * Trigger DEM download for a shapefile.
     * Automatically downloads and clips DEM to boundary.
     *
     * @param shapefileId Shapefile UUID
     * @param source DEM source (SRTM, OpenTopography, NASA)
     * @return DEMStatusResponse with download status
     */
    @PostMapping("/download")
    @Operation(summary = "Download DEM", description = "Trigger automatic DEM download for shapefile")
    public ResponseEntity<DEMStatusResponse> downloadDEM(
        @RequestParam UUID shapefileId,
        @RequestParam(defaultValue = "SRTM") String source
    ) {
        try {
            log.info("DEM download request for shapefile: {} from source: {}", shapefileId, source);
            DEMStatusResponse response = demDownloadService.downloadDEM(shapefileId, source);
            return ResponseEntity.accepted().body(response);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            log.error("Error downloading DEM", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get DEM download status.
     *
     * @param demId DEM UUID
     * @return DEMStatusResponse with current status
     */
    @GetMapping("/{demId}/status")
    @Operation(summary = "Get DEM status", description = "Retrieve current DEM download and processing status")
    public ResponseEntity<DEMStatusResponse> getDEMStatus(@PathVariable UUID demId) {
        try {
            log.info("Retrieving DEM status: {}", demId);
            DEMStatusResponse response = demDownloadService.getDEMStatus(demId);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            log.warn("DEM not found: {}", demId);
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("Error retrieving DEM status", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
