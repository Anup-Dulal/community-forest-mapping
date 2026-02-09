package com.cfm.service;

import com.cfm.model.AnalysisResult;
import com.cfm.model.DEM;
import com.cfm.repository.AnalysisResultRepository;
import com.cfm.repository.DEMRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service for terrain analysis operations.
 * Orchestrates slope and aspect calculation via GIS microservice.
 * Requirements 4 & 5: Slope and Aspect Analysis
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TerrainAnalysisService {

    private final DEMRepository demRepository;
    private final AnalysisResultRepository analysisResultRepository;
    private final RestTemplate restTemplate;

    @Value("${app.gis-service-url:http://localhost:8001}")
    private String gisServiceUrl;

    /**
     * Calculate slope from DEM.
     * Orchestrates slope calculation via GIS microservice.
     *
     * @param demId DEM UUID
     * @return Response with slope analysis status
     * @throws IllegalArgumentException if DEM not found
     */
    public Map<String, Object> calculateSlope(UUID demId) {
        log.info("Starting slope calculation for DEM: {}", demId);

        try {
            // Get DEM
            DEM dem = demRepository.findById(demId)
                .orElseThrow(() -> new IllegalArgumentException("DEM not found: " + demId));

            // Get or create analysis result
            AnalysisResult analysis = analysisResultRepository.findByShapefileId(dem.getShapefile().getId())
                .orElse(AnalysisResult.builder()
                    .shapefile(dem.getShapefile())
                    .dem(dem)
                    .status("processing")
                    .build());

            analysis.setStatus("processing");
            AnalysisResult savedAnalysis = analysisResultRepository.save(analysis);

            // Call GIS service to calculate slope
            calculateSlopeViaGIS(savedAnalysis.getId(), dem.getClippedRasterPath());

            return Map.of(
                "analysisId", savedAnalysis.getId().toString(),
                "status", "processing",
                "message", "Slope calculation started"
            );

        } catch (Exception e) {
            log.error("Error starting slope calculation", e);
            throw new RuntimeException("Failed to start slope calculation: " + e.getMessage());
        }
    }

    /**
     * Calculate aspect from DEM.
     * Orchestrates aspect calculation via GIS microservice.
     *
     * @param demId DEM UUID
     * @return Response with aspect analysis status
     * @throws IllegalArgumentException if DEM not found
     */
    public Map<String, Object> calculateAspect(UUID demId) {
        log.info("Starting aspect calculation for DEM: {}", demId);

        try {
            // Get DEM
            DEM dem = demRepository.findById(demId)
                .orElseThrow(() -> new IllegalArgumentException("DEM not found: " + demId));

            // Get or create analysis result
            AnalysisResult analysis = analysisResultRepository.findByShapefileId(dem.getShapefile().getId())
                .orElse(AnalysisResult.builder()
                    .shapefile(dem.getShapefile())
                    .dem(dem)
                    .status("processing")
                    .build());

            analysis.setStatus("processing");
            AnalysisResult savedAnalysis = analysisResultRepository.save(analysis);

            // Call GIS service to calculate aspect
            calculateAspectViaGIS(savedAnalysis.getId(), dem.getClippedRasterPath());

            return Map.of(
                "analysisId", savedAnalysis.getId().toString(),
                "status", "processing",
                "message", "Aspect calculation started"
            );

        } catch (Exception e) {
            log.error("Error starting aspect calculation", e);
            throw new RuntimeException("Failed to start aspect calculation: " + e.getMessage());
        }
    }

    /**
     * Calculate slope via GIS microservice.
     *
     * @param analysisId Analysis result UUID
     * @param demPath Path to clipped DEM
     */
    private void calculateSlopeViaGIS(UUID analysisId, String demPath) {
        new Thread(() -> {
            try {
                log.info("Calculating slope via GIS service for analysis: {}", analysisId);

                // Prepare request
                Map<String, Object> request = new HashMap<>();
                request.put("analysisId", analysisId.toString());
                request.put("demPath", demPath);

                // Call GIS service
                String url = gisServiceUrl + "/api/terrain/slope";
                var response = restTemplate.postForObject(url, request, Map.class);

                if (response != null && "success".equals(response.get("status"))) {
                    // Update analysis result
                    AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                        .orElseThrow();
                    analysis.setSlopeRasterPath((String) response.get("slopeRasterPath"));
                    analysis.setStatus("complete");
                    analysis.setGeneratedAt(LocalDateTime.now());
                    analysisResultRepository.save(analysis);

                    log.info("Slope calculation successful for analysis: {}", analysisId);
                }

            } catch (Exception e) {
                log.error("Error calculating slope via GIS service", e);
                try {
                    AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                        .orElseThrow();
                    analysis.setStatus("error");
                    analysisResultRepository.save(analysis);
                } catch (Exception ex) {
                    log.error("Error updating analysis status", ex);
                }
            }
        }).start();
    }

    /**
     * Calculate aspect via GIS microservice.
     *
     * @param analysisId Analysis result UUID
     * @param demPath Path to clipped DEM
     */
    private void calculateAspectViaGIS(UUID analysisId, String demPath) {
        new Thread(() -> {
            try {
                log.info("Calculating aspect via GIS service for analysis: {}", analysisId);

                // Prepare request
                Map<String, Object> request = new HashMap<>();
                request.put("analysisId", analysisId.toString());
                request.put("demPath", demPath);

                // Call GIS service
                String url = gisServiceUrl + "/api/terrain/aspect";
                var response = restTemplate.postForObject(url, request, Map.class);

                if (response != null && "success".equals(response.get("status"))) {
                    // Update analysis result
                    AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                        .orElseThrow();
                    analysis.setAspectRasterPath((String) response.get("aspectRasterPath"));
                    analysis.setStatus("complete");
                    analysis.setGeneratedAt(LocalDateTime.now());
                    analysisResultRepository.save(analysis);

                    log.info("Aspect calculation successful for analysis: {}", analysisId);
                }

            } catch (Exception e) {
                log.error("Error calculating aspect via GIS service", e);
                try {
                    AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                        .orElseThrow();
                    analysis.setStatus("error");
                    analysisResultRepository.save(analysis);
                } catch (Exception ex) {
                    log.error("Error updating analysis status", ex);
                }
            }
        }).start();
    }
}
