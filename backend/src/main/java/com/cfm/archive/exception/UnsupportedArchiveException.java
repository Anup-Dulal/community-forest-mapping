package com.cfm.archive.exception;

/**
 * Exception thrown when archive format is not supported.
 */
public class UnsupportedArchiveException extends ArchiveProcessingException {
    
    public UnsupportedArchiveException(String message) {
        super(message);
    }
}
