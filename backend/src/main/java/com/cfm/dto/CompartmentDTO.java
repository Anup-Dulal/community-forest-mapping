package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * DTO for compartment data with hierarchical structure
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CompartmentDTO {

    private String id;
    private String label;
    private Integer number;
    private Integer level;
    private BigDecimal area;
    private String geometry;
    private String parentId;
    private Integer subCompartmentNumber;
    
    @Builder.Default
    private List<CompartmentDTO> subCompartments = new ArrayList<>();

    /**
     * Check if this is a top-level compartment
     */
    public boolean isTopLevel() {
        return level != null && level == 0;
    }

    /**
     * Check if this is a sub-compartment
     */
    public boolean isSubCompartment() {
        return level != null && level == 1;
    }

    /**
     * Get total number of sub-compartments
     */
    public int getSubCompartmentCount() {
        return subCompartments.size();
    }
}
