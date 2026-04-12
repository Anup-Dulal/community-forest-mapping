package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * DTO representing the result of shapefile geometry validation.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ValidationResult {
    private Boolean isValid;
    private String status; // valid, warning, error
    private List<ValidationWarning> warnings;
    private Double boundaryArea; // in square kilometers
    private String projection;
    private String message;
}
