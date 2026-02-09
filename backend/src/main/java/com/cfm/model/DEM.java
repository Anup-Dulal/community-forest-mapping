package com.cfm.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity representing a Digital Elevation Model (DEM) dataset.
 * Stores metadata about downloaded and processed DEM data.
 */
@Entity
@Table(name = "dems", indexes = {
    @Index(name = "idx_dems_shapefile_id", columnList = "shapefile_id"),
    @Index(name = "idx_dems_status", columnList = "status")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DEM {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "shapefile_id", nullable = false)
    private Shapefile shapefile;

    @Column(nullable = false, length = 50)
    private String source; // SRTM, OpenTopography, NASA

    @Column(name = "downloaded_at")
    private LocalDateTime downloadedAt;

    @Column(name = "raster_path", length = 500)
    private String rasterPath;

    @Column(name = "clipped_raster_path", length = 500)
    private String clippedRasterPath;

    @Column(length = 50)
    @Builder.Default
    private String status = "downloading"; // downloading, downloaded, clipping, clipped, error

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
