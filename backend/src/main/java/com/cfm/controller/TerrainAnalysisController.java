package com.cfm.controller;

import com.cfm.dto.MapGenerationRequest;
import com.cfm.service.TerrainAnalysisService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * REST Controller for terrain analysis operations.
 * Handles slope and aspect calculation requests.
 */
@RestController
@RequestMapping("/terrain")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Terrain Analysis", description = "Endpoints for slope and aspect analysis")
public class TerrainAnalysisController {

    private final TerrainAnalysisService terrainAnalysisService;

    /**
     * Calculate slope from DEM.
     *
     * @param demId DEM UUID
     * @return Response with slope analysis status
     */
    @PostMapping("/slope")
    @Operation(summary = "Calculate slope", description = "Calculate slope from DEM and classify into categories")
    public ResponseEntity<?> calculateSlope(@RequestParam UUID demId) {
        try {
            log.info("Slope calculation request for DEM: {}", demId);
            var response = terrainAnalysisService.calculateSlope(demId);
            return ResponseEntity.accepted().body(response);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            log.error("Error calculating slope", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
        }
    }

    /**
     * Calculate aspect from DEM.
     *
     * @param demId DEM UUID
     * @return Response with aspect analysis status
     */
    @PostMapping("/aspect")
    @Operation(summary = "Calculate aspect", description = "Calculate aspect from DEM and classify into cardinal directions")
    public ResponseEntity<?> calculateAspect(@RequestParam UUID demId) {
        try {
            log.info("Aspect calculation request for DEM: {}", demId);
            var response = terrainAnalysisService.calculateAspect(demId);
            return ResponseEntity.accepted().body(response);
        } catch (IllegalArgumentException e) {
            log.warn("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            log.error("Error calculating aspect", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(e.getMessage());
        }
    }
}
