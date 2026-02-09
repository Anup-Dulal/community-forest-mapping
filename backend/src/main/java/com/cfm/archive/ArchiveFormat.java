package com.cfm.archive;

/**
 * Enumeration of supported archive formats.
 * Used for format detection and routing to appropriate extractors.
 */
public enum ArchiveFormat {
    ZIP("ZIP archive"),
    RAR4("RAR4 archive"),
    RAR5("RAR5 archive"),
    UNKNOWN("Unknown format");
    
    private final String description;
    
    ArchiveFormat(String description) {
        this.description = description;
    }
    
    public String getDescription() {
        return description;
    }
}
