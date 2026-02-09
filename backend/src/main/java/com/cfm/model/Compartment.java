package com.cfm.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity representing a compartment (equal-area subdivision) of the forest boundary.
 * Stores geometry and metadata for each compartment.
 * Geometry is stored as WKT (Well-Known Text) format for SQLite compatibility.
 */
@Entity
@Table(name = "compartments", indexes = {
    @Index(name = "idx_compartments_analysis_result_id", columnList = "analysis_result_id"),
    @Index(name = "idx_compartments_compartment_id", columnList = "compartment_id")
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
    private String compartmentId; // C1, C2, C3, etc.

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
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
