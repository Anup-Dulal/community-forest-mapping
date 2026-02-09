package com.cfm.repository;

import com.cfm.model.Compartment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

/**
 * Repository for Compartment entity.
 * Provides database access methods for compartment operations.
 */
@Repository
public interface CompartmentRepository extends JpaRepository<Compartment, UUID> {
    List<Compartment> findByAnalysisResultId(UUID analysisResultId);
}
