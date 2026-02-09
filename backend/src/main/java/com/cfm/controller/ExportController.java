package com.cfm.controller;

import com.cfm.service.CoordinateExportService;
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
 * REST Controller for coordinate export operations.
 * Provides endpoints for exporting sample plot coordinates to CSV and Excel formats.
 */
@Slf4j
@RestController
@RequestMapping("/export")
@CrossOrigin(origins = "*", maxAge = 3600)
public class ExportController {

    @Autowired
    private CoordinateExportService coordinateExportService;

    /**
     * Export sample plot coordinates to CSV format.
     *
     * @param analysisResultId ID of the analysis result
     * @return CSV file as attachment
     */
    @GetMapping("/coordinates/csv")
    public ResponseEntity<?> exportCoordinatesAsCSV(
            @RequestParam UUID analysisResultId
    ) {
        try {
            log.info("Exporting coordinates to CSV for analysis: {}", analysisResultId);

            String filepath = coordinateExportService.exportToCSV(analysisResultId);

            File file = new File(filepath);
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }

            Resource resource = new FileSystemResource(file);

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + file.getName() + "\"")
                    .contentType(MediaType.parseMediaType("text/csv"))
                    .body(resource);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error exporting to CSV: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to export to CSV: " + e.getMessage())
            );
        }
    }

    /**
     * Export sample plot coordinates to Excel format.
     *
     * @param analysisResultId ID of the analysis result
     * @return Excel file as attachment
     */
    @GetMapping("/coordinates/excel")
    public ResponseEntity<?> exportCoordinatesAsExcel(
            @RequestParam UUID analysisResultId
    ) {
        try {
            log.info("Exporting coordinates to Excel for analysis: {}", analysisResultId);

            String filepath = coordinateExportService.exportToExcel(analysisResultId);

            File file = new File(filepath);
            if (!file.exists()) {
                return ResponseEntity.notFound().build();
            }

            Resource resource = new FileSystemResource(file);

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + file.getName() + "\"")
                    .contentType(MediaType.parseMediaType(
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                    .body(resource);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error exporting to Excel: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to export to Excel: " + e.getMessage())
            );
        }
    }

    /**
     * Get export statistics for sample plots.
     *
     * @param analysisResultId ID of the analysis result
     * @return Export statistics
     */
    @GetMapping("/coordinates/statistics")
    public ResponseEntity<?> getExportStatistics(
            @RequestParam UUID analysisResultId
    ) {
        try {
            log.info("Getting export statistics for analysis: {}", analysisResultId);

            Map<String, Object> stats = coordinateExportService.getExportStatistics(analysisResultId);

            return ResponseEntity.ok(stats);

        } catch (Exception e) {
            log.error("Error getting export statistics: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to get statistics: " + e.getMessage())
            );
        }
    }
}
