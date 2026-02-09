package com.cfm.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity representing analysis results including slope, aspect, compartments, and sample plots.
 * Stores paths to generated raster and vector data.
 */
@Entity
@Table(name = "analysis_results", indexes = {
    @Index(name = "idx_analysis_results_shapefile_id", columnList = "shapefile_id"),
    @Index(name = "idx_analysis_results_dem_id", columnList = "dem_id"),
    @Index(name = "idx_analysis_results_status", columnList = "status")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AnalysisResult {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "shapefile_id", nullable = false)
    private Shapefile shapefile;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "dem_id")
    private DEM dem;

    @Column(name = "slope_raster_path", length = 500)
    private String slopeRasterPath;

    @Column(name = "aspect_raster_path", length = 500)
    private String aspectRasterPath;

    @Column(name = "compartment_geometry_path", length = 500)
    private String compartmentGeometryPath;

    @Column(name = "sample_plot_geometry_path", length = 500)
    private String samplePlotGeometryPath;

    @Column(name = "generated_at")
    private LocalDateTime generatedAt;

    @Column(length = 50)
    @Builder.Default
    private String status = "pending"; // pending, processing, complete, error

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
