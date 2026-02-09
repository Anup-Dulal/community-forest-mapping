package com.cfm.archive;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.compress.archivers.zip.ZipFile;
import org.apache.commons.compress.archivers.zip.ZipArchiveEntry;
import org.springframework.stereotype.Component;

import java.io.*;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;

/**
 * Extracts ZIP archives using Apache Commons Compress.
 */
@Slf4j
@Component
public class ZipExtractor {
    
    /**
     * Extract ZIP archive.
     * @param zipFile The ZIP file to extract
     * @param targetDirectory Directory to extract into
     * @return List of extracted file paths
     * @throws IOException if extraction fails
     */
    public List<Path> extract(File zipFile, Path targetDirectory) throws IOException {
        List<Path> extractedFiles = new ArrayList<>();
        
        try (ZipFile zip = new ZipFile(zipFile)) {
            Enumeration<ZipArchiveEntry> entries = zip.getEntries();
            
            while (entries.hasMoreElements()) {
                ZipArchiveEntry entry = entries.nextElement();
                
                if (entry.isDirectory()) {
                    continue;
                }
                
                // Get just the filename (no path)
                String filename = new File(entry.getName()).getName();
                
                // Validate filename to prevent directory traversal
                if (filename.contains("..") || filename.contains("/") || filename.contains("\\")) {
                    log.warn("Skipping potentially unsafe filename: {}", filename);
                    continue;
                }
                
                Path targetFile = targetDirectory.resolve(filename);
                
                // Extract file
                try (InputStream is = zip.getInputStream(entry);
                     OutputStream os = new FileOutputStream(targetFile.toFile())) {
                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = is.read(buffer)) != -1) {
                        os.write(buffer, 0, bytesRead);
                    }
                }
                
                extractedFiles.add(targetFile);
                log.debug("Extracted from ZIP: {}", filename);
            }
        }
        
        log.info("Extracted {} files from ZIP archive", extractedFiles.size());
        return extractedFiles;
    }
}
