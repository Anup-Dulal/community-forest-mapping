package com.cfm.model;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity representing a sample plot point for forest inventory.
 * Stores coordinates in both lat/lon and UTM/UPS systems.
 * Geometry is stored as WKT (Well-Known Text) format for SQLite compatibility.
 */
@Entity
@Table(name = "sample_plots", indexes = {
    @Index(name = "idx_sample_plots_analysis_result_id", columnList = "analysis_result_id"),
    @Index(name = "idx_sample_plots_compartment_id", columnList = "compartment_id"),
    @Index(name = "idx_sample_plots_plot_id", columnList = "plot_id")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SamplePlot {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "analysis_result_id", nullable = false)
    private AnalysisResult analysisResult;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "compartment_id", nullable = false)
    private Compartment compartment;

    @Column(nullable = false, length = 50)
    private String plotId; // SP-01, SP-02, etc.

    @Column(precision = 15, scale = 2)
    private BigDecimal easting;

    @Column(precision = 15, scale = 2)
    private BigDecimal northing;

    @Column(precision = 10, scale = 6)
    private BigDecimal latitude;

    @Column(precision = 10, scale = 6)
    private BigDecimal longitude;

    @Column(columnDefinition = "TEXT")
    private String geometry; // WKT format

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
