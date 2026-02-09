package com.cfm.repository;

import com.cfm.model.Shapefile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

/**
 * Repository for Shapefile entity.
 * Provides database access methods for shapefile operations.
 */
@Repository
public interface ShapefileRepository extends JpaRepository<Shapefile, UUID> {
    List<Shapefile> findByUserId(UUID userId);
    List<Shapefile> findByStatus(String status);
}
