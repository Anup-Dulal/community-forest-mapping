package com.cfm.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entity representing an uploaded shapefile with boundary geometry.
 * Stores metadata and geometry information for community forest boundaries.
 * Geometry is stored as WKT (Well-Known Text) format for SQLite compatibility.
 */
@Entity
@Table(name = "shapefiles", indexes = {
    @Index(name = "idx_shapefiles_user_id", columnList = "user_id"),
    @Index(name = "idx_shapefiles_status", columnList = "status")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Shapefile {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "user_id")
    private UUID userId;

    @Column(nullable = false)
    private String filename;

    @Column(name = "uploaded_at")
    private LocalDateTime uploadedAt;

    @Column(columnDefinition = "TEXT")
    private String geometry; // WKT format

    @Column(columnDefinition = "TEXT")
    private String boundingBox; // WKT format

    @Column(length = 50)
    private String projection;

    @Column(length = 50)
    @Builder.Default
    private String status = "uploaded";

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        uploadedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
