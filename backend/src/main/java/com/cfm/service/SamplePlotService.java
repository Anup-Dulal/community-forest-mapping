package com.cfm.service;

import com.cfm.dto.SamplePlotResponse;
import com.cfm.model.AnalysisResult;
import com.cfm.model.SamplePlot;
import com.cfm.repository.AnalysisResultRepository;
import com.cfm.repository.SamplePlotRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.math.BigDecimal;
import java.util.*;

/**
 * Service for orchestrating sample plot generation.
 * Coordinates with GIS microservice for plot generation and coordinate conversion.
 */
@Slf4j
@Service
public class SamplePlotService {

    @Autowired
    private SamplePlotRepository samplePlotRepository;

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Value("${gis.service.url:http://localhost:8001}")
    private String gisServiceUrl;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Generate sample plots for compartments.
     *
     * @param analysisResultId ID of the analysis result
     * @param samplingIntensity Sampling intensity as fraction (default 0.02 = 2%)
     * @param minPlotsPerCompartment Minimum plots per compartment (default 5)
     * @param distributionMethod "systematic" or "random"
     * @return SamplePlotResponse with generation status
     * @throws IllegalArgumentException if analysis result not found
     */
    public SamplePlotResponse generateSamplePlots(
            UUID analysisResultId,
            Double samplingIntensity,
            Integer minPlotsPerCompartment,
            String distributionMethod
    ) {
        try {
            // Validate analysis result exists
            AnalysisResult analysisResult = analysisResultRepository.findById(analysisResultId)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisResultId));

            // Get compartment geometry path
            String compartmentGeometryPath = analysisResult.getCompartmentGeometryPath();
            if (compartmentGeometryPath == null || compartmentGeometryPath.isEmpty()) {
                throw new IllegalArgumentException("Compartment geometry not found for analysis: " + analysisResultId);
            }

            // Set defaults
            if (samplingIntensity == null) {
                samplingIntensity = 0.02;
            }
            if (minPlotsPerCompartment == null) {
                minPlotsPerCompartment = 5;
            }
            if (distributionMethod == null || distributionMethod.isEmpty()) {
                distributionMethod = "systematic";
            }

            log.info("Generating sample plots for analysis: {}", analysisResultId);

            // Call GIS microservice to generate sample plots
            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("compartmentGeometryPath", compartmentGeometryPath);
            gisRequest.put("samplingIntensity", samplingIntensity);
            gisRequest.put("minPlotsPerCompartment", minPlotsPerCompartment);
            gisRequest.put("distributionMethod", distributionMethod);
            gisRequest.put("analysisId", analysisResultId.toString());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/sample-plots/generate",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to generate sample plots");
            }

            String samplePlotGeometryPath = gisResponse.get("samplePlotGeometryPath").asText();
            JsonNode statistics = gisResponse.get("statistics");

            // Store sample plot geometry path in analysis result
            analysisResult.setSamplePlotGeometryPath(samplePlotGeometryPath);
            analysisResultRepository.save(analysisResult);

            // Parse sample plots from GeoJSON and store in database
            parseSamplePlotsFromGeoJSON(analysisResult, samplePlotGeometryPath);

            log.info("Sample plots generated successfully for analysis: {}", analysisResultId);

            return SamplePlotResponse.builder()
                    .status("success")
                    .analysisId(analysisResultId)
                    .samplePlotGeometryPath(samplePlotGeometryPath)
                    .totalPlots(statistics.get("total_plots").asInt())
                    .minPlots(statistics.get("min_plots").asInt())
                    .maxPlots(statistics.get("max_plots").asInt())
                    .avgPlots(statistics.get("avg_plots").asDouble())
                    .build();

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for sample plot generation: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error generating sample plots: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to generate sample plots: " + e.getMessage(), e);
        }
    }

    /**
     * Convert sample plot coordinates from lat/lon to UTM.
     *
     * @param samplePlotId ID of the sample plot
     * @return Map with UTM coordinates
     * @throws IllegalArgumentException if sample plot not found
     */
    public Map<String, Object> convertCoordinatesToUTM(UUID samplePlotId) {
        try {
            SamplePlot samplePlot = samplePlotRepository.findById(samplePlotId)
                    .orElseThrow(() -> new IllegalArgumentException("Sample plot not found: " + samplePlotId));

            if (samplePlot.getLatitude() == null || samplePlot.getLongitude() == null) {
                throw new IllegalArgumentException("Sample plot coordinates not found");
            }

            // Call GIS microservice to convert coordinates
            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("conversionType", "lat_lon_to_utm");
            gisRequest.put("latitude", samplePlot.getLatitude().doubleValue());
            gisRequest.put("longitude", samplePlot.getLongitude().doubleValue());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/coordinates/convert",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to convert coordinates");
            }

            JsonNode result = gisResponse.get("result");

            // Update sample plot with UTM coordinates
            samplePlot.setEasting(new BigDecimal(result.get("easting").asDouble()));
            samplePlot.setNorthing(new BigDecimal(result.get("northing").asDouble()));
            samplePlotRepository.save(samplePlot);

            return objectMapper.convertValue(result, Map.class);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for coordinate conversion: {}", e.getMessage());
            throw e;
        } catch (Exception e) {
            log.error("Error converting coordinates: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to convert coordinates: " + e.getMessage(), e);
        }
    }

    /**
     * Validate coordinate conversion round trip.
     *
     * @param latitude Original latitude
     * @param longitude Original longitude
     * @param toleranceMeters Acceptable error in meters
     * @return Validation result
     */
    public Map<String, Object> validateCoordinateRoundTrip(
            Double latitude,
            Double longitude,
            Double toleranceMeters
    ) {
        try {
            if (toleranceMeters == null) {
                toleranceMeters = 1.0;
            }

            Map<String, Object> gisRequest = new HashMap<>();
            gisRequest.put("conversionType", "validate_round_trip");
            gisRequest.put("latitude", latitude);
            gisRequest.put("longitude", longitude);
            gisRequest.put("toleranceMeters", toleranceMeters);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(gisRequest, headers);

            JsonNode gisResponse = restTemplate.postForObject(
                    gisServiceUrl + "/api/coordinates/convert",
                    request,
                    JsonNode.class
            );

            if (gisResponse == null || !gisResponse.get("status").asText().equals("success")) {
                throw new RuntimeException("GIS service failed to validate coordinates");
            }

            return objectMapper.convertValue(gisResponse.get("result"), Map.class);

        } catch (Exception e) {
            log.error("Error validating coordinate round trip: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to validate coordinates: " + e.getMessage(), e);
        }
    }

    /**
     * Parse sample plots from GeoJSON file and store in database.
     * This is a placeholder implementation - in production, would parse actual GeoJSON.
     *
     * @param analysisResult The analysis result entity
     * @param samplePlotGeometryPath Path to the sample plot GeoJSON file
     */
    private void parseSamplePlotsFromGeoJSON(AnalysisResult analysisResult, String samplePlotGeometryPath) {
        try {
            // In a real implementation, this would:
            // 1. Read the GeoJSON file
            // 2. Parse each feature
            // 3. Create SamplePlot entities
            // 4. Save to database
            
            // For now, we log that this would be done
            log.info("Sample plots would be parsed from: {}", samplePlotGeometryPath);
            
        } catch (Exception e) {
            log.error("Error parsing sample plots from GeoJSON: {}", e.getMessage(), e);
            // Don't throw - this is optional for now
        }
    }

    /**
     * Get all sample plots for an analysis result.
     *
     * @param analysisResultId ID of the analysis result
     * @return List of sample plots
     */
    public List<SamplePlot> getSamplePlotsByAnalysisResult(UUID analysisResultId) {
        return samplePlotRepository.findByAnalysisResultId(analysisResultId);
    }

    /**
     * Get all sample plots for a compartment.
     *
     * @param compartmentId ID of the compartment
     * @return List of sample plots
     */
    public List<SamplePlot> getSamplePlotsByCompartment(UUID compartmentId) {
        return samplePlotRepository.findByCompartmentId(compartmentId);
    }
}
