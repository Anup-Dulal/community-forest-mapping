package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.Size;
import java.util.List;

/**
 * DTO for hierarchical compartment generation request
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class HierarchicalCompartmentRequestDTO {

    @NotBlank(message = "Boundary WKT is required")
    private String boundaryWkt;

    @NotBlank(message = "Analysis ID is required")
    private String analysisId;

    @NotEmpty(message = "At least one compartment specification is required")
    @Size(max = 10, message = "Maximum 10 compartments allowed")
    @Valid
    private List<CompartmentSpecDTO> compartments;

    /**
     * Get total number of sub-compartments across all compartments
     */
    public int getTotalSubCompartments() {
        return compartments.stream()
                .mapToInt(CompartmentSpecDTO::getSubCompartmentCount)
                .sum();
    }

    /**
     * Get total number of compartments
     */
    public int getTotalCompartments() {
        return compartments.size();
    }
}
