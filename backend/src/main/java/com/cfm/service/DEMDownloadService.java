package com.cfm.service;

import com.cfm.dto.DEMStatusResponse;
import com.cfm.model.DEM;
import com.cfm.model.Shapefile;
import com.cfm.repository.DEMRepository;
import com.cfm.repository.ShapefileRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service for orchestrating DEM download and processing.
 * Handles automatic DEM download from SRTM, OpenTopography, or NASA sources.
 * Requirement 3: Automatic DEM Download and Processing
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class DEMDownloadService {

    private final DEMRepository demRepository;
    private final ShapefileRepository shapefileRepository;
    private final RestTemplate restTemplate;

    @Value("${app.gis-service-url:http://localhost:8001}")
    private String gisServiceUrl;

    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY_MS = 5000;

    /**
     * Trigger DEM download for a shapefile.
     * Automatically downloads and clips DEM to boundary.
     *
     * @param shapefileId Shapefile UUID
     * @param source DEM source (SRTM, OpenTopography, NASA)
     * @return DEMStatusResponse with download status
     * @throws IllegalArgumentException if shapefile not found
     */
    public DEMStatusResponse downloadDEM(UUID shapefileId, String source) {
        log.info("Starting DEM download for shapefile: {}", shapefileId);

        try {
            // Get shapefile
            Shapefile shapefile = shapefileRepository.findById(shapefileId)
                .orElseThrow(() -> new IllegalArgumentException("Shapefile not found: " + shapefileId));

            // Check if DEM already exists
            var existingDEM = demRepository.findByShapefileId(shapefileId);
            if (existingDEM.isPresent() && "clipped".equals(existingDEM.get().getStatus())) {
                log.info("DEM already downloaded and clipped for shapefile: {}", shapefileId);
                return mapToResponse(existingDEM.get());
            }

            // Create or update DEM entity
            DEM dem = existingDEM.orElse(DEM.builder()
                .shapefile(shapefile)
                .source(source)
                .status("downloading")
                .build());

            dem.setStatus("downloading");
            DEM savedDEM = demRepository.save(dem);

            // Call GIS service to download DEM
            downloadDEMViaGIS(savedDEM.getId(), shapefile, source);

            return DEMStatusResponse.builder()
                .demId(savedDEM.getId())
                .source(source)
                .status("downloading")
                .progressPercentage(0)
                .message("DEM download started")
                .build();

        } catch (Exception e) {
            log.error("Error starting DEM download", e);
            throw new RuntimeException("Failed to start DEM download: " + e.getMessage());
        }
    }

    /**
     * Get DEM download status.
     *
     * @param demId DEM UUID
     * @return DEMStatusResponse with current status
     */
    public DEMStatusResponse getDEMStatus(UUID demId) {
        try {
            DEM dem = demRepository.findById(demId)
                .orElseThrow(() -> new IllegalArgumentException("DEM not found: " + demId));

            return mapToResponse(dem);
        } catch (Exception e) {
            log.error("Error retrieving DEM status", e);
            throw new RuntimeException("Failed to retrieve DEM status: " + e.getMessage());
        }
    }

    /**
     * Download DEM via GIS microservice with retry logic.
     * Handles download failures with automatic retry (up to 3 attempts).
     *
     * @param demId DEM UUID
     * @param shapefile Shapefile entity
     * @param source DEM source
     */
    private void downloadDEMViaGIS(UUID demId, Shapefile shapefile, String source) {
        new Thread(() -> {
            int retries = 0;
            while (retries < MAX_RETRIES) {
                try {
                    log.info("Attempting DEM download (attempt {}/{})", retries + 1, MAX_RETRIES);

                    // Prepare request
                    Map<String, Object> request = new HashMap<>();
                    request.put("demId", demId.toString());
                    request.put("source", source);
                    request.put("bbox", extractBoundingBox(shapefile));

                    // Call GIS service
                    String url = gisServiceUrl + "/api/dem/download";
                    var response = restTemplate.postForObject(url, request, Map.class);

                    if (response != null && "success".equals(response.get("status"))) {
                        // Update DEM entity
                        DEM dem = demRepository.findById(demId)
                            .orElseThrow();
                        dem.setStatus("downloaded");
                        dem.setDownloadedAt(LocalDateTime.now());
                        dem.setRasterPath((String) response.get("rasterPath"));
                        demRepository.save(dem);

                        log.info("DEM download successful for: {}", demId);
                        return;
                    }

                    retries++;
                    if (retries < MAX_RETRIES) {
                        log.warn("DEM download attempt {} failed, retrying...", retries);
                        Thread.sleep(RETRY_DELAY_MS);
                    }

                } catch (Exception e) {
                    log.error("Error during DEM download attempt {}", retries + 1, e);
                    retries++;
                    if (retries < MAX_RETRIES) {
                        try {
                            Thread.sleep(RETRY_DELAY_MS);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                }
            }

            // Mark as failed after all retries
            try {
                DEM dem = demRepository.findById(demId).orElseThrow();
                dem.setStatus("error");
                demRepository.save(dem);
                log.error("DEM download failed after {} attempts", MAX_RETRIES);
            } catch (Exception e) {
                log.error("Error updating DEM status to error", e);
            }
        }).start();
    }

    /**
     * Extract bounding box from shapefile.
     * Parses WKT geometry string to extract bounding box coordinates.
     *
     * @param shapefile Shapefile entity
     * @return Bounding box map with minLon, minLat, maxLon, maxLat
     */
    private Map<String, Double> extractBoundingBox(Shapefile shapefile) {
        Map<String, Double> bbox = new HashMap<>();
        
        if (shapefile.getGeometry() != null && !shapefile.getGeometry().isEmpty()) {
            try {
                // Parse WKT geometry string
                String wktGeometry = shapefile.getGeometry();
                
                // Extract coordinates from WKT format
                // WKT format: POLYGON ((lon lat, lon lat, ...))
                // or MULTIPOLYGON (((lon lat, lon lat, ...)))
                double minLon = Double.MAX_VALUE;
                double minLat = Double.MAX_VALUE;
                double maxLon = -Double.MAX_VALUE;
                double maxLat = -Double.MAX_VALUE;
                
                // Extract all coordinate pairs from WKT
                String coordPattern = "(-?\\d+\\.?\\d*) (-?\\d+\\.?\\d*)";
                java.util.regex.Pattern pattern = java.util.regex.Pattern.compile(coordPattern);
                java.util.regex.Matcher matcher = pattern.matcher(wktGeometry);
                
                while (matcher.find()) {
                    double lon = Double.parseDouble(matcher.group(1));
                    double lat = Double.parseDouble(matcher.group(2));
                    
                    minLon = Math.min(minLon, lon);
                    minLat = Math.min(minLat, lat);
                    maxLon = Math.max(maxLon, lon);
                    maxLat = Math.max(maxLat, lat);
                }
                
                if (minLon != Double.MAX_VALUE) {
                    bbox.put("minLon", minLon);
                    bbox.put("minLat", minLat);
                    bbox.put("maxLon", maxLon);
                    bbox.put("maxLat", maxLat);
                    log.debug("Extracted bounding box from WKT: minLon={}, minLat={}, maxLon={}, maxLat={}", 
                        minLon, minLat, maxLon, maxLat);
                }
            } catch (Exception e) {
                log.error("Error parsing WKT geometry: {}", e.getMessage(), e);
            }
        }
        
        return bbox;
    }

    /**
     * Map DEM entity to response DTO.
     *
     * @param dem DEM entity
     * @return DEMStatusResponse
     */
    private DEMStatusResponse mapToResponse(DEM dem) {
        return DEMStatusResponse.builder()
            .demId(dem.getId())
            .source(dem.getSource())
            .status(dem.getStatus())
            .downloadedAt(dem.getDownloadedAt())
            .message("DEM status: " + dem.getStatus())
            .progressPercentage(calculateProgress(dem.getStatus()))
            .build();
    }

    /**
     * Calculate progress percentage based on status.
     *
     * @param status DEM status
     * @return Progress percentage
     */
    private Integer calculateProgress(String status) {
        return switch (status) {
            case "downloading" -> 25;
            case "downloaded" -> 50;
            case "clipping" -> 75;
            case "clipped" -> 100;
            case "error" -> 0;
            default -> 0;
        };
    }
}
