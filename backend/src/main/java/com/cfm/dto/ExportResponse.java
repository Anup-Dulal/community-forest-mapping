package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

/**
 * DTO for export response.
 * Contains download link and metadata for exported files.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ExportResponse {
    private UUID exportId;
    private String filename;
    private String format;
    private String downloadUrl;
    private String message;
}
