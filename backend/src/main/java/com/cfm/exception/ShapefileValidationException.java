package com.cfm.exception;

/**
 * Exception thrown when shapefile validation fails.
 */
public class ShapefileValidationException extends RuntimeException {
    public ShapefileValidationException(String message) {
        super(message);
    }

    public ShapefileValidationException(String message, Throwable cause) {
        super(message, cause);
    }
}
