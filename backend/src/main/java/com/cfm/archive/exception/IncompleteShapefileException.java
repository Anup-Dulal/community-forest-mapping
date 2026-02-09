package com.cfm.archive.exception;

/**
 * Exception thrown when shapefile is missing required components.
 */
public class IncompleteShapefileException extends ArchiveProcessingException {
    
    public IncompleteShapefileException(String message) {
        super(message);
    }
}
