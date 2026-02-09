package com.cfm.repository;

import com.cfm.model.SamplePlot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

/**
 * Repository for SamplePlot entity.
 * Provides database access methods for sample plot operations.
 */
@Repository
public interface SamplePlotRepository extends JpaRepository<SamplePlot, UUID> {
    List<SamplePlot> findByAnalysisResultId(UUID analysisResultId);
    List<SamplePlot> findByCompartmentId(UUID compartmentId);
}
