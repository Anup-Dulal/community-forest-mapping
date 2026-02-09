package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

/**
 * DTO for map generation request.
 * Specifies which maps to generate and analysis parameters.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class MapGenerationRequest {
    private UUID shapefileId;
    private Integer compartmentCount;
    private Double samplingIntensity;
    private Integer minSamplePlotsPerCompartment;
    private Boolean generateSlope;
    private Boolean generateAspect;
    private Boolean generateCompartments;
    private Boolean generateSamplePlots;
}
