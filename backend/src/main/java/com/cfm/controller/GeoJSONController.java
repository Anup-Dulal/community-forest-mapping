package com.cfm.controller;

import com.cfm.model.AnalysisResult;
import com.cfm.repository.AnalysisResultRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.File;
import java.nio.file.Files;
import java.util.UUID;
import java.util.Map;

/**
 * GeoJSON Controller - Serves GeoJSON data for map layers
 */
@RestController
@RequestMapping("/api/geojson")
@CrossOrigin(origins = "*", allowedHeaders = "*")
public class GeoJSONController {

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Get compartment GeoJSON
     */
    @GetMapping("/compartment")
    public ResponseEntity<?> getCompartmentGeoJSON(@RequestParam UUID analysisId) {
        try {
            // Get analysis result to find compartment geometry file path
            AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + analysisId));
            
            String compartmentGeometryPath = analysis.getCompartmentGeometryPath();
            
            if (compartmentGeometryPath == null || compartmentGeometryPath.trim().isEmpty()) {
                // Return empty FeatureCollection if no geometry path
                ObjectNode geoJson = objectMapper.createObjectNode();
                geoJson.put("type", "FeatureCollection");
                geoJson.putArray("features");
                return ResponseEntity.ok(geoJson);
            }
            
            // Read GeoJSON from file
            File geojsonFile = new File(compartmentGeometryPath);
            if (!geojsonFile.exists()) {
                throw new RuntimeException("Compartment geometry file not found: " + compartmentGeometryPath);
            }
            
            String geojsonContent = new String(Files.readAllBytes(geojsonFile.toPath()));
            Map<String, Object> geojsonData = objectMapper.readValue(geojsonContent, Map.class);
            
            return ResponseEntity.ok(geojsonData);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }

    /**
     * Get sample plot GeoJSON
     */
    @GetMapping("/samplePlot")
    public ResponseEntity<?> getSamplePlotGeoJSON(@RequestParam UUID analysisId) {
        try {
            // Get analysis result to find sample plot geometry file path
            AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + analysisId));
            
            String samplePlotGeometryPath = analysis.getSamplePlotGeometryPath();
            
            if (samplePlotGeometryPath == null || samplePlotGeometryPath.trim().isEmpty()) {
                // Return empty FeatureCollection if no geometry path
                ObjectNode geoJson = objectMapper.createObjectNode();
                geoJson.put("type", "FeatureCollection");
                geoJson.putArray("features");
                return ResponseEntity.ok(geoJson);
            }
            
            // Read GeoJSON from file
            File geojsonFile = new File(samplePlotGeometryPath);
            if (!geojsonFile.exists()) {
                throw new RuntimeException("Sample plot geometry file not found: " + samplePlotGeometryPath);
            }
            
            String geojsonContent = new String(Files.readAllBytes(geojsonFile.toPath()));
            Map<String, Object> geojsonData = objectMapper.readValue(geojsonContent, Map.class);
            
            return ResponseEntity.ok(geojsonData);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }

    /**
     * Get DEM GeoJSON - proxies to GIS service
     */
    @GetMapping("/dem")
    public ResponseEntity<?> getDEMGeoJSON(@RequestParam UUID analysisId) {
        try {
            // Proxy request to GIS service
            String gisServiceUrl = "http://gis-service:8000/api/geojson/dem?analysisId=" + analysisId;
            
            org.springframework.web.client.RestTemplate restTemplate = new org.springframework.web.client.RestTemplate();
            
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(gisServiceUrl, Map.class);
                return ResponseEntity.ok(response);
            } catch (org.springframework.web.client.ResourceAccessException e) {
                // GIS service not available, return empty FeatureCollection
                ObjectNode geoJson = objectMapper.createObjectNode();
                geoJson.put("type", "FeatureCollection");
                geoJson.putArray("features");
                return ResponseEntity.ok(geoJson);
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }

    /**
     * Get slope GeoJSON - proxies to GIS service
     */
    @GetMapping("/slope")
    public ResponseEntity<?> getSlopeGeoJSON(@RequestParam UUID analysisId) {
        try {
            // Proxy request to GIS service
            String gisServiceUrl = "http://gis-service:8000/api/geojson/slope?analysisId=" + analysisId;
            
            org.springframework.web.client.RestTemplate restTemplate = new org.springframework.web.client.RestTemplate();
            
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(gisServiceUrl, Map.class);
                return ResponseEntity.ok(response);
            } catch (org.springframework.web.client.ResourceAccessException e) {
                // GIS service not available, return empty FeatureCollection
                ObjectNode geoJson = objectMapper.createObjectNode();
                geoJson.put("type", "FeatureCollection");
                geoJson.putArray("features");
                return ResponseEntity.ok(geoJson);
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }

    /**
     * Get aspect GeoJSON - proxies to GIS service
     */
    @GetMapping("/aspect")
    public ResponseEntity<?> getAspectGeoJSON(@RequestParam UUID analysisId) {
        try {
            // Proxy request to GIS service
            String gisServiceUrl = "http://gis-service:8000/api/geojson/aspect?analysisId=" + analysisId;
            
            org.springframework.web.client.RestTemplate restTemplate = new org.springframework.web.client.RestTemplate();
            
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.getForObject(gisServiceUrl, Map.class);
                return ResponseEntity.ok(response);
            } catch (org.springframework.web.client.ResourceAccessException e) {
                // GIS service not available, return empty FeatureCollection
                ObjectNode geoJson = objectMapper.createObjectNode();
                geoJson.put("type", "FeatureCollection");
                geoJson.putArray("features");
                return ResponseEntity.ok(geoJson);
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }
    }
}
