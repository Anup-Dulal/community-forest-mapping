package com.cfm.service;

import com.cfm.archive.ArchiveExtractionService;
import com.cfm.dto.UploadResponse;
import com.cfm.model.Shapefile;
import com.cfm.repository.ShapefileRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@Slf4j
@Service
public class ShapefileUploadService {

    private static final Set<String> REQUIRED_EXTENSIONS = Set.of(".shp", ".shx", ".dbf", ".prj");
    private static final String UPLOAD_DIR = "uploads";

    @Autowired
    private ShapefileRepository shapefileRepository;
    
    @Autowired
    private ArchiveExtractionService archiveExtractionService;

    @Value("${gis.service.url:http://localhost:8001}")
    private String gisServiceUrl;

    /**
     * Upload and validate shapefile.
     * Supports ZIP, RAR4, RAR5, and individual file uploads.
     */
    public UploadResponse uploadAndValidate(MultipartFile[] files) throws IOException {
        List<MultipartFile> processedFiles = new ArrayList<>();
        Path extractPath = Paths.get(UPLOAD_DIR, UUID.randomUUID().toString());
        Files.createDirectories(extractPath);

        try {
            // Process uploaded files
            for (MultipartFile file : files) {
                String filename = file.getOriginalFilename();
                if (filename == null) continue;

                String extension = getExtension(filename);

                if (".zip".equalsIgnoreCase(extension) || ".rar".equalsIgnoreCase(extension)) {
                    processArchive(file, extractPath, processedFiles);
                } else if (REQUIRED_EXTENSIONS.contains(extension)) {
                    processedFiles.add(file);
                }
            }

            // Validate shapefile completeness
            validateShapefileCompleteness(processedFiles);

            // Store in database
            UUID shapefileId = UUID.randomUUID();
            Shapefile shapefile = new Shapefile();
            shapefile.setId(shapefileId);
            shapefile.setFilename(files[0].getOriginalFilename());
            shapefile.setGeometry("POLYGON ((0 0, 0 0, 0 0, 0 0))");
            shapefileRepository.save(shapefile);

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
     * Extract file extension.
     */
    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        return lastDot > 0 ? filename.substring(lastDot).toLowerCase() : "";
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
