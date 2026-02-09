package com.cfm.service;

import com.cfm.model.AnalysisResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Cache manager for analysis results.
 * Caches slope, aspect, compartment, and sample plot data.
 */
@Service
@Slf4j
public class AnalysisResultCacheManager {

    private static final long ANALYSIS_RESULT_TTL_MINUTES = 120; // 2 hours
    private static final long RASTER_DATA_TTL_MINUTES = 240; // 4 hours

    @Autowired
    private CacheService cacheService;

    /**
     * Cache an analysis result.
     */
    public void cacheAnalysisResult(AnalysisResult result) {
        String key = buildAnalysisResultKey(result.getId());
        cacheService.put(key, result, ANALYSIS_RESULT_TTL_MINUTES);
        log.debug("Cached analysis result: {}", result.getId());
    }

    /**
     * Get a cached analysis result.
     */
    public AnalysisResult getCachedAnalysisResult(UUID analysisResultId) {
        String key = buildAnalysisResultKey(analysisResultId);
        AnalysisResult result = cacheService.get(key, AnalysisResult.class);
        
        if (result != null) {
            log.debug("Retrieved cached analysis result: {}", analysisResultId);
        }
        
        return result;
    }

    /**
     * Cache slope raster data.
     */
    public void cacheSlopeRaster(UUID analysisResultId, String rasterPath) {
        String key = buildSlopeRasterKey(analysisResultId);
        cacheService.put(key, rasterPath, RASTER_DATA_TTL_MINUTES);
        log.debug("Cached slope raster for analysis: {}", analysisResultId);
    }

    /**
     * Get cached slope raster data.
     */
    public String getCachedSlopeRaster(UUID analysisResultId) {
        String key = buildSlopeRasterKey(analysisResultId);
        return cacheService.get(key, String.class);
    }

    /**
     * Cache aspect raster data.
     */
    public void cacheAspectRaster(UUID analysisResultId, String rasterPath) {
        String key = buildAspectRasterKey(analysisResultId);
        cacheService.put(key, rasterPath, RASTER_DATA_TTL_MINUTES);
        log.debug("Cached aspect raster for analysis: {}", analysisResultId);
    }

    /**
     * Get cached aspect raster data.
     */
    public String getCachedAspectRaster(UUID analysisResultId) {
        String key = buildAspectRasterKey(analysisResultId);
        return cacheService.get(key, String.class);
    }

    /**
     * Cache compartment geometry data.
     */
    public void cacheCompartmentGeometry(UUID analysisResultId, String geometryPath) {
        String key = buildCompartmentGeometryKey(analysisResultId);
        cacheService.put(key, geometryPath, RASTER_DATA_TTL_MINUTES);
        log.debug("Cached compartment geometry for analysis: {}", analysisResultId);
    }

    /**
     * Get cached compartment geometry data.
     */
    public String getCachedCompartmentGeometry(UUID analysisResultId) {
        String key = buildCompartmentGeometryKey(analysisResultId);
        return cacheService.get(key, String.class);
    }

    /**
     * Cache sample plot geometry data.
     */
    public void cacheSamplePlotGeometry(UUID analysisResultId, String geometryPath) {
        String key = buildSamplePlotGeometryKey(analysisResultId);
        cacheService.put(key, geometryPath, RASTER_DATA_TTL_MINUTES);
        log.debug("Cached sample plot geometry for analysis: {}", analysisResultId);
    }

    /**
     * Get cached sample plot geometry data.
     */
    public String getCachedSamplePlotGeometry(UUID analysisResultId) {
        String key = buildSamplePlotGeometryKey(analysisResultId);
        return cacheService.get(key, String.class);
    }

    /**
     * Invalidate all cache entries for an analysis result.
     */
    public void invalidateAnalysisResultCache(UUID analysisResultId) {
        cacheService.remove(buildAnalysisResultKey(analysisResultId));
        cacheService.remove(buildSlopeRasterKey(analysisResultId));
        cacheService.remove(buildAspectRasterKey(analysisResultId));
        cacheService.remove(buildCompartmentGeometryKey(analysisResultId));
        cacheService.remove(buildSamplePlotGeometryKey(analysisResultId));
        log.debug("Invalidated cache for analysis result: {}", analysisResultId);
    }

    /**
     * Get cache statistics.
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("cacheService", cacheService.getStats());
        stats.put("analysisResultTTLMinutes", ANALYSIS_RESULT_TTL_MINUTES);
        stats.put("rasterDataTTLMinutes", RASTER_DATA_TTL_MINUTES);
        return stats;
    }

    // Key building methods

    private String buildAnalysisResultKey(UUID analysisResultId) {
        return "analysis_result:" + analysisResultId;
    }

    private String buildSlopeRasterKey(UUID analysisResultId) {
        return "slope_raster:" + analysisResultId;
    }

    private String buildAspectRasterKey(UUID analysisResultId) {
        return "aspect_raster:" + analysisResultId;
    }

    private String buildCompartmentGeometryKey(UUID analysisResultId) {
        return "compartment_geometry:" + analysisResultId;
    }

    private String buildSamplePlotGeometryKey(UUID analysisResultId) {
        return "sample_plot_geometry:" + analysisResultId;
    }
}
