package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO for DEM download status response.
 * Contains current status of DEM download and processing.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DEMStatusResponse {
    private UUID demId;
    private String source;
    private String status;
    private LocalDateTime downloadedAt;
    private String message;
    private Integer progressPercentage;
}
