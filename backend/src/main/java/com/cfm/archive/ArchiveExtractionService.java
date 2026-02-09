package com.cfm.archive;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/**
 * Unified service for extracting archives of any supported format.
 * Routes extraction requests to the appropriate extractor based on detected format.
 */
@Slf4j
@Service
public class ArchiveExtractionService {
    
    private final ArchiveFormatDetector formatDetector;
    private final ZipExtractor zipExtractor;
    private final Rar4Extractor rar4Extractor;
    private final Rar5Extractor rar5Extractor;
    
    @Autowired
    public ArchiveExtractionService(
            ArchiveFormatDetector formatDetector,
            ZipExtractor zipExtractor,
            Rar4Extractor rar4Extractor,
            Rar5Extractor rar5Extractor) {
        this.formatDetector = formatDetector;
        this.zipExtractor = zipExtractor;
        this.rar4Extractor = rar4Extractor;
        this.rar5Extractor = rar5Extractor;
    }
    
    /**
     * Extract archive to target directory.
     * @param archiveFile The archive to extract
     * @param targetDirectory Directory to extract files into
     * @return List of extracted file paths
     * @throws IOException if extraction fails
     */
    public List<Path> extractArchive(File archiveFile, Path targetDirectory) throws IOException {
        // Detect format
        ArchiveFormat format = formatDetector.detectFormat(archiveFile);
        log.info("Detected archive format: {} for file: {}", format, archiveFile.getName());
        
        // Route to appropriate extractor
        switch (format) {
            case ZIP:
                return zipExtractor.extract(archiveFile, targetDirectory);
                
            case RAR4:
                return rar4Extractor.extract(archiveFile, targetDirectory);
                
            case RAR5:
                if (!rar5Extractor.isAvailable()) {
                    throw new IOException(
                            "RAR5 format detected but could not be processed. " +
                            "Native unrar binary is not available for this platform. " +
                            "Please convert your RAR5 file to ZIP or RAR4 format.");
                }
                return rar5Extractor.extract(archiveFile, targetDirectory);
                
            case UNKNOWN:
            default:
                throw new IOException(
                        "Unable to determine archive format. Supported formats: ZIP, RAR4, RAR5. " +
                        "Please ensure your file is a valid archive.");
        }
    }
    
    /**
     * Extract archive from MultipartFile.
     * @param multipartFile The uploaded archive
     * @param targetDirectory Directory to extract files into
     * @return List of extracted file paths
     * @throws IOException if extraction fails
     */
    public List<Path> extractArchive(MultipartFile multipartFile, Path targetDirectory) throws IOException {
        // Create temp file for the uploaded archive
        File tempArchive = null;
        try {
            String originalFilename = multipartFile.getOriginalFilename();
            String suffix = originalFilename != null ? originalFilename.substring(originalFilename.lastIndexOf('.')) : ".tmp";
            tempArchive = Files.createTempFile("archive_", suffix).toFile();
            multipartFile.transferTo(tempArchive);
            
            return extractArchive(tempArchive, targetDirectory);
            
        } finally {
            // Cleanup temp archive file
            if (tempArchive != null && tempArchive.exists()) {
                if (!tempArchive.delete()) {
                    log.warn("Failed to delete temp archive file: {}", tempArchive);
                }
            }
        }
    }
}
