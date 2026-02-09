package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

/**
 * DTO for shapefile upload response.
 * Contains metadata about the uploaded shapefile.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UploadResponse {
    private UUID shapefileId;
    private String filename;
    private String status;
    private String message;
    private BoundingBoxDTO boundingBox;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class BoundingBoxDTO {
        private Double minLat;
        private Double maxLat;
        private Double minLon;
        private Double maxLon;
    }
}
