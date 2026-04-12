package com.cfm.archive;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Placeholder for RAR5 extraction.
 * RAR5 support requires external library not available in Maven Central.
 * Use RAR4 (junrar) or ZIP formats instead.
 */
@Slf4j
@Component
public class Rar5Extractor {
    
    /**
     * Extract RAR5 archive - currently not supported.
     * @param rarFile The RAR5 file to extract
     * @param targetDirectory Directory to extract into
     * @return List of extracted file paths
     * @throws IOException if extraction fails
     */
    public List<Path> extract(File rarFile, Path targetDirectory) throws IOException {
        log.warn("RAR5 extraction not supported. Please use RAR4 or ZIP format instead.");
        throw new IOException("RAR5 extraction not supported. Please use RAR4 or ZIP format instead.");
    }
    
    /**
     * Check if RAR5 extraction is available.
     * @return false (not available)
     */
    public boolean isAvailable() {
        return false;
    }
}
