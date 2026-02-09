package com.cfm.exception;

/**
 * Exception thrown when sample plot generation fails.
 */
public class SamplePlotGenerationException extends RuntimeException {
    public SamplePlotGenerationException(String message) {
        super(message);
    }

    public SamplePlotGenerationException(String message, Throwable cause) {
        super(message, cause);
    }
}
