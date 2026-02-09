package com.cfm.controller;

import com.cfm.service.MapExportService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.util.Map;
import java.util.UUID;

/**
 * REST Controller for map export operations.
 * Provides endpoints for rendering and exporting maps in PDF and PNG formats.
 */
@Slf4j
@RestController
@RequestMapping("/maps")
@CrossOrigin(origins = "*", maxAge = 3600)
public class MapExportController {

    @Autowired
    private MapExportService mapExportService;

    /**
     * Render and export slope map.
     *
     * @param analysisResultId ID of the analysis result
     * @param format "png" or "pdf" (default "png")
     * @return Map file as attachment
     */
    @PostMapping("/export/slope")
    public ResponseEntity<?> exportSlopeMap(
            @RequestParam UUID analysisResultId,
            @RequestParam(required = false, defaultValue = "png") String format
    ) {
        try {
            log.info("Exporting slope map for analysis: {}", analysisResultId);

            Map<String, Object> result = mapExportService.renderSlopeMap(analysisResultId, format);

            String mapPath = (String) result.get("mapPath");
            File file = new File(mapPath);

            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }

            Resource resource = new FileSystemResource(file);
            MediaType mediaType = "pdf".equalsIgnoreCase(format) ?
                    MediaType.APPLICATION_PDF : MediaType.IMAGE_PNG;

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + file.getName() + "\"")
                    .contentType(mediaType)
                    .body(resource);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error exporting slope map: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to export slope map: " + e.getMessage())
            );
        }
    }

    /**
     * Render and export aspect map.
     *
     * @param analysisResultId ID of the analysis result
     * @param format "png" or "pdf" (default "png")
     * @return Map file as attachment
     */
    @PostMapping("/export/aspect")
    public ResponseEntity<?> exportAspectMap(
            @RequestParam UUID analysisResultId,
            @RequestParam(required = false, defaultValue = "png") String format
    ) {
        try {
            log.info("Exporting aspect map for analysis: {}", analysisResultId);

            Map<String, Object> result = mapExportService.renderAspectMap(analysisResultId, format);

            String mapPath = (String) result.get("mapPath");
            File file = new File(mapPath);

            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }

            Resource resource = new FileSystemResource(file);
            MediaType mediaType = "pdf".equalsIgnoreCase(format) ?
                    MediaType.APPLICATION_PDF : MediaType.IMAGE_PNG;

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + file.getName() + "\"")
                    .contentType(mediaType)
                    .body(resource);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error exporting aspect map: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to export aspect map: " + e.getMessage())
            );
        }
    }

    /**
     * Render and export compartment map.
     *
     * @param analysisResultId ID of the analysis result
     * @param format "png" or "pdf" (default "png")
     * @return Map file as attachment
     */
    @PostMapping("/export/compartment")
    public ResponseEntity<?> exportCompartmentMap(
            @RequestParam UUID analysisResultId,
            @RequestParam(required = false, defaultValue = "png") String format
    ) {
        try {
            log.info("Exporting compartment map for analysis: {}", analysisResultId);

            Map<String, Object> result = mapExportService.renderCompartmentMap(analysisResultId, format);

            String mapPath = (String) result.get("mapPath");
            File file = new File(mapPath);

            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }

            Resource resource = new FileSystemResource(file);
            MediaType mediaType = "pdf".equalsIgnoreCase(format) ?
                    MediaType.APPLICATION_PDF : MediaType.IMAGE_PNG;

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + file.getName() + "\"")
                    .contentType(mediaType)
                    .body(resource);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error exporting compartment map: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to export compartment map: " + e.getMessage())
            );
        }
    }

    /**
     * Render and export sample plot map.
     *
     * @param analysisResultId ID of the analysis result
     * @param format "png" or "pdf" (default "png")
     * @return Map file as attachment
     */
    @PostMapping("/export/sample-plots")
    public ResponseEntity<?> exportSamplePlotMap(
            @RequestParam UUID analysisResultId,
            @RequestParam(required = false, defaultValue = "png") String format
    ) {
        try {
            log.info("Exporting sample plot map for analysis: {}", analysisResultId);

            Map<String, Object> result = mapExportService.renderSamplePlotMap(analysisResultId, format);

            String mapPath = (String) result.get("mapPath");
            File file = new File(mapPath);

            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }

            Resource resource = new FileSystemResource(file);
            MediaType mediaType = "pdf".equalsIgnoreCase(format) ?
                    MediaType.APPLICATION_PDF : MediaType.IMAGE_PNG;

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + file.getName() + "\"")
                    .contentType(mediaType)
                    .body(resource);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error exporting sample plot map: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to export sample plot map: " + e.getMessage())
            );
        }
    }
}
