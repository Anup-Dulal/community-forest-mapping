package com.cfm.archive;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermission;
import java.util.HashSet;
import java.util.Set;

/**
 * Manages extraction and lifecycle of bundled native unrar binaries.
 */
@Slf4j
@Component
public class NativeBinaryManager {
    
    private final PlatformInfo platformInfo;
    private Path extractedBinaryPath;
    private boolean binaryAvailable = false;
    
    public NativeBinaryManager() {
        this.platformInfo = PlatformInfo.detect();
    }
    
    @PostConstruct
    public void initialize() {
        log.info("Initializing NativeBinaryManager for platform: {}", platformInfo);
        
        if (!platformInfo.getPlatformType().isSupported()) {
            log.warn("Platform {} is not supported for RAR5 extraction. RAR5 support will be disabled.", 
                    platformInfo.getPlatformType());
            return;
        }
        
        try {
            extractedBinaryPath = extractBinaryFromResources();
            binaryAvailable = true;
            log.info("Native unrar binary extracted successfully to: {}", extractedBinaryPath);
        } catch (IOException e) {
            log.error("Failed to extract native unrar binary: {}", e.getMessage(), e);
            log.warn("RAR5 support will be disabled. ZIP and RAR4 formats will continue to work.");
        }
    }
    
    /**
     * Get path to extracted unrar binary for current platform.
     * @return Path to executable unrar binary
     * @throws IOException if binary cannot be extracted or is unavailable
     */
    public Path getUnrarBinaryPath() throws IOException {
        if (!binaryAvailable) {
            throw new IOException("Native unrar binary is not available for platform: " + platformInfo.getPlatformType());
        }
        return extractedBinaryPath;
    }
    
    /**
     * Check if unrar binary is available for current platform.
     * @return true if binary is available and executable
     */
    public boolean isBinaryAvailable() {
        return binaryAvailable;
    }
    
    /**
     * Extract binary from JAR resources to temp directory.
     */
    private Path extractBinaryFromResources() throws IOException {
        String resourcePath = platformInfo.getPlatformType().getResourcePath();
        if (resourcePath == null) {
            throw new IOException("No resource path for platform: " + platformInfo.getPlatformType());
        }
        
        // Read binary from resources
        InputStream resourceStream = getClass().getClassLoader().getResourceAsStream(resourcePath);
        if (resourceStream == null) {
            throw new IOException("Binary not found in resources: " + resourcePath);
        }
        
        // Create temp file
        String binaryName = platformInfo.getPlatformType().getBinaryName();
        Path tempFile = Files.createTempFile("unrar_", "_" + binaryName);
        
        // Copy binary to temp file
        try (InputStream is = resourceStream;
             OutputStream os = new FileOutputStream(tempFile.toFile())) {
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
        }
        
        // Set executable permissions on Unix platforms
        if (!platformInfo.getOsName().contains("win")) {
            setExecutablePermissions(tempFile);
        }
        
        // Register shutdown hook to cleanup
        registerShutdownHook(tempFile);
        
        return tempFile;
    }
    
    /**
     * Set executable permissions on Unix platforms.
     */
    private void setExecutablePermissions(Path file) throws IOException {
        try {
            Set<PosixFilePermission> perms = new HashSet<>();
            perms.add(PosixFilePermission.OWNER_READ);
            perms.add(PosixFilePermission.OWNER_WRITE);
            perms.add(PosixFilePermission.OWNER_EXECUTE);
            perms.add(PosixFilePermission.GROUP_READ);
            perms.add(PosixFilePermission.GROUP_EXECUTE);
            perms.add(PosixFilePermission.OTHERS_READ);
            perms.add(PosixFilePermission.OTHERS_EXECUTE);
            Files.setPosixFilePermissions(file, perms);
            log.debug("Set executable permissions on: {}", file);
        } catch (UnsupportedOperationException e) {
            log.debug("POSIX permissions not supported on this platform");
        }
    }
    
    /**
     * Register shutdown hook to cleanup temp binary.
     */
    private void registerShutdownHook(Path file) {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try {
                if (Files.exists(file)) {
                    Files.delete(file);
                    log.debug("Cleaned up temp binary: {}", file);
                }
            } catch (IOException e) {
                log.warn("Failed to cleanup temp binary {}: {}", file, e.getMessage());
            }
        }));
    }
    
    /**
     * Clean up extracted binaries on shutdown.
     */
    @PreDestroy
    public void cleanup() {
        if (extractedBinaryPath != null && Files.exists(extractedBinaryPath)) {
            try {
                Files.delete(extractedBinaryPath);
                log.info("Cleaned up extracted binary: {}", extractedBinaryPath);
            } catch (IOException e) {
                log.warn("Failed to cleanup binary {}: {}", extractedBinaryPath, e.getMessage());
            }
        }
    }
}
