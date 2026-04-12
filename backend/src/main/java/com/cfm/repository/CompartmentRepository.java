package com.cfm.repository;

import com.cfm.model.Compartment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for Compartment entity.
 * Provides database access methods for compartment operations including hierarchical queries.
 */
@Repository
public interface CompartmentRepository extends JpaRepository<Compartment, UUID> {
    
    /**
     * Find all compartments for an analysis result (both parent and sub-compartments)
     */
    List<Compartment> findByAnalysisResultId(UUID analysisResultId);
    
    /**
     * Find compartments by analysis result and level
     * @param analysisResultId Analysis result UUID
     * @param level 0 for top-level compartments, 1 for sub-compartments
     */
    List<Compartment> findByAnalysisResultIdAndLevel(UUID analysisResultId, Integer level);
    
    /**
     * Find only top-level compartments (level = 0)
     */
    @Query("SELECT c FROM Compartment c WHERE c.analysisResult.id = :analysisResultId AND c.level = 0 ORDER BY c.subCompartmentNumber")
    List<Compartment> findTopLevelByAnalysisResultId(@Param("analysisResultId") UUID analysisResultId);
    
    /**
     * Find sub-compartments for a parent compartment
     */
    List<Compartment> findByParentCompartmentIdOrderBySubCompartmentNumber(UUID parentCompartmentId);
    
    /**
     * Find compartment by label
     */
    Optional<Compartment> findByAnalysisResultIdAndLabel(UUID analysisResultId, String label);
    
    /**
     * Count compartments by level
     */
    Long countByAnalysisResultIdAndLevel(UUID analysisResultId, Integer level);
    
    /**
     * Find all sub-compartments for an analysis result
     */
    @Query("SELECT c FROM Compartment c WHERE c.analysisResult.id = :analysisResultId AND c.level = 1 ORDER BY c.parentCompartment.subCompartmentNumber, c.subCompartmentNumber")
    List<Compartment> findAllSubCompartmentsByAnalysisResultId(@Param("analysisResultId") UUID analysisResultId);
}

