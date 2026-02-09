package com.cfm.exception;

/**
 * Exception thrown when compartment generation fails.
 */
public class CompartmentGenerationException extends RuntimeException {
    public CompartmentGenerationException(String message) {
        super(message);
    }

    public CompartmentGenerationException(String message, Throwable cause) {
        super(message, cause);
    }
}
