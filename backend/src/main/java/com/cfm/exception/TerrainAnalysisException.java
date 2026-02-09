package com.cfm.exception;

/**
 * Exception thrown when terrain analysis fails.
 */
public class TerrainAnalysisException extends RuntimeException {
    public TerrainAnalysisException(String message) {
        super(message);
    }

    public TerrainAnalysisException(String message, Throwable cause) {
        super(message, cause);
    }
}
