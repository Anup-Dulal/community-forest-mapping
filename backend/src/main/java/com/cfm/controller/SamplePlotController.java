package com.cfm.controller;

import com.cfm.dto.SamplePlotResponse;
import com.cfm.model.SamplePlot;
import com.cfm.service.SamplePlotService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * REST Controller for sample plot operations.
 * Provides endpoints for generating sample plots and converting coordinates.
 */
@Slf4j
@RestController
@RequestMapping("/api/sample-plots")
@CrossOrigin(origins = "*", maxAge = 3600)
public class SamplePlotController {

    @Autowired
    private SamplePlotService samplePlotService;

    /**
     * Generate sample plots for compartments.
     *
     * @param analysisResultId ID of the analysis result
     * @param samplingIntensity Sampling intensity as fraction (default 0.02 = 2%)
     * @param minPlotsPerCompartment Minimum plots per compartment (default 5)
     * @param distributionMethod "systematic" or "random" (default "systematic")
     * @return SamplePlotResponse with generation status
     */
    @PostMapping("/generate")
    public ResponseEntity<?> generateSamplePlots(
            @RequestParam String analysisResultId,
            @RequestParam(required = false) Double samplingIntensity,
            @RequestParam(required = false) Integer minPlotsPerCompartment,
            @RequestParam(required = false) String distributionMethod
    ) {
        try {
            UUID id = UUID.fromString(analysisResultId);
            log.info("Generating sample plots for analysis: {}", id);

            SamplePlotResponse response = samplePlotService.generateSamplePlots(
                    id,
                    samplingIntensity,
                    minPlotsPerCompartment,
                    distributionMethod
            );

            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error generating sample plots: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to generate sample plots: " + e.getMessage())
            );
        }
    }

    /**
     * Generate sample plots for hierarchical compartments (sub-compartments).
     * Ensures minimum 5 plots per SUB-COMPARTMENT (not parent compartment).
     *
     * @param request Map containing analysisId, compartmentGeometryPath, samplingIntensity, etc.
     * @return Response with generation status
     */
    @PostMapping("/generate-hierarchical")
    public ResponseEntity<?> generateHierarchicalSamplePlots(
            @RequestBody Map<String, Object> request
    ) {
        try {
            String analysisId = (String) request.get("analysisId");
            String compartmentGeometryPath = (String) request.get("compartmentGeometryPath");
            Double samplingIntensity = request.containsKey("samplingIntensity") ? 
                ((Number) request.get("samplingIntensity")).doubleValue() : 0.02;
            Integer minPlotsPerCompartment = request.containsKey("minPlotsPerCompartment") ? 
                ((Number) request.get("minPlotsPerCompartment")).intValue() : 5;
            String distributionMethod = (String) request.getOrDefault("distributionMethod", "systematic");

            log.info("Generating hierarchical sample plots for analysis: {}", analysisId);
            log.info("Compartment geometry path: {}", compartmentGeometryPath);

            SamplePlotResponse response = samplePlotService.generateHierarchicalSamplePlots(
                    UUID.fromString(analysisId),
                    compartmentGeometryPath,
                    samplingIntensity,
                    minPlotsPerCompartment,
                    distributionMethod
            );

            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error generating hierarchical sample plots: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to generate hierarchical sample plots: " + e.getMessage())
            );
        }
    }

    /**
     * Get all sample plots for an analysis result.
     *
     * @param analysisResultId ID of the analysis result
     * @return List of sample plots
     */
    @GetMapping("/analysis/{analysisResultId}")
    public ResponseEntity<?> getSamplePlotsByAnalysisResult(
            @PathVariable String analysisResultId
    ) {
        try {
            UUID id = UUID.fromString(analysisResultId);
            List<SamplePlot> samplePlots = samplePlotService.getSamplePlotsByAnalysisResult(id);
            return ResponseEntity.ok(samplePlots);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid UUID format: {}", analysisResultId);
            return ResponseEntity.badRequest().body(
                    Map.of("error", "Invalid analysis ID format")
            );
        } catch (Exception e) {
            log.error("Error retrieving sample plots: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to retrieve sample plots: " + e.getMessage())
            );
        }
    }

    /**
     * Get all sample plots for a compartment.
     *
     * @param compartmentId ID of the compartment
     * @return List of sample plots
     */
    @GetMapping("/compartment/{compartmentId}")
    public ResponseEntity<?> getSamplePlotsByCompartment(
            @PathVariable String compartmentId
    ) {
        try {
            UUID id = UUID.fromString(compartmentId);
            List<SamplePlot> samplePlots = samplePlotService.getSamplePlotsByCompartment(id);
            return ResponseEntity.ok(samplePlots);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid UUID format: {}", compartmentId);
            return ResponseEntity.badRequest().body(
                    Map.of("error", "Invalid compartment ID format")
            );
        } catch (Exception e) {
            log.error("Error retrieving sample plots: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to retrieve sample plots: " + e.getMessage())
            );
        }
    }

    /**
     * Convert sample plot coordinates to UTM.
     *
     * @param samplePlotId ID of the sample plot
     * @return Map with UTM coordinates
     */
    @PostMapping("/{samplePlotId}/convert-to-utm")
    public ResponseEntity<?> convertCoordinatesToUTM(
            @PathVariable String samplePlotId
    ) {
        try {
            UUID id = UUID.fromString(samplePlotId);
            log.info("Converting coordinates for sample plot: {}", id);

            Map<String, Object> result = samplePlotService.convertCoordinatesToUTM(id);

            return ResponseEntity.ok(result);

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument: {}", e.getMessage());
            return ResponseEntity.badRequest().body(
                    Map.of("error", e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error converting coordinates: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to convert coordinates: " + e.getMessage())
            );
        }
    }

    /**
     * Validate coordinate conversion round trip.
     *
     * @param latitude Original latitude
     * @param longitude Original longitude
     * @param toleranceMeters Acceptable error in meters (default 1.0)
     * @return Validation result
     */
    @PostMapping("/validate-coordinates")
    public ResponseEntity<?> validateCoordinateRoundTrip(
            @RequestParam Double latitude,
            @RequestParam Double longitude,
            @RequestParam(required = false) Double toleranceMeters
    ) {
        try {
            log.info("Validating coordinate round trip for lat: {}, lon: {}", latitude, longitude);

            Map<String, Object> result = samplePlotService.validateCoordinateRoundTrip(
                    latitude,
                    longitude,
                    toleranceMeters
            );

            return ResponseEntity.ok(result);

        } catch (Exception e) {
            log.error("Error validating coordinates: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                    Map.of("error", "Failed to validate coordinates: " + e.getMessage())
            );
        }
    }
}
