package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO representing a validation warning for shapefile geometry.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ValidationWarning {
    private String type; // self-intersection, projection, attributes, area, other
    private String message;
    private String severity; // warning, error
    private Boolean autoRepairAvailable;
}
