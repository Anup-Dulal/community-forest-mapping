package com.cfm.repository;

import com.cfm.model.AnalysisResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for AnalysisResult entity.
 * Provides database access methods for analysis result operations.
 */
@Repository
public interface AnalysisResultRepository extends JpaRepository<AnalysisResult, UUID> {
    Optional<AnalysisResult> findByShapefileId(UUID shapefileId);
    List<AnalysisResult> findByStatus(String status);
}
