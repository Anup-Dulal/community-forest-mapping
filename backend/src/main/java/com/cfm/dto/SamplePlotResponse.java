package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

/**
 * Response DTO for sample plot generation operations.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SamplePlotResponse {

    private String status;
    private UUID analysisId;
    private String samplePlotGeometryPath;
    private Integer totalPlots;
    private Integer minPlots;
    private Integer maxPlots;
    private Double avgPlots;
    private String errorMessage;
}
