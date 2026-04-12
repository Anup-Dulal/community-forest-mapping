package com.cfm.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.ser.std.ToStringSerializer;
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
    @JsonSerialize(using = ToStringSerializer.class)
    @JsonProperty("shapefileId")
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
