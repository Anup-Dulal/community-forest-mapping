package com.cfm.archive;

import com.github.junrar.Archive;
import com.github.junrar.rarfile.FileHeader;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.*;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Extracts RAR4 archives using JUnRAR library.
 */
@Slf4j
@Component
public class Rar4Extractor {
    
    /**
     * Extract RAR4 archive.
     * @param rarFile The RAR4 file to extract
     * @param targetDirectory Directory to extract into
     * @return List of extracted file paths
     * @throws IOException if extraction fails
     */
    public List<Path> extract(File rarFile, Path targetDirectory) throws IOException {
        List<Path> extractedFiles = new ArrayList<>();
        
        try (Archive archive = new Archive(rarFile)) {
            FileHeader fileHeader;
            
            while ((fileHeader = archive.nextFileHeader()) != null) {
                if (fileHeader.isDirectory()) {
                    continue;
                }
                
                // Use getFileName() instead of deprecated getFileNameString()
                String filename = new File(fileHeader.getFileName()).getName();
                
                // Validate filename to prevent directory traversal
                if (filename.contains("..") || filename.contains("/") || filename.contains("\\")) {
                    log.warn("Skipping potentially unsafe filename: {}", filename);
                    continue;
                }
                
                Path targetFile = targetDirectory.resolve(filename);
                
                // Extract file
                try (OutputStream os = new FileOutputStream(targetFile.toFile())) {
                    archive.extractFile(fileHeader, os);
                }
                
                extractedFiles.add(targetFile);
                log.debug("Extracted from RAR4: {}", filename);
            }
            
        } catch (com.github.junrar.exception.UnsupportedRarV5Exception e) {
            throw new IOException("RAR5 format detected but not supported by RAR4 extractor. " +
                    "This should have been detected earlier.", e);
        } catch (Exception e) {
            throw new IOException("Failed to extract RAR4 archive: " + e.getMessage(), e);
        }
        
        log.info("Extracted {} files from RAR4 archive", extractedFiles.size());
        return extractedFiles;
    }
}
