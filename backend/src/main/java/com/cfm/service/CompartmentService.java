package com.cfm.service;

import com.cfm.model.AnalysisResult;
import com.cfm.model.Compartment;
import com.cfm.model.Shapefile;
import com.cfm.repository.AnalysisResultRepository;
import com.cfm.repository.CompartmentRepository;
import com.cfm.repository.ShapefileRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Service for compartment generation and management.
 * Orchestrates equal-area compartment division via GIS microservice.
 * Requirement 6: Equal-Area Compartment Division
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CompartmentService {

    private final CompartmentRepository compartmentRepository;
    private final AnalysisResultRepository analysisResultRepository;
    private final ShapefileRepository shapefileRepository;
    private final RestTemplate restTemplate;

    @Value("${app.gis-service-url:http://localhost:8001}")
    private String gisServiceUrl;

    /**
     * Generate equal-area compartments for a shapefile.
     *
     * @param shapefileId Shapefile UUID
     * @param numCompartments Number of compartments to generate
     * @return Response with compartment generation status
     * @throws IllegalArgumentException if shapefile not found
     */
    public Map<String, Object> generateCompartments(UUID shapefileId, Integer numCompartments) {
        log.info("Starting compartment generation for shapefile: {} with {} compartments", 
            shapefileId, numCompartments);

        try {
            // Get shapefile
            Shapefile shapefile = shapefileRepository.findById(shapefileId)
                .orElseThrow(() -> new IllegalArgumentException("Shapefile not found: " + shapefileId));

            // Get or create analysis result
            AnalysisResult analysis = analysisResultRepository.findByShapefileId(shapefileId)
                .orElse(AnalysisResult.builder()
                    .shapefile(shapefile)
                    .status("processing")
                    .build());

            analysis.setStatus("processing");
            AnalysisResult savedAnalysis = analysisResultRepository.save(analysis);

            // Call GIS service to generate compartments
            // shapefile.getGeometry() returns WKT string
            generateCompartmentsViaGIS(savedAnalysis.getId(), shapefile.getGeometry(), numCompartments);

            return Map.of(
                "analysisId", savedAnalysis.getId().toString(),
                "status", "processing",
                "message", "Compartment generation started"
            );

        } catch (Exception e) {
            log.error("Error starting compartment generation", e);
            throw new RuntimeException("Failed to start compartment generation: " + e.getMessage());
        }
    }

    /**
     * Get compartments for an analysis result.
     *
     * @param analysisId Analysis result UUID
     * @return List of compartments
     */
    public List<Compartment> getCompartmentsByAnalysisId(UUID analysisId) {
        try {
            return compartmentRepository.findByAnalysisResultId(analysisId);
        } catch (Exception e) {
            log.error("Error retrieving compartments", e);
            throw new RuntimeException("Failed to retrieve compartments: " + e.getMessage());
        }
    }

    /**
     * Generate compartments via GIS microservice.
     * Passes WKT geometry string to GIS service for compartment generation.
     *
     * @param analysisId Analysis result UUID
     * @param boundaryGeometry Boundary geometry as WKT string
     * @param numCompartments Number of compartments
     */
    private void generateCompartmentsViaGIS(UUID analysisId, String boundaryGeometry, Integer numCompartments) {
        new Thread(() -> {
            try {
                log.info("Generating compartments via GIS service for analysis: {}", analysisId);

                // Prepare request - boundaryGeometry is a WKT string
                Map<String, Object> request = new HashMap<>();
                request.put("analysisId", analysisId.toString());
                request.put("boundaryGeometry", boundaryGeometry != null ? boundaryGeometry : "");
                request.put("numCompartments", numCompartments);

                // Call GIS service
                String url = gisServiceUrl + "/api/compartments/generate";
                var response = restTemplate.postForObject(url, request, Map.class);

                if (response != null && "success".equals(response.get("status"))) {
                    // Update analysis result
                    AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                        .orElseThrow();
                    analysis.setCompartmentGeometryPath((String) response.get("compartmentGeometryPath"));
                    analysis.setStatus("complete");
                    analysisResultRepository.save(analysis);

                    log.info("Compartment generation successful for analysis: {}", analysisId);
                }

            } catch (Exception e) {
                log.error("Error generating compartments via GIS service", e);
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
