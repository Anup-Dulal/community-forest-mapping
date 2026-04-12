package com.cfm.service;

import com.cfm.model.AnalysisResult;
import com.cfm.model.Compartment;
import com.cfm.model.Shapefile;
import com.cfm.repository.AnalysisResultRepository;
import com.cfm.repository.CompartmentRepository;
import com.cfm.repository.ShapefileRepository;
import com.cfm.repository.DEMRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * Service for compartment generation and management.
 * Orchestrates equal-area compartment division via GIS microservice.
 * Requirement 6: Equal-Area Compartment Division
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CompartmentService {

    private final CompartmentRepository compartmentRepository;
    private final AnalysisResultRepository analysisResultRepository;
    private final ShapefileRepository shapefileRepository;
    private final DEMRepository demRepository;
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
            // Log all shapefiles in database
            long count = shapefileRepository.count();
            log.info("Total shapefiles in database: {}", count);
            
            // Get shapefile
            log.info("Attempting to find shapefile with ID: {}", shapefileId);
            Shapefile shapefile = shapefileRepository.findById(shapefileId)
                .orElseThrow(() -> {
                    log.error("Shapefile not found with ID: {}", shapefileId);
                    return new IllegalArgumentException("Shapefile not found: " + shapefileId);
                });
            
            log.info("Found shapefile: {}", shapefile.getId());

            // Get or create analysis result
            AnalysisResult analysis = analysisResultRepository.findByShapefileId(shapefileId)
                .orElse(AnalysisResult.builder()
                    .shapefile(shapefile)
                    .status("processing")
                    .build());

            // Link DEM if available
            var dem = demRepository.findByShapefileId(shapefileId);
            if (dem.isPresent()) {
                analysis.setDem(dem.get());
                log.info("Linked DEM to analysis result: {}", dem.get().getId());
            }

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
     * Generate hierarchical compartments (compartments with sub-compartments).
     *
     * @param shapefileId Shapefile UUID
     * @param compartmentSpecs List of compartment specifications with sub-compartment counts
     * @return Response with compartment generation status
     * @throws IllegalArgumentException if shapefile not found
     */
    public Map<String, Object> generateHierarchicalCompartments(
            UUID shapefileId, 
            List<Map<String, Integer>> compartmentSpecs) {
        
        log.info("Starting hierarchical compartment generation for shapefile: {}", shapefileId);
        log.info("Compartment specifications: {}", compartmentSpecs);

        try {
            // Get shapefile
            Shapefile shapefile = shapefileRepository.findById(shapefileId)
                .orElseThrow(() -> {
                    log.error("Shapefile not found with ID: {}", shapefileId);
                    return new IllegalArgumentException("Shapefile not found: " + shapefileId);
                });
            
            log.info("Found shapefile: {}", shapefile.getId());

            // Get or create analysis result
            AnalysisResult analysis = analysisResultRepository.findByShapefileId(shapefileId)
                .orElse(AnalysisResult.builder()
                    .shapefile(shapefile)
                    .status("processing")
                    .build());

            // Link DEM if available
            var dem = demRepository.findByShapefileId(shapefileId);
            if (dem.isPresent()) {
                analysis.setDem(dem.get());
                log.info("Linked DEM to analysis result: {}", dem.get().getId());
            }

            analysis.setStatus("processing");
            AnalysisResult savedAnalysis = analysisResultRepository.save(analysis);

            // Call GIS service to generate hierarchical compartments
            generateHierarchicalCompartmentsViaGIS(
                savedAnalysis.getId(), 
                shapefile.getGeometry(), 
                compartmentSpecs
            );

            return Map.of(
                "analysisId", savedAnalysis.getId().toString(),
                "status", "processing",
                "message", "Hierarchical compartment generation started"
            );

        } catch (Exception e) {
            log.error("Error starting hierarchical compartment generation", e);
            throw new RuntimeException("Failed to start hierarchical compartment generation: " + e.getMessage());
        }
    }

    /**
     * Generate hierarchical compartments via GIS microservice.
     * Uses a separate thread to avoid blocking the HTTP request.
     *
     * @param analysisId Analysis result UUID
     * @param boundaryWkt Boundary geometry as WKT string
     * @param compartmentSpecs List of compartment specifications
     */
    private void generateHierarchicalCompartmentsViaGIS(
            UUID analysisId, 
            String boundaryWkt, 
            List<Map<String, Integer>> compartmentSpecs) {
        
        // Get reference to self for calling transactional methods from background thread
        final CompartmentService self = this;
        
        new Thread(() -> {
            try {
                log.info("Background thread started for hierarchical compartment generation: {}", analysisId);

                // Prepare request
                Map<String, Object> request = new HashMap<>();
                request.put("analysisId", analysisId.toString());
                request.put("boundaryWkt", boundaryWkt);
                request.put("compartments", compartmentSpecs);

                // Call GIS service
                String url = gisServiceUrl + "/api/compartments/generate-hierarchical";
                log.info("Calling GIS service at: {}", url);
                
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.postForObject(url, request, Map.class);

                log.info("GIS service response received: {}", response != null ? "success" : "null");

                if (response != null && "success".equals(response.get("status"))) {
                    log.info("GIS service returned success, updating database...");
                    // Call transactional method through self reference
                    self.updateAnalysisWithHierarchicalCompartments(analysisId, response);
                    log.info("Database update completed for analysis: {}", analysisId);
                } else {
                    log.error("GIS service returned non-success status: {}", response);
                    self.updateAnalysisStatus(analysisId, "error");
                }

            } catch (Exception e) {
                log.error("Error in background thread for hierarchical compartment generation", e);
                log.error("Exception type: {}", e.getClass().getName());
                log.error("Exception message: {}", e.getMessage());
                if (e.getCause() != null) {
                    log.error("Cause: {}", e.getCause().getMessage());
                }
                try {
                    self.updateAnalysisStatus(analysisId, "error");
                } catch (Exception ex) {
                    log.error("Error updating analysis status to error", ex);
                }
            }
        }).start();
        
        log.info("Background thread dispatched for analysis: {}", analysisId);
    }

    /**
     * Update analysis result with hierarchical compartment generation result.
     * Parses the nested compartment/sub-compartment structure and saves to database.
     * This method must be public to allow proper transaction management when called from background threads.
     */
    @Transactional
    @SuppressWarnings("unchecked")
    public void updateAnalysisWithHierarchicalCompartments(UUID analysisId, Map<String, Object> response) {
        try {
            log.info("Starting database update for analysis: {}", analysisId);
            
            AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + analysisId));
            
            log.info("Found analysis result, updating compartment geometry path");
            
            String compartmentGeometryPath = (String) response.get("compartmentGeometryPath");
            analysis.setCompartmentGeometryPath(compartmentGeometryPath);
            
            // Parse hierarchical compartments from response
            List<Map<String, Object>> compartments = (List<Map<String, Object>>) response.get("compartments");
            
            log.info("Parsing {} compartments from response", compartments != null ? compartments.size() : 0);
            
            if (compartments != null) {
                int totalSaved = 0;
                for (Map<String, Object> compData : compartments) {
                    // Create parent compartment
                    Integer compNumber = ((Number) compData.get("number")).intValue();
                    String compLabel = (String) compData.get("label");
                    String compGeometry = (String) compData.get("geometry");
                    Double compArea = ((Number) compData.get("area")).doubleValue();
                    
                    log.debug("Creating parent compartment: {}", compLabel);
                    
                    Compartment parentCompartment = Compartment.builder()
                        .analysisResult(analysis)
                        .compartmentId(compLabel)
                        .label(compLabel)
                        .level(0)
                        .subCompartmentNumber(compNumber)
                        .area(java.math.BigDecimal.valueOf(compArea))
                        .geometry(compGeometry)
                        .samplePlotCount(0)
                        .build();
                    
                    Compartment savedParent = compartmentRepository.save(parentCompartment);
                    totalSaved++;
                    log.info("Saved parent compartment: {} (ID: {})", compLabel, savedParent.getId());
                    
                    // Create sub-compartments
                    List<Map<String, Object>> subCompartments = 
                        (List<Map<String, Object>>) compData.get("subCompartments");
                    
                    if (subCompartments != null) {
                        log.debug("Creating {} sub-compartments for {}", subCompartments.size(), compLabel);
                        
                        for (Map<String, Object> subData : subCompartments) {
                            Integer subNumber = ((Number) subData.get("number")).intValue();
                            String subLabel = (String) subData.get("label");
                            String subGeometry = (String) subData.get("geometry");
                            Double subArea = ((Number) subData.get("area")).doubleValue();
                            
                            Compartment subCompartment = Compartment.builder()
                                .analysisResult(analysis)
                                .parentCompartment(savedParent)
                                .compartmentId(subLabel)
                                .label(subLabel)
                                .level(1)
                                .subCompartmentNumber(subNumber)
                                .area(java.math.BigDecimal.valueOf(subArea))
                                .geometry(subGeometry)
                                .samplePlotCount(0)
                                .build();
                            
                            compartmentRepository.save(subCompartment);
                            totalSaved++;
                            log.debug("Saved sub-compartment: {}", subLabel);
                        }
                    }
                }
                
                log.info("Saved {} total compartments/sub-compartments to database", totalSaved);
            }
            
            log.info("Setting analysis status to complete");
            analysis.setStatus("complete");
            analysisResultRepository.save(analysis);
            log.info("Analysis result updated successfully with status=complete");
            
        } catch (Exception e) {
            log.error("Error updating analysis with hierarchical compartments", e);
            log.error("Stack trace:", e);
            throw new RuntimeException("Failed to update analysis result", e);
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
     * Get analysis result details.
     *
     * @param analysisId Analysis result UUID
     * @return Map with analysis result details including DEM ID
     */
    public Map<String, Object> getAnalysisResultDetails(UUID analysisId) {
        try {
            AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisId));
            
            // Use HashMap instead of Map.of() to allow null values
            Map<String, Object> details = new HashMap<>();
            details.put("analysisId", analysis.getId().toString());
            details.put("demId", analysis.getDem() != null ? analysis.getDem().getId().toString() : null);
            details.put("shapefileId", analysis.getShapefile().getId().toString());
            details.put("status", analysis.getStatus());
            details.put("compartmentGeometryPath", analysis.getCompartmentGeometryPath() != null ? analysis.getCompartmentGeometryPath() : "");
            details.put("samplePlotGeometryPath", analysis.getSamplePlotGeometryPath() != null ? analysis.getSamplePlotGeometryPath() : "");
            details.put("slopeRasterPath", analysis.getSlopeRasterPath() != null ? analysis.getSlopeRasterPath() : "");
            details.put("aspectRasterPath", analysis.getAspectRasterPath() != null ? analysis.getAspectRasterPath() : "");
            
            return details;
        } catch (Exception e) {
            log.error("Error retrieving analysis result details", e);
            throw new RuntimeException("Failed to retrieve analysis result details: " + e.getMessage());
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

                // Convert WKT to GeoJSON
                Map<String, Object> geometryGeoJson = convertWktToGeoJson(boundaryGeometry);
                
                // Prepare request
                Map<String, Object> request = new HashMap<>();
                request.put("analysisId", analysisId.toString());
                request.put("boundaryGeometry", geometryGeoJson);
                request.put("numCompartments", numCompartments);

                // Call GIS service
                String url = gisServiceUrl + "/api/compartments/generate";
                log.info("Calling GIS service at: {}", url);
                var response = restTemplate.postForObject(url, request, Map.class);

                log.info("GIS service response: {}", response);

                if (response != null && "success".equals(response.get("status"))) {
                    // Update analysis result in a new transaction
                    updateAnalysisWithCompartmentResult(analysisId, response);
                    log.info("Compartment generation successful for analysis: {}", analysisId);
                } else {
                    log.error("GIS service returned non-success status: {}", response);
                    updateAnalysisStatus(analysisId, "error");
                }

            } catch (Exception e) {
                log.error("Error generating compartments via GIS service", e);
                try {
                    updateAnalysisStatus(analysisId, "error");
                } catch (Exception ex) {
                    log.error("Error updating analysis status", ex);
                }
            }
        }).start();
    }

    /**
     * Convert WKT geometry string to GeoJSON format.
     * Simple implementation that handles basic polygon WKT.
     */
    private Map<String, Object> convertWktToGeoJson(String wkt) {
        try {
            // Simple WKT to GeoJSON conversion for POLYGON
            // Format: POLYGON ((x1 y1, x2 y2, ..., x1 y1))
            
            Map<String, Object> geoJson = new HashMap<>();
            geoJson.put("type", "Polygon");
            
            if (wkt.startsWith("POLYGON")) {
                // Extract coordinates from WKT
                String coordsStr = wkt.substring(wkt.indexOf("((") + 2, wkt.lastIndexOf("))"));
                String[] coordPairs = coordsStr.split(",");
                
                List<List<Double>> coordinates = new ArrayList<>();
                List<Double> ring = new ArrayList<>();
                
                for (String pair : coordPairs) {
                    String[] xy = pair.trim().split("\\s+");
                    if (xy.length == 2) {
                        ring.add(Double.parseDouble(xy[0]));
                        ring.add(Double.parseDouble(xy[1]));
                    }
                }
                
                // Create coordinate array for GeoJSON
                List<List<List<Double>>> coordinatesList = new ArrayList<>();
                List<List<Double>> ringCoords = new ArrayList<>();
                
                for (int i = 0; i < ring.size(); i += 2) {
                    List<Double> coord = new ArrayList<>();
                    coord.add(ring.get(i));
                    coord.add(ring.get(i + 1));
                    ringCoords.add(coord);
                }
                
                coordinatesList.add(ringCoords);
                geoJson.put("coordinates", coordinatesList);
            }
            
            return geoJson;
        } catch (Exception e) {
            log.error("Error converting WKT to GeoJSON: {}", wkt, e);
            // Return a default polygon if conversion fails
            Map<String, Object> defaultGeoJson = new HashMap<>();
            defaultGeoJson.put("type", "Polygon");
            List<List<List<Double>>> coords = new ArrayList<>();
            List<List<Double>> ring = new ArrayList<>();
            ring.add(Arrays.asList(0.0, 0.0));
            ring.add(Arrays.asList(1.0, 0.0));
            ring.add(Arrays.asList(1.0, 1.0));
            ring.add(Arrays.asList(0.0, 1.0));
            ring.add(Arrays.asList(0.0, 0.0));
            coords.add(ring);
            defaultGeoJson.put("coordinates", coords);
            return defaultGeoJson;
        }
    }

    /**
     * Update analysis result with compartment generation result.
     * This method is called from a separate thread, so it needs its own transaction.
     */
    @Transactional
    private void updateAnalysisWithCompartmentResult(UUID analysisId, Map<String, Object> response) {
        try {
            AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + analysisId));
            
            String compartmentGeometryPath = (String) response.get("compartmentGeometryPath");
            analysis.setCompartmentGeometryPath(compartmentGeometryPath);
            
            // Parse compartments from response and save to database
            @SuppressWarnings("unchecked")
            Map<String, Object> statistics = (Map<String, Object>) response.get("statistics");
            if (statistics != null) {
                Integer numCompartments = ((Number) statistics.get("num_compartments")).intValue();
                
                // Create compartment entities from the GIS response
                for (int i = 1; i <= numCompartments; i++) {
                    Compartment compartment = Compartment.builder()
                        .analysisResult(analysis)
                        .compartmentId("C" + i)
                        .area(java.math.BigDecimal.ZERO) // Will be calculated from geometry
                        .geometry("") // Geometry will be loaded from GeoJSON file
                        .samplePlotCount(0)
                        .build();
                    compartmentRepository.save(compartment);
                }
                
                log.info("Saved {} compartments to database", numCompartments);
            }
            
            analysis.setStatus("complete");
            analysisResultRepository.save(analysis);
            log.info("Analysis result updated with compartment geometry path");
        } catch (Exception e) {
            log.error("Error updating analysis with compartment result", e);
            throw new RuntimeException("Failed to update analysis result", e);
        }
    }

    /**
     * Update analysis status.
     * This method is called from a separate thread, so it needs its own transaction.
     * Must be public to allow proper transaction management when called from background threads.
     */
    @Transactional
    public void updateAnalysisStatus(UUID analysisId, String status) {
        try {
            AnalysisResult analysis = analysisResultRepository.findById(analysisId)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + analysisId));
            analysis.setStatus(status);
            analysisResultRepository.save(analysis);
            log.info("Analysis status updated to: {}", status);
        } catch (Exception e) {
            log.error("Error updating analysis status", e);
        }
    }
}
