package com.cfm.exception;

/**
 * Exception thrown when DEM download fails.
 */
public class DEMDownloadException extends RuntimeException {
    public DEMDownloadException(String message) {
        super(message);
    }

    public DEMDownloadException(String message, Throwable cause) {
        super(message, cause);
    }
}
