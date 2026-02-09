package com.cfm.archive;

import be.stef.rar5.Unrar5j;
import be.stef.rar5.ExtractionResult;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Extracts RAR5 archives using pure Java unrar5j library.
 * No native binaries required!
 */
@Slf4j
@Component
public class Rar5Extractor {
    
    /**
     * Extract RAR5 archive using pure Java library.
     * @param rarFile The RAR5 file to extract
     * @param targetDirectory Directory to extract into
     * @return List of extracted file paths
     * @throws IOException if extraction fails
     */
    public List<Path> extract(File rarFile, Path targetDirectory) throws IOException {
        log.info("Extracting RAR5 archive using pure Java library: {}", rarFile.getName());
        
        try {
            // Extract using unrar5j (pure Java, no native dependencies!)
            ExtractionResult result = Unrar5j.extract(
                rarFile.getAbsolutePath(),
                targetDirectory.toString(),
                null  // no password
            );
            
            // Check results
            if (result.errorCount > 0) {
                log.error("RAR5 extraction had {} errors out of {} files", 
                        result.errorCount, result.totalFiles);
                result.print();  // Print error details
                throw new IOException("RAR5 extraction failed with " + result.errorCount + " errors");
            }
            
            log.info("Successfully extracted {} files from RAR5 archive", result.successCount);
            
            // List extracted files recursively (files may be in subdirectories)
            List<Path> extractedFiles = new ArrayList<>();
            try (Stream<Path> files = Files.walk(targetDirectory)) {
                extractedFiles = files
                        .filter(Files::isRegularFile)
                        .collect(Collectors.toList());
            }
            
            log.info("Found {} files after recursive search", extractedFiles.size());
            return extractedFiles;
            
        } catch (Exception e) {
            log.error("Failed to extract RAR5 archive: {}", e.getMessage(), e);
            throw new IOException("Failed to extract RAR5 archive: " + e.getMessage(), e);
        }
    }
    
    /**
     * Check if RAR5 extraction is available.
     * @return true (always available - pure Java implementation)
     */
    public boolean isAvailable() {
        return true;  // Pure Java, always available!
    }
}
