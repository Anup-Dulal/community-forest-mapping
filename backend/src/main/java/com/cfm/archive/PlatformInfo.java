package com.cfm.archive;

import lombok.Getter;

/**
 * Platform detection and information for native binary management.
 */
@Getter
public class PlatformInfo {
    
    private final String osName;
    private final String osArch;
    private final PlatformType platformType;
    
    /**
     * Supported platform types with resource paths.
     */
    public enum PlatformType {
        WINDOWS_X64("windows-x64", "unrar.exe"),
        MACOS_X64("macos-x64", "unrar"),
        MACOS_AARCH64("macos-aarch64", "unrar"),
        UNSUPPORTED("unsupported", null);
        
        private final String resourcePath;
        private final String binaryName;
        
        PlatformType(String resourcePath, String binaryName) {
            this.resourcePath = resourcePath;
            this.binaryName = binaryName;
        }
        
        public String getResourcePath() {
            if (binaryName == null) {
                return null;
            }
            return "binaries/" + resourcePath + "/" + binaryName;
        }
        
        public String getBinaryName() {
            return binaryName;
        }
        
        public boolean isSupported() {
            return this != UNSUPPORTED;
        }
    }
    
    private PlatformInfo(String osName, String osArch, PlatformType platformType) {
        this.osName = osName;
        this.osArch = osArch;
        this.platformType = platformType;
    }
    
    /**
     * Detect current platform.
     * @return PlatformInfo with detected platform type
     */
    public static PlatformInfo detect() {
        String osName = System.getProperty("os.name").toLowerCase();
        String osArch = System.getProperty("os.arch").toLowerCase();
        
        PlatformType type;
        if (osName.contains("win") && osArch.contains("64")) {
            type = PlatformType.WINDOWS_X64;
        } else if (osName.contains("mac")) {
            if (osArch.contains("aarch64") || osArch.contains("arm")) {
                type = PlatformType.MACOS_AARCH64;
            } else {
                type = PlatformType.MACOS_X64;
            }
        } else {
            type = PlatformType.UNSUPPORTED;
        }
        
        return new PlatformInfo(osName, osArch, type);
    }
    
    @Override
    public String toString() {
        return String.format("Platform{os=%s, arch=%s, type=%s}", osName, osArch, platformType);
    }
}
