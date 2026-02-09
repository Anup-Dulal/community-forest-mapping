package com.cfm.archive.exception;

/**
 * Base exception for archive processing errors.
 */
public class ArchiveProcessingException extends RuntimeException {
    
    public ArchiveProcessingException(String message) {
        super(message);
    }
    
    public ArchiveProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}
