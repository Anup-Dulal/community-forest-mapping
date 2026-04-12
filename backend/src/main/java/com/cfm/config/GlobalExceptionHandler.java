package com.cfm.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.mvc.support.DefaultHandlerExceptionResolver;

import java.util.Map;
import java.util.UUID;

/**
 * Global exception handler for REST controllers.
 * Handles type conversion errors and provides meaningful error responses.
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Handle UUID conversion errors.
     * Provides a helpful error message when UUID parameter is invalid.
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<Map<String, Object>> handleTypeMismatch(MethodArgumentTypeMismatchException ex) {
        String paramName = ex.getName();
        String paramValue = ex.getValue() != null ? ex.getValue().toString() : "null";
        
        // Check if this is a UUID conversion error
        if (ex.getRequiredType() == UUID.class) {
            log.warn("Invalid UUID format for parameter '{}': {}", paramName, paramValue);
            
            return ResponseEntity.badRequest().body(Map.of(
                "error", "Invalid UUID format",
                "parameter", paramName,
                "value", paramValue,
                "message", "Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "status", 400
            ));
        }
        
        log.warn("Type mismatch for parameter '{}': expected {}, got {}", 
            paramName, ex.getRequiredType().getSimpleName(), paramValue);
        
        return ResponseEntity.badRequest().body(Map.of(
            "error", "Invalid parameter type",
            "parameter", paramName,
            "expectedType", ex.getRequiredType().getSimpleName(),
            "value", paramValue,
            "status", 400
        ));
    }

    /**
     * Handle general exceptions.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneralException(Exception ex) {
        log.error("Unexpected error", ex);
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
            "error", "Internal server error",
            "message", ex.getMessage(),
            "status", 500
        ));
    }
}
