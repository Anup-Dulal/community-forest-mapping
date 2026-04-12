package com.cfm.controller;

import com.cfm.dto.HierarchicalCompartmentRequestDTO;
import com.cfm.service.CompartmentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * REST Controller for compartment generation and management.
 * Handles equal-area compartment division of forest boundaries.
 * Supports both flat and hierarchical (compartment/sub-compartment) structures.
 */
@RestController
@RequestMapping("/api/compartments")
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
        @RequestParam String shapefileId,
        @RequestParam(defaultValue = "4") Integer numCompartments
    ) {
        try {
            UUID id = UUID.fromString(shapefileId);
            log.info("Compartment generation request for shapefile: {} with {} compartments", 
                id, numCompartments);
            var response = compartmentService.generateCompartments(id, numCompartments);
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
     * Generate hierarchical compartments (compartments with sub-compartments).
     *
     * @param request Hierarchical compartment generation request
     * @return Response with compartment generation status
     */
    @PostMapping("/generate-hierarchical")
    @Operation(
        summary = "Generate hierarchical compartments", 
        description = "Generate compartments with configurable sub-compartments (e.g., C1S1, C1S2, C2S1, etc.)"
    )
    public ResponseEntity<?> generateHierarchicalCompartments(
        @Valid @RequestBody HierarchicalCompartmentRequestDTO request
    ) {
        try {
            UUID shapefileId = UUID.fromString(request.getAnalysisId());
            
            log.info("Hierarchical compartment generation request for shapefile: {}", shapefileId);
            log.info("Total compartments: {}, Total sub-compartments: {}", 
                request.getTotalCompartments(), 
                request.getTotalSubCompartments());
            
            // Convert DTO to service format
            List<Map<String, Integer>> compartmentSpecs = request.getCompartments().stream()
                .map(spec -> Map.of(
                    "compartmentNumber", spec.getCompartmentNumber(),
                    "subCompartmentCount", spec.getSubCompartmentCount()
                ))
                .collect(Collectors.toList());
            
            var response = compartmentService.generateHierarchicalCompartments(
                shapefileId, 
                compartmentSpecs
            );
            
            return ResponseEntity.accepted().body(response);
            
        } catch (IllegalArgumentException e) {
            log.warn("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Invalid request",
                "message", e.getMessage()
            ));
        } catch (Exception e) {
            log.error("Error generating hierarchical compartments", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                "error", "Internal server error",
                "message", e.getMessage()
            ));
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
    public ResponseEntity<?> getCompartments(@PathVariable String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Retrieving compartments for analysis: {}", id);
            var compartments = compartmentService.getCompartmentsByAnalysisId(id);
            return ResponseEntity.ok(compartments);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid UUID format: {}", analysisId);
            return ResponseEntity.badRequest().body("Invalid analysis ID format");
        } catch (Exception e) {
            log.error("Error retrieving compartments", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
        }
    }

    /**
     * Get analysis result details.
     *
     * @param analysisId Analysis result UUID
     * @return Analysis result details including DEM ID
     */
    @GetMapping("/{analysisId}/details")
    @Operation(summary = "Get analysis details", description = "Retrieve analysis result details including DEM ID")
    public ResponseEntity<?> getAnalysisDetails(@PathVariable String analysisId) {
        try {
            UUID id = UUID.fromString(analysisId);
            log.info("Retrieving analysis details for: {}", id);
            var details = compartmentService.getAnalysisResultDetails(id);
            return ResponseEntity.ok(details);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid UUID format: {}", analysisId);
            return ResponseEntity.badRequest().body("Invalid analysis ID format");
        } catch (Exception e) {
            log.error("Error retrieving analysis details", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
        }
    }
}
