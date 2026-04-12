package com.cfm.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.NotNull;

/**
 * DTO for specifying a compartment and its sub-compartment count
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CompartmentSpecDTO {

    @NotNull(message = "Compartment number is required")
    @Min(value = 1, message = "Compartment number must be at least 1")
    private Integer compartmentNumber;

    @NotNull(message = "Sub-compartment count is required")
    @Min(value = 1, message = "Sub-compartment count must be at least 1")
    @Max(value = 20, message = "Sub-compartment count cannot exceed 20")
    private Integer subCompartmentCount;
}
