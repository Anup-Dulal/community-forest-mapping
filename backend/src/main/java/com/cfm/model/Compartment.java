package com.cfm.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Entity representing a compartment or sub-compartment (equal-area subdivision) of the forest boundary.
 * Supports hierarchical structure: compartments can contain sub-compartments.
 * Geometry is stored as WKT (Well-Known Text) format for SQLite compatibility.
 */
@Entity
@Table(name = "compartments", indexes = {
    @Index(name = "idx_compartments_analysis_result_id", columnList = "analysis_result_id"),
    @Index(name = "idx_compartments_compartment_id", columnList = "compartment_id"),
    @Index(name = "idx_compartment_parent", columnList = "parent_compartment_id"),
    @Index(name = "idx_compartment_analysis_level", columnList = "analysis_result_id, level"),
    @Index(name = "idx_compartment_label", columnList = "label")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Compartment {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "analysis_result_id", nullable = false)
    private AnalysisResult analysisResult;

    @Column(nullable = false, length = 50)
    private String compartmentId; // C1, C2, C3, etc. (legacy field, kept for compatibility)

    @Column(nullable = false, length = 50)
    private String label; // C1, C1S1, C2S3, etc. (new hierarchical label)

    // Hierarchical structure fields
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_compartment_id")
    private Compartment parentCompartment;

    @OneToMany(mappedBy = "parentCompartment", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<Compartment> subCompartments = new ArrayList<>();

    @Column(nullable = false)
    @Builder.Default
    private Integer level = 0; // 0 = compartment, 1 = sub-compartment

    @Column(name = "sub_compartment_number")
    private Integer subCompartmentNumber; // Sequential number within parent (1, 2, 3...)

    @Column(precision = 15, scale = 2)
    private BigDecimal area;

    @Column(columnDefinition = "TEXT")
    private String geometry; // WKT format

    @Column(name = "sample_plot_count")
    @Builder.Default
    private Integer samplePlotCount = 0;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        
        // Set compartmentId to label for backward compatibility
        if (compartmentId == null && label != null) {
            compartmentId = label;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }

    /**
     * Helper method to check if this is a top-level compartment
     */
    public boolean isTopLevel() {
        return level == 0 && parentCompartment == null;
    }

    /**
     * Helper method to check if this is a sub-compartment
     */
    public boolean isSubCompartment() {
        return level == 1 && parentCompartment != null;
    }

    /**
     * Get the compartment number from label (e.g., "C1S3" -> 1)
     */
    public Integer getCompartmentNumber() {
        if (label == null) return null;
        String numStr = label.substring(1, label.indexOf('S') > 0 ? label.indexOf('S') : label.length());
        return Integer.parseInt(numStr);
    }
}
