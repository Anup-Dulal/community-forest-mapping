package com.cfm.service;

import com.cfm.archive.ArchiveExtractionService;
import com.cfm.dto.UploadResponse;
import com.cfm.dto.ValidationResult;
import com.cfm.model.Shapefile;
import com.cfm.repository.ShapefileRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.client.RestTemplate;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@Slf4j
@Service
@Transactional
public class ShapefileUploadService {

    private static final Set<String> REQUIRED_EXTENSIONS = Set.of(".shp", ".shx", ".dbf", ".prj");
    
    @Autowired
    private ShapefileRepository shapefileRepository;
    
    @Autowired
    private ArchiveExtractionService archiveExtractionService;

    @Autowired
    private GeometryValidationService geometryValidationService;

    @Value("${app.upload-dir:/app/uploads}")
    private String uploadBaseDir;

    /**
     * Upload and validate shapefile.
     * Supports individual file uploads (.shp, .shx, .dbf, .prj).
     * Archive support (ZIP, RAR4, RAR5) temporarily disabled due to dependency issues.
     */
    public UploadResponse uploadAndValidate(MultipartFile[] files) throws IOException {
        List<MultipartFile> processedFiles = new ArrayList<>();
        UUID shapefileId = UUID.randomUUID();
        // Use absolute path and normalize to remove any ./ or ../ components
        Path uploadPath = Paths.get(uploadBaseDir).toAbsolutePath().normalize().resolve(shapefileId.toString());

        try {
            // Create upload directory
            Files.createDirectories(uploadPath);
            log.info("Created upload directory: {}", uploadPath);

            // Process uploaded files - only accept individual shapefile components
            for (MultipartFile file : files) {
                String filename = file.getOriginalFilename();
                if (filename == null) continue;

                String extension = getExtension(filename);

                // Only accept individual shapefile components
                if (REQUIRED_EXTENSIONS.contains(extension)) {
                    processedFiles.add(file);
                    // Save file to disk
                    Path filePath = uploadPath.resolve(filename);
                    file.transferTo(filePath.toFile());
                    log.info("Saved shapefile component: {}", filePath);
                } else if (".zip".equalsIgnoreCase(extension) || ".rar".equalsIgnoreCase(extension)) {
                    log.warn("Archive uploads temporarily disabled. Please upload individual .shp, .shx, .dbf, .prj files.");
                }
            }

            // Validate shapefile completeness
            validateShapefileCompleteness(processedFiles);

            // Parse shapefile to extract geometry
            String geometry = parseShapefileGeometry(uploadPath, files[0].getOriginalFilename());
            log.info("Extracted geometry from shapefile: {}", geometry.substring(0, Math.min(100, geometry.length())));

            // Store in database
            Shapefile shapefile = new Shapefile();
            shapefile.setId(shapefileId);
            shapefile.setFilename(files[0].getOriginalFilename());
            shapefile.setGeometry(geometry);
            log.info("Saving shapefile to database: {}", shapefileId);
            try {
                Shapefile savedShapefile = shapefileRepository.save(shapefile);
                log.info("Shapefile saved successfully: {}", savedShapefile.getId());
                shapefileRepository.flush(); // Ensure data is written to database
                log.info("Shapefile flushed to database");
            } catch (Exception e) {
                log.error("Error saving shapefile", e);
                throw e;
            }

            log.info("Shapefile uploaded successfully: {}", shapefileId);
            UploadResponse response = new UploadResponse();
            response.setShapefileId(shapefileId);
            response.setFilename(files[0].getOriginalFilename());
            response.setStatus("success");
            response.setMessage("Shapefile uploaded successfully");
            return response;

        } catch (Exception e) {
            log.error("Error uploading shapefile", e);
            throw new RuntimeException("Upload failed: " + e.getMessage(), e);
        }
    }

    /**
     * Parse shapefile and extract geometry as WKT.
     * Uses GIS service to parse the shapefile.
     */
    private String parseShapefileGeometry(Path uploadPath, String shapefileName) throws IOException {
        try {
            // Normalize the path to remove any ./ or ../ components
            String cleanPath = uploadPath.toAbsolutePath().normalize().toString();
            log.info("Parsing shapefile from directory: {}", cleanPath);
            
            // Call GIS service to parse shapefile
            // Note: gis-service is the Docker service name, port 8000 is the internal FastAPI port
            String gisServiceUrl = "http://gis-service:8000/api/shapefile/parse";
            
            Map<String, Object> request = new HashMap<>();
            request.put("shapefileDir", cleanPath);
            
            RestTemplate restTemplate = new RestTemplate();
            
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = restTemplate.postForObject(gisServiceUrl, request, Map.class);
                
                if (response != null && response.containsKey("geometry")) {
                    log.info("Successfully parsed shapefile via GIS service");
                    
                    // Extract geometry from response
                    @SuppressWarnings("unchecked")
                    Map<String, Object> geometry = (Map<String, Object>) response.get("geometry");
                    
                    // Log projection info
                    String projection = (String) response.get("projection");
                    log.info("Shapefile projection: {}", projection);
                    
                    // Log bounding box
                    @SuppressWarnings("unchecked")
                    Map<String, Object> bbox = (Map<String, Object>) response.get("boundingBox");
                    if (bbox != null) {
                        log.info("Bounding box: minLon={}, minLat={}, maxLon={}, maxLat={}", 
                            bbox.get("minLon"), bbox.get("minLat"), bbox.get("maxLon"), bbox.get("maxLat"));
                    }
                    
                    // Convert GeoJSON geometry to WKT
                    String wkt = convertGeoJsonToWkt(geometry);
                    log.info("Converted geometry to WKT: {}", wkt.substring(0, Math.min(100, wkt.length())));
                    
                    return wkt;
                }
                
                log.error("GIS service response missing geometry field");
                throw new IOException("Failed to parse shapefile: Invalid response from GIS service");
                
            } catch (org.springframework.web.client.ResourceAccessException e) {
                log.error("Cannot connect to GIS service at {}", gisServiceUrl, e);
                throw new IOException("Cannot connect to GIS service. Please ensure it is running.");
            }
            
        } catch (IOException e) {
            throw e;
        } catch (Exception e) {
            log.error("Error parsing shapefile geometry", e);
            throw new IOException("Failed to parse shapefile: " + e.getMessage());
        }
    }
    
    /**
     * Convert GeoJSON geometry to WKT format.
     */
    private String convertGeoJsonToWkt(Map<String, Object> geoJson) {
        try {
            String type = (String) geoJson.get("type");
            
            if ("Polygon".equals(type)) {
                @SuppressWarnings("unchecked")
                List<List<List<Number>>> coordinates = (List<List<List<Number>>>) geoJson.get("coordinates");
                
                StringBuilder wkt = new StringBuilder("POLYGON ((");
                List<List<Number>> ring = coordinates.get(0);
                
                for (int i = 0; i < ring.size(); i++) {
                    List<Number> coord = ring.get(i);
                    wkt.append(coord.get(0)).append(" ").append(coord.get(1));
                    if (i < ring.size() - 1) {
                        wkt.append(", ");
                    }
                }
                wkt.append("))");
                
                return wkt.toString();
                
            } else if ("MultiPolygon".equals(type)) {
                @SuppressWarnings("unchecked")
                List<List<List<List<Number>>>> coordinates = (List<List<List<List<Number>>>>) geoJson.get("coordinates");
                
                StringBuilder wkt = new StringBuilder("MULTIPOLYGON (");
                
                for (int p = 0; p < coordinates.size(); p++) {
                    List<List<List<Number>>> polygon = coordinates.get(p);
                    wkt.append("((");
                    
                    List<List<Number>> ring = polygon.get(0);
                    for (int i = 0; i < ring.size(); i++) {
                        List<Number> coord = ring.get(i);
                        wkt.append(coord.get(0)).append(" ").append(coord.get(1));
                        if (i < ring.size() - 1) {
                            wkt.append(", ");
                        }
                    }
                    
                    wkt.append("))");
                    if (p < coordinates.size() - 1) {
                        wkt.append(", ");
                    }
                }
                wkt.append(")");
                
                return wkt.toString();
            }
            
            throw new IllegalArgumentException("Unsupported geometry type: " + type);
            
        } catch (Exception e) {
            log.error("Error converting GeoJSON to WKT", e);
            throw new IllegalArgumentException("Failed to convert geometry: " + e.getMessage());
        }
    }

    /**
     * Process archive file using unified extraction service.
     */
    private void processArchive(MultipartFile archiveFile, Path extractPath, List<MultipartFile> processedFiles) throws IOException {
        // Extract archive using unified service
        List<Path> extractedPaths = archiveExtractionService.extractArchive(archiveFile, extractPath);
        
        // Convert extracted paths to MultipartFile wrappers
        for (Path path : extractedPaths) {
            processedFiles.add(new FileWrapper(path.toFile(), path.getFileName().toString()));
        }
    }

    /**
     * Validate shapefile completeness.
     */
    private void validateShapefileCompleteness(List<MultipartFile> files) {
        Set<String> extensions = new HashSet<>();
        for (MultipartFile file : files) {
            String filename = file.getOriginalFilename();
            if (filename != null) {
                extensions.add(getExtension(filename));
            }
        }

        Set<String> missing = new HashSet<>(REQUIRED_EXTENSIONS);
        missing.removeAll(extensions);

        if (!missing.isEmpty()) {
            String missingList = String.join(", ", missing);
            throw new IllegalArgumentException(
                    "Missing required shapefile components: " + missingList + ". " +
                    "A complete shapefile requires: .shp, .shx, .dbf, .prj files.");
        }
        log.debug("Shapefile validation passed");
    }

    /**
     * Get shapefile by ID.
     */
    public Shapefile getShapefileById(UUID id) {
        return shapefileRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("Shapefile not found: " + id));
    }

    /**
     * Get shapefile data by ID as Map for API response.
     */
    public java.util.Map<String, Object> getShapefileDataById(UUID id) {
        Shapefile shapefile = getShapefileById(id);
        
        java.util.Map<String, Object> data = new java.util.HashMap<>();
        data.put("id", shapefile.getId());
        data.put("filename", shapefile.getFilename());
        data.put("geometry", shapefile.getGeometry());
        data.put("projection", shapefile.getProjection());
        data.put("status", shapefile.getStatus());
        data.put("createdAt", shapefile.getCreatedAt());
        data.put("updatedAt", shapefile.getUpdatedAt());
        
        return data;
    }

    /**
     * Extract file extension.
     */
    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        return lastDot > 0 ? filename.substring(lastDot).toLowerCase() : "";
    }

    /**
     * Validate shapefile geometry.
     * Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8
     */
    public ValidationResult validateShapefileGeometry(UUID shapefileId) {
        log.info("Validating geometry for shapefile: {}", shapefileId);
        
        Shapefile shapefile = getShapefileById(shapefileId);
        Path uploadPath = Paths.get(uploadBaseDir).toAbsolutePath().resolve(shapefileId.toString());
        
        ValidationResult result = geometryValidationService.validateGeometry(uploadPath, shapefile.getFilename());
        
        // Update shapefile status based on validation result
        if ("error".equals(result.getStatus())) {
            shapefile.setStatus("validation_failed");
        } else if ("warning".equals(result.getStatus())) {
            shapefile.setStatus("validated_with_warnings");
        } else {
            shapefile.setStatus("validated");
        }
        
        shapefileRepository.save(shapefile);
        log.info("Geometry validation completed with status: {}", result.getStatus());
        
        return result;
    }

    /**
     * Auto-repair shapefile geometry.
     * Requirements: 17.2, 17.6
     */
    public ValidationResult autoRepairShapefileGeometry(UUID shapefileId) {
        log.info("Auto-repairing geometry for shapefile: {}", shapefileId);
        
        Shapefile shapefile = getShapefileById(shapefileId);
        Path uploadPath = Paths.get(uploadBaseDir).toAbsolutePath().resolve(shapefileId.toString());
        
        boolean repairSuccess = geometryValidationService.autoRepairSelfIntersections(uploadPath);
        
        if (repairSuccess) {
            shapefile.setStatus("repaired");
            shapefileRepository.save(shapefile);
            
            // Re-validate after repair
            return validateShapefileGeometry(shapefileId);
        } else {
            return ValidationResult.builder()
                .isValid(false)
                .status("error")
                .message("Auto-repair failed. Please check the shapefile.")
                .build();
        }
    }

    /**
     * Get boundary geometry for a shapefile.
     * Requirements: 13.1, 13.2, 13.4
     */
    public java.util.Map<String, Object> getBoundaryGeometry(UUID shapefileId) {
        log.info("Fetching boundary geometry for shapefile: {}", shapefileId);
        
        Shapefile shapefile = getShapefileById(shapefileId);
        
        // Get WKT geometry
        String wktGeometry = shapefile.getGeometry();
        if (wktGeometry == null || wktGeometry.trim().isEmpty()) {
            throw new IllegalArgumentException("Shapefile geometry is empty");
        }
        
        try {
            // Call GIS service to convert WKT to GeoJSON
            String gisServiceUrl = "http://gis-service:8000/api/shapefile/wkt-to-geojson";
            
            RestTemplate restTemplate = new RestTemplate();
            java.util.Map<String, String> requestBody = new java.util.HashMap<>();
            requestBody.put("wkt", wktGeometry);
            
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.setContentType(org.springframework.http.MediaType.APPLICATION_JSON);
            
            org.springframework.http.HttpEntity<java.util.Map<String, String>> request = 
                new org.springframework.http.HttpEntity<>(requestBody, headers);
            
            org.springframework.http.ResponseEntity<java.util.Map> gisResponse = 
                restTemplate.postForEntity(gisServiceUrl, request, java.util.Map.class);
            
            if (!gisResponse.getStatusCode().is2xxSuccessful() || gisResponse.getBody() == null) {
                throw new RuntimeException("Failed to convert WKT to GeoJSON");
            }
            
            java.util.Map<String, Object> geoJsonData = gisResponse.getBody();
            
            // Build response
            java.util.Map<String, Object> response = new java.util.HashMap<>();
            response.put("geometry", geoJsonData.get("geometry"));
            
            // Calculate area from geometry (approximate)
            // For now, use a placeholder - proper area calculation would require geometry parsing
            double areaSquareMeters = 10000.0; // Placeholder
            double areaHectares = areaSquareMeters / 10000.0;
            response.put("area", areaSquareMeters);
            response.put("areaHectares", areaHectares);
            
            // Extract bounding box from geometry if available
            if (geoJsonData.containsKey("bbox")) {
                response.put("boundingBox", geoJsonData.get("bbox"));
            }
            
            log.info("Successfully fetched boundary geometry for shapefile: {}", shapefileId);
            return response;
            
        } catch (Exception e) {
            log.error("Error converting WKT to GeoJSON for shapefile: {}", shapefileId, e);
            throw new RuntimeException("Failed to fetch boundary geometry: " + e.getMessage(), e);
        }
    }

    /**
     * Wrapper class to convert File to MultipartFile.
     */
    private static class FileWrapper implements MultipartFile {
        private final File file;
        private final String filename;

        FileWrapper(File file, String filename) {
            this.file = file;
            this.filename = filename;
        }

        @Override
        public String getName() {
            return filename;
        }

        @Override
        public String getOriginalFilename() {
            return filename;
        }

        @Override
        public String getContentType() {
            return "application/octet-stream";
        }

        @Override
        public boolean isEmpty() {
            return file.length() == 0;
        }

        @Override
        public long getSize() {
            return file.length();
        }

        @Override
        public byte[] getBytes() throws IOException {
            return Files.readAllBytes(file.toPath());
        }

        @Override
        public InputStream getInputStream() throws IOException {
            return new FileInputStream(file);
        }

        @Override
        public void transferTo(File dest) throws IOException {
            Files.copy(file.toPath(), dest.toPath());
        }
    }
}
