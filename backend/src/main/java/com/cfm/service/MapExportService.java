package com.cfm.service;

import com.cfm.model.AnalysisResult;
import com.cfm.repository.AnalysisResultRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import com.fasterxml.jackson.databind.JsonNode;

import java.util.*;

/**
 * Service for orchestrating map rendering and export.
 * Coordinates with GIS microservice for map generation in PDF and PNG formats.
 */
@Slf4j
@Service
public class MapExportService {

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Value("${gis.service.url:http://localhost:8001}")
    private String gisServiceUrl;

    /**
     * Render and export slope map.
     *
     * @param analysisResultId ID of the analysis result
     * @param outputFormat "png" or "pdf"
     * @return Map with export status and file path
     * @throws IllegalArgumentException if analysis result not found
     */
    public Map<String, Object> renderSlopeMap(UUID analysisResultId, String outputFormat) {
        try {
            // Validate analysis result exists
            AnalysisResult analysisResult = analysisResultRepository.findById(analysisResultId)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisResultId));

            // Validate required data
            if (analysisResult.getShapefile() == null || analysisResult.getShapefile().getGeometry() == null) {
                throw new IllegalArgumentException("Boundary geometry not found");
            }
            if (analysisResult.getSlopeRasterPath() == null || analysisResult.getSlopeRasterPath().isEmpty()) {
                throw new IllegalArgumentException("Slope raster not found");
            }

            log.info("Rendering slope map for analysis: {}", analysisResultId);

            // Call GIS microservice
            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("boundaryPath", analysisResult.getShapefile().getGeometry());
            gisRequest.put("slopeRasterPath", analysisResult.getSlopeRasterPath());
            gisRequest.put("compartmentPath", analysisResult.getCompartmentGeometryPath());
            gisRequest.put("title", "Slope Classification Map");
            gisRequest.put("outputFormat", outputFormat);
            gisRequest.put("analysisId", analysisResultId.toString());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/maps/render-slope",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to render slope map");
            }

            String mapPath = gisResponse.get("mapPath").asText();

            log.info("Slope map rendered successfully: {}", mapPath);

            return Map.of(
                    "status", "success",
                    "analysisId", analysisResultId,
                    "mapType", "slope",
                    "mapPath", mapPath,
                    "outputFormat", outputFormat
            );

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for slope map rendering: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error rendering slope map: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to render slope map: " + e.getMessage(), e);
        }
    }

    /**
     * Render and export aspect map.
     *
     * @param analysisResultId ID of the analysis result
     * @param outputFormat "png" or "pdf"
     * @return Map with export status and file path
     * @throws IllegalArgumentException if analysis result not found
     */
    public Map<String, Object> renderAspectMap(UUID analysisResultId, String outputFormat) {
        try {
            // Validate analysis result exists
            AnalysisResult analysisResult = analysisResultRepository.findById(analysisResultId)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisResultId));

            // Validate required data
            if (analysisResult.getShapefile() == null || analysisResult.getShapefile().getGeometry() == null) {
                throw new IllegalArgumentException("Boundary geometry not found");
            }
            if (analysisResult.getAspectRasterPath() == null || analysisResult.getAspectRasterPath().isEmpty()) {
                throw new IllegalArgumentException("Aspect raster not found");
            }

            log.info("Rendering aspect map for analysis: {}", analysisResultId);

            // Call GIS microservice
            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("boundaryPath", analysisResult.getShapefile().getGeometry());
            gisRequest.put("aspectRasterPath", analysisResult.getAspectRasterPath());
            gisRequest.put("compartmentPath", analysisResult.getCompartmentGeometryPath());
            gisRequest.put("title", "Aspect Direction Map");
            gisRequest.put("outputFormat", outputFormat);
            gisRequest.put("analysisId", analysisResultId.toString());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/maps/render-aspect",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to render aspect map");
            }

            String mapPath = gisResponse.get("mapPath").asText();

            log.info("Aspect map rendered successfully: {}", mapPath);

            return Map.of(
                    "status", "success",
                    "analysisId", analysisResultId,
                    "mapType", "aspect",
                    "mapPath", mapPath,
                    "outputFormat", outputFormat
            );

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for aspect map rendering: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error rendering aspect map: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to render aspect map: " + e.getMessage(), e);
        }
    }

    /**
     * Render and export compartment map.
     *
     * @param analysisResultId ID of the analysis result
     * @param outputFormat "png" or "pdf"
     * @return Map with export status and file path
     * @throws IllegalArgumentException if analysis result not found
     */
    public Map<String, Object> renderCompartmentMap(UUID analysisResultId, String outputFormat) {
        try {
            // Validate analysis result exists
            AnalysisResult analysisResult = analysisResultRepository.findById(analysisResultId)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisResultId));

            // Validate required data
            if (analysisResult.getShapefile() == null || analysisResult.getShapefile().getGeometry() == null) {
                throw new IllegalArgumentException("Boundary geometry not found");
            }
            if (analysisResult.getCompartmentGeometryPath() == null || analysisResult.getCompartmentGeometryPath().isEmpty()) {
                throw new IllegalArgumentException("Compartment geometry not found");
            }

            log.info("Rendering compartment map for analysis: {}", analysisResultId);

            // Call GIS microservice
            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("boundaryPath", analysisResult.getShapefile().getGeometry());
            gisRequest.put("compartmentPath", analysisResult.getCompartmentGeometryPath());
            gisRequest.put("title", "Compartment Division Map");
            gisRequest.put("outputFormat", outputFormat);
            gisRequest.put("analysisId", analysisResultId.toString());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/maps/render-compartment",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to render compartment map");
            }

            String mapPath = gisResponse.get("mapPath").asText();

            log.info("Compartment map rendered successfully: {}", mapPath);

            return Map.of(
                    "status", "success",
                    "analysisId", analysisResultId,
                    "mapType", "compartment",
                    "mapPath", mapPath,
                    "outputFormat", outputFormat
            );

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for compartment map rendering: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error rendering compartment map: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to render compartment map: " + e.getMessage(), e);
        }
    }

    /**
     * Render and export sample plot map.
     *
     * @param analysisResultId ID of the analysis result
     * @param outputFormat "png" or "pdf"
     * @return Map with export status and file path
     * @throws IllegalArgumentException if analysis result not found
     */
    public Map<String, Object> renderSamplePlotMap(UUID analysisResultId, String outputFormat) {
        try {
            // Validate analysis result exists
            AnalysisResult analysisResult = analysisResultRepository.findById(analysisResultId)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisResultId));

            // Validate required data
            if (analysisResult.getShapefile() == null || analysisResult.getShapefile().getGeometry() == null) {
                throw new IllegalArgumentException("Boundary geometry not found");
            }
            if (analysisResult.getCompartmentGeometryPath() == null || analysisResult.getCompartmentGeometryPath().isEmpty()) {
                throw new IllegalArgumentException("Compartment geometry not found");
            }
            if (analysisResult.getSamplePlotGeometryPath() == null || analysisResult.getSamplePlotGeometryPath().isEmpty()) {
                throw new IllegalArgumentException("Sample plot geometry not found");
            }

            log.info("Rendering sample plot map for analysis: {}", analysisResultId);

            // Call GIS microservice
            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("boundaryPath", analysisResult.getShapefile().getGeometry());
            gisRequest.put("compartmentPath", analysisResult.getCompartmentGeometryPath());
            gisRequest.put("samplePlotPath", analysisResult.getSamplePlotGeometryPath());
            gisRequest.put("title", "Sample Plot Distribution Map");
            gisRequest.put("outputFormat", outputFormat);
            gisRequest.put("analysisId", analysisResultId.toString());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/maps/render-sample-plots",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to render sample plot map");
            }

            String mapPath = gisResponse.get("mapPath").asText();

            log.info("Sample plot map rendered successfully: {}", mapPath);

            return Map.of(
                    "status", "success",
                    "analysisId", analysisResultId,
                    "mapType", "sample_plots",
                    "mapPath", mapPath,
                    "outputFormat", outputFormat
            );

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for sample plot map rendering: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error rendering sample plot map: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to render sample plot map: " + e.getMessage(), e);
        }
    }
}
