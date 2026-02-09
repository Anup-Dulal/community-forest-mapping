package com.cfm.controller;

import com.cfm.service.CompartmentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * REST Controller for compartment generation and management.
 * Handles equal-area compartment division of forest boundaries.
 */
@RestController
@RequestMapping("/compartments")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Compartment Management", description = "Endpoints for compartment generation and management")
public class CompartmentController {

    private final CompartmentService compartmentService;

    /**
     * Generate equal-area compartments for a shapefile.
     *
     * @param shapefileId Shapefile UUID
     * @param numCompartments Number of compartments to generate
     * @return Response with compartment generation status
     */
    @PostMapping("/generate")
    @Operation(summary = "Generate compartments", description = "Generate equal-area compartments from boundary")
    public ResponseEntity<?> generateCompartments(
        @RequestParam UUID shapefileId,
        @RequestParam(defaultValue = "4") Integer numCompartments
    ) {
        try {
            log.info("Compartment generation request for shapefile: {} with {} compartments", 
                shapefileId, numCompartments);
            var response = compartmentService.generateCompartments(shapefileId, numCompartments);
            return ResponseEntity.accepted().body(response);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            log.error("Error generating compartments", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
        }
    }

    /**
     * Get compartments for an analysis result.
     *
     * @param analysisId Analysis result UUID
     * @return List of compartments
     */
    @GetMapping("/analysis/{analysisId}")
    @Operation(summary = "Get compartments", description = "Retrieve compartments for an analysis result")
    public ResponseEntity<?> getCompartments(@PathVariable UUID analysisId) {
        try {
            log.info("Retrieving compartments for analysis: {}", analysisId);
            var compartments = compartmentService.getCompartmentsByAnalysisId(analysisId);
            return ResponseEntity.ok(compartments);
        } catch (Exception e) {
            log.error("Error retrieving compartments", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
        }
    }
}
