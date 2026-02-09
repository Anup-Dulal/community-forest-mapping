package com.cfm.service;

import com.cfm.model.AnalysisResult;
import com.cfm.model.Compartment;
import com.cfm.model.DEM;
import com.cfm.model.Shapefile;
import com.cfm.repository.AnalysisResultRepository;
import com.cfm.repository.CompartmentRepository;
import com.cfm.repository.DEMRepository;
import com.cfm.repository.ShapefileRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * Service for managing user sessions and data persistence.
 * Handles session state management, data retrieval, and persistence operations.
 */
@Slf4j
@Service
public class SessionService {

    @Autowired
    private ShapefileRepository shapefileRepository;

    @Autowired
    private DEMRepository demRepository;

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private CompartmentRepository compartmentRepository;

    /**
     * Create a new session with initial state.
     *
     * @return Session ID
     */
    public String createSession() {
        String sessionId = UUID.randomUUID().toString();
        log.info("Session created: {}", sessionId);
        return sessionId;
    }

    /**
     * Get session data including all analysis results and related data.
     *
     * @param sessionId Session ID
     * @return Map with session data
     */
    public Map<String, Object> getSessionData(String sessionId) {
        try {
            Map<String, Object> sessionData = new HashMap<>();
            sessionData.put("sessionId", sessionId);
            sessionData.put("createdAt", System.currentTimeMillis());

            // Get all shapefiles
            List<Shapefile> shapefiles = shapefileRepository.findAll();
            sessionData.put("shapefiles", shapefiles);

            // Get all DEMs
            List<DEM> dems = demRepository.findAll();
            sessionData.put("dems", dems);

            // Get all analysis results
            List<AnalysisResult> analysisResults = analysisResultRepository.findAll();
            sessionData.put("analysisResults", analysisResults);

            // Get all compartments
            List<Compartment> compartments = compartmentRepository.findAll();
            sessionData.put("compartments", compartments);

            log.info("Session data retrieved for session: {}", sessionId);
            return sessionData;

        } catch (Exception e) {
            log.error("Error retrieving session data: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve session data: " + e.getMessage(), e);
        }
    }

    /**
     * Get analysis results for a session.
     *
     * @param sessionId Session ID
     * @return List of analysis results
     */
    public List<AnalysisResult> getAnalysisResults(String sessionId) {
        try {
            List<AnalysisResult> results = analysisResultRepository.findAll();
            log.info("Retrieved {} analysis results for session: {}", results.size(), sessionId);
            return results;

        } catch (Exception e) {
            log.error("Error retrieving analysis results: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve analysis results: " + e.getMessage(), e);
        }
    }

    /**
     * Get a specific analysis result by ID.
     *
     * @param analysisResultId Analysis result ID
     * @return Analysis result
     * @throws IllegalArgumentException if not found
     */
    public AnalysisResult getAnalysisResult(UUID analysisResultId) {
        try {
            return analysisResultRepository.findById(analysisResultId)
                    .orElseThrow(() -> new IllegalArgumentException("Analysis result not found: " + analysisResultId));

        } catch (IllegalArgumentException e) {
            log.error("Analysis result not found: {}", analysisResultId);
            throw e;
        } catch (Exception e) {
            log.error("Error retrieving analysis result: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve analysis result: " + e.getMessage(), e);
        }
    }

    /**
     * Get all shapefiles in the session.
     *
     * @param sessionId Session ID
     * @return List of shapefiles
     */
    public List<Shapefile> getShapefiles(String sessionId) {
        try {
            List<Shapefile> shapefiles = shapefileRepository.findAll();
            log.info("Retrieved {} shapefiles for session: {}", shapefiles.size(), sessionId);
            return shapefiles;

        } catch (Exception e) {
            log.error("Error retrieving shapefiles: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve shapefiles: " + e.getMessage(), e);
        }
    }

    /**
     * Get a specific shapefile by ID.
     *
     * @param shapefileId Shapefile ID
     * @return Shapefile
     * @throws IllegalArgumentException if not found
     */
    public Shapefile getShapefile(UUID shapefileId) {
        try {
            return shapefileRepository.findById(shapefileId)
                    .orElseThrow(() -> new IllegalArgumentException("Shapefile not found: " + shapefileId));

        } catch (IllegalArgumentException e) {
            log.error("Shapefile not found: {}", shapefileId);
            throw e;
        } catch (Exception e) {
            log.error("Error retrieving shapefile: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve shapefile: " + e.getMessage(), e);
        }
    }

    /**
     * Get all DEMs in the session.
     *
     * @param sessionId Session ID
     * @return List of DEMs
     */
    public List<DEM> getDEMs(String sessionId) {
        try {
            List<DEM> dems = demRepository.findAll();
            log.info("Retrieved {} DEMs for session: {}", dems.size(), sessionId);
            return dems;

        } catch (Exception e) {
            log.error("Error retrieving DEMs: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve DEMs: " + e.getMessage(), e);
        }
    }

    /**
     * Get a specific DEM by ID.
     *
     * @param demId DEM ID
     * @return DEM
     * @throws IllegalArgumentException if not found
     */
    public DEM getDEM(UUID demId) {
        try {
            return demRepository.findById(demId)
                    .orElseThrow(() -> new IllegalArgumentException("DEM not found: " + demId));

        } catch (IllegalArgumentException e) {
            log.error("DEM not found: {}", demId);
            throw e;
        } catch (Exception e) {
            log.error("Error retrieving DEM: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve DEM: " + e.getMessage(), e);
        }
    }

    /**
     * Get all compartments for an analysis result.
     *
     * @param analysisResultId Analysis result ID
     * @return List of compartments
     */
    public List<Compartment> getCompartments(UUID analysisResultId) {
        try {
            List<Compartment> compartments = compartmentRepository.findByAnalysisResultId(analysisResultId);
            log.info("Retrieved {} compartments for analysis: {}", compartments.size(), analysisResultId);
            return compartments;

        } catch (Exception e) {
            log.error("Error retrieving compartments: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to retrieve compartments: " + e.getMessage(), e);
        }
    }

    /**
     * Validate data persistence by storing and retrieving data.
     *
     * @param analysisResultId Analysis result ID
     * @return Validation result
     */
    public Map<String, Object> validateDataPersistence(UUID analysisResultId) {
        try {
            Map<String, Object> validation = new HashMap<>();

            // Retrieve analysis result
            AnalysisResult analysisResult = getAnalysisResult(analysisResultId);
            validation.put("analysisResultFound", analysisResult != null);

            // Retrieve shapefile
            if (analysisResult.getShapefile() != null) {
                Shapefile shapefile = getShapefile(analysisResult.getShapefile().getId());
                validation.put("shapefileFound", shapefile != null);
                validation.put("shapefileDataIntegrity", shapefile.getId().equals(analysisResult.getShapefile().getId()));
            }

            // Retrieve DEM
            if (analysisResult.getDem() != null) {
                DEM dem = getDEM(analysisResult.getDem().getId());
                validation.put("demFound", dem != null);
                validation.put("demDataIntegrity", dem.getId().equals(analysisResult.getDem().getId()));
            }

            // Retrieve compartments
            List<Compartment> compartments = getCompartments(analysisResultId);
            validation.put("compartmentsFound", !compartments.isEmpty());
            validation.put("compartmentCount", compartments.size());

            // Overall validation
            boolean allValid = (boolean) validation.getOrDefault("analysisResultFound", false) &&
                    (boolean) validation.getOrDefault("shapefileDataIntegrity", true) &&
                    (boolean) validation.getOrDefault("demDataIntegrity", true);

            validation.put("isValid", allValid);

            log.info("Data persistence validation completed for analysis: {}", analysisResultId);
            return validation;

        } catch (Exception e) {
            log.error("Error validating data persistence: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to validate data persistence: " + e.getMessage(), e);
        }
    }

    /**
     * Clear session data (delete all analysis results and related data).
     *
     * @param sessionId Session ID
     */
    public void clearSession(String sessionId) {
        try {
            // Delete all analysis results (cascade delete will handle related data)
            analysisResultRepository.deleteAll();

            // Delete all DEMs
            demRepository.deleteAll();

            // Delete all shapefiles
            shapefileRepository.deleteAll();

            log.info("Session cleared: {}", sessionId);

        } catch (Exception e) {
            log.error("Error clearing session: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to clear session: " + e.getMessage(), e);
        }
    }
}
