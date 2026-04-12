package com.cfm.controller;

import com.cfm.model.AnalysisResult;
import com.cfm.repository.AnalysisResultRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Controller for exporting maps and coordinates in various formats.
 * Provides endpoints for PDF, PNG, Excel, CSV, and GPX exports.
 */
@Slf4j
@RestController
@RequestMapping("/api/export")
@CrossOrigin(origins = "*", maxAge = 3600)
public class ExportController {

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Value("${gis.service.url:http://gis-service:8000}")
    private String gisServiceUrl;

    /**
     * Export map as PDF with professional layout.
     */
    @PostMapping("/map/pdf")
    public ResponseEntity<?> exportMapPDF(
            @RequestParam String analysisId,
            @RequestParam(required = false) String cfName,
            @RequestParam(required = false) String mapTitle,
            @RequestParam(required = false, defaultValue = "english") String language
    ) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting PDF map for analysis: {} in language: {}", id, language);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            if (compartmentGeometryPath == null || compartmentGeometryPath.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No compartment data available"));
            }

            // Call GIS service to generate PDF
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("compartmentGeometryPath", compartmentGeometryPath);
            request.put("cfName", cfName != null ? cfName : "Community Forest");
            request.put("mapTitle", mapTitle != null ? mapTitle : "Compartment Map");
            request.put("language", language);
            request.put("format", "pdf");

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/map/layout",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.APPLICATION_PDF)
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"compartment_map_" + analysisId + ".pdf\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate PDF"));

        } catch (Exception e) {
            log.error("Error exporting PDF map", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export map as PNG image.
     */
    @PostMapping("/map/png")
    public ResponseEntity<?> exportMapPNG(
            @RequestParam String analysisId,
            @RequestParam(required = false) String cfName,
            @RequestParam(required = false) String mapTitle,
            @RequestParam(required = false, defaultValue = "english") String language
    ) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting PNG map for analysis: {} in language: {}", id, language);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            if (compartmentGeometryPath == null || compartmentGeometryPath.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No compartment data available"));
            }

            // Call GIS service to generate PNG
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("compartmentGeometryPath", compartmentGeometryPath);
            request.put("cfName", cfName != null ? cfName : "Community Forest");
            request.put("mapTitle", mapTitle != null ? mapTitle : "Compartment Map");
            request.put("language", language);
            request.put("format", "png");

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/map/layout",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.IMAGE_PNG)
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"compartment_map_" + analysisId + ".png\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate PNG"));

        } catch (Exception e) {
            log.error("Error exporting PNG map", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export polygon vertices as Excel with UTM coordinates.
     */
    @PostMapping("/coordinates/excel")
    public ResponseEntity<?> exportCoordinatesExcel(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting Excel coordinates for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            if (compartmentGeometryPath == null || compartmentGeometryPath.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No compartment data available"));
            }

            // Call GIS service to generate Excel
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("compartmentGeometryPath", compartmentGeometryPath);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/coordinates/excel",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"compartment_coordinates_" + analysisId + ".xlsx\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate Excel"));

        } catch (Exception e) {
            log.error("Error exporting Excel coordinates", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export polygon vertices as CSV with UTM coordinates.
     */
    @PostMapping("/coordinates/csv")
    public ResponseEntity<?> exportCoordinatesCSV(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting CSV coordinates for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            if (compartmentGeometryPath == null || compartmentGeometryPath.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No compartment data available"));
            }

            // Call GIS service to generate CSV
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("compartmentGeometryPath", compartmentGeometryPath);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/coordinates/csv",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.parseMediaType("text/csv"))
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"compartment_coordinates_" + analysisId + ".csv\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate CSV"));

        } catch (Exception e) {
            log.error("Error exporting CSV coordinates", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export sample plots as GPX for GPS devices.
     */
    @PostMapping("/gpx")
    public ResponseEntity<?> exportGPX(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting GPX for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String samplePlotGeometryPath = analysis.getSamplePlotGeometryPath();
            if (samplePlotGeometryPath == null || samplePlotGeometryPath.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No sample plot data available"));
            }

            // Call GIS service to generate GPX
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("samplePlotGeometryPath", samplePlotGeometryPath);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/gpx",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.parseMediaType("application/gpx+xml"))
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"sample_plots_" + analysisId + ".gpx\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate GPX"));

        } catch (Exception e) {
            log.error("Error exporting GPX", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Get slope and aspect statistics for analysis.
     */
    @GetMapping("/statistics/terrain")
    public ResponseEntity<?> getTerrainStatistics(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Getting terrain statistics for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            String slopeRasterPath = analysis.getSlopeRasterPath();
            String aspectRasterPath = analysis.getAspectRasterPath();

            if (compartmentGeometryPath == null || slopeRasterPath == null || aspectRasterPath == null) {
                return ResponseEntity.badRequest().body(Map.of("error", "Terrain data not available"));
            }

            // Call GIS service to calculate statistics
            String url = gisServiceUrl + "/api/statistics/terrain?analysisId=" + analysisId +
                    "&compartmentGeometryPath=" + compartmentGeometryPath +
                    "&slopeRasterPath=" + slopeRasterPath +
                    "&aspectRasterPath=" + aspectRasterPath;

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("Error getting terrain statistics", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export compartment area summary as Excel.
     */
    @PostMapping("/areas/compartments")
    public ResponseEntity<?> exportCompartmentAreas(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting compartment areas for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            if (compartmentGeometryPath == null || compartmentGeometryPath.isEmpty()) {
                return ResponseEntity.badRequest().body(Map.of("error", "No compartment data available"));
            }

            // Call GIS service to generate Excel with area summary
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("compartmentGeometryPath", compartmentGeometryPath);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/areas/compartments",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"compartment_areas_" + analysisId + ".xlsx\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate compartment areas Excel"));

        } catch (Exception e) {
            log.error("Error exporting compartment areas", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export slope area summary as Excel.
     */
    @PostMapping("/areas/slope")
    public ResponseEntity<?> exportSlopeAreas(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting slope areas for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String slopeRasterPath = analysis.getSlopeRasterPath();
            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            
            if (slopeRasterPath == null || compartmentGeometryPath == null) {
                return ResponseEntity.badRequest().body(Map.of("error", "Slope data not available"));
            }

            // Call GIS service to generate Excel with slope area summary
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("slopeRasterPath", slopeRasterPath);
            request.put("compartmentGeometryPath", compartmentGeometryPath);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/areas/slope",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"slope_areas_" + analysisId + ".xlsx\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate slope areas Excel"));

        } catch (Exception e) {
            log.error("Error exporting slope areas", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Export aspect area summary as Excel.
     */
    @PostMapping("/areas/aspect")
    public ResponseEntity<?> exportAspectAreas(@RequestParam String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Exporting aspect areas for analysis: {}", id);

            AnalysisResult analysis = analysisResultRepository.findById(id)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis not found: " + id));

            String aspectRasterPath = analysis.getAspectRasterPath();
            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            
            if (aspectRasterPath == null || compartmentGeometryPath == null) {
                return ResponseEntity.badRequest().body(Map.of("error", "Aspect data not available"));
            }

            // Call GIS service to generate Excel with aspect area summary
            Map<String, Object> request = new HashMap<>();
            request.put("analysisId", analysisId);
            request.put("aspectRasterPath", aspectRasterPath);
            request.put("compartmentGeometryPath", compartmentGeometryPath);

            @SuppressWarnings("unchecked")
            Map<String, Object> response = restTemplate.postForObject(
                    gisServiceUrl + "/api/export/areas/aspect",
                    request,
                    Map.class
            );

            if (response != null && "success".equals(response.get("status"))) {
                String filePath = (String) response.get("filePath");
                File file = new File(filePath);
                
                if (file.exists()) {
                    Resource resource = new FileSystemResource(file);
                    return ResponseEntity.ok()
                            .contentType(MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
                            .header(HttpHeaders.CONTENT_DISPOSITION, 
                                    "attachment; filename=\"aspect_areas_" + analysisId + ".xlsx\"")
                            .body(resource);
                }
            }

            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Failed to generate aspect areas Excel"));

        } catch (Exception e) {
            log.error("Error exporting aspect areas", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", e.getMessage()));
        }
    }
}

