package com.cfm.archive;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.*;

/**
 * Detects archive format by reading file signatures (magic bytes).
 * Does not rely on file extensions for detection.
 */
@Slf4j
@Component
public class ArchiveFormatDetector {
    
    // File signatures (magic bytes)
    private static final byte[] ZIP_SIGNATURE = {0x50, 0x4B, 0x03, 0x04}; // PK..
    private static final byte[] RAR4_SIGNATURE = {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x00}; // Rar!...
    private static final byte[] RAR5_SIGNATURE = {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x01, 0x00}; // Rar!....
    
    /**
     * Detect archive format by reading file signature.
     * @param file The archive file to detect
     * @return Detected archive format
     * @throws IOException if file cannot be read
     */
    public ArchiveFormat detectFormat(File file) throws IOException {
        try (FileInputStream fis = new FileInputStream(file)) {
            return detectFormat(fis);
        }
    }
    
    /**
     * Detect archive format from input stream.
     * @param inputStream Stream to read (will read first 16 bytes)
     * @return Detected archive format
     * @throws IOException if stream cannot be read
     */
    public ArchiveFormat detectFormat(InputStream inputStream) throws IOException {
        // Mark the stream so we can reset it after reading
        if (!inputStream.markSupported()) {
            inputStream = new BufferedInputStream(inputStream);
        }
        
        inputStream.mark(16);
        
        try {
            byte[] header = new byte[8];
            int bytesRead = inputStream.read(header);
            
            if (bytesRead < 4) {
                log.debug("File too small to determine format (only {} bytes)", bytesRead);
                return ArchiveFormat.UNKNOWN;
            }
            
            // Check ZIP signature (4 bytes)
            if (matchesSignature(header, ZIP_SIGNATURE)) {
                log.debug("Detected ZIP format");
                return ArchiveFormat.ZIP;
            }
            
            // Check RAR5 signature (8 bytes) - must check before RAR4
            if (bytesRead >= 8 && matchesSignature(header, RAR5_SIGNATURE)) {
                log.debug("Detected RAR5 format");
                return ArchiveFormat.RAR5;
            }
            
            // Check RAR4 signature (7 bytes)
            if (bytesRead >= 7 && matchesSignature(header, RAR4_SIGNATURE)) {
                log.debug("Detected RAR4 format");
                return ArchiveFormat.RAR4;
            }
            
            log.debug("Unknown archive format");
            return ArchiveFormat.UNKNOWN;
            
        } finally {
            // Reset stream to beginning
            inputStream.reset();
        }
    }
    
    /**
     * Check if header bytes match the expected signature.
     */
    private boolean matchesSignature(byte[] header, byte[] signature) {
        if (header.length < signature.length) {
            return false;
        }
        
        for (int i = 0; i < signature.length; i++) {
            if (header[i] != signature[i]) {
                return false;
            }
        }
        
        return true;
    }
}
