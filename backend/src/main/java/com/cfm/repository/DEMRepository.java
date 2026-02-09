package com.cfm.repository;

import com.cfm.model.DEM;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for DEM entity.
 * Provides database access methods for DEM operations.
 */
@Repository
public interface DEMRepository extends JpaRepository<DEM, UUID> {
    Optional<DEM> findByShapefileId(UUID shapefileId);
    List<DEM> findByStatus(String status);
}
