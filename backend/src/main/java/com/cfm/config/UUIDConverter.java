package com.cfm.config;

import org.springframework.core.convert.converter.Converter;
import org.springframework.stereotype.Component;

import java.util.UUID;

/**
 * Custom UUID converter for Spring that handles various UUID formats.
 * Provides lenient parsing to handle edge cases in UUID string conversion.
 */
@Component
public class UUIDConverter implements Converter<String, UUID> {
    
    @Override
    public UUID convert(String source) {
        if (source == null || source.trim().isEmpty()) {
            return null;
        }
        
        try {
            // Try standard UUID parsing first
            return UUID.fromString(source.trim());
        } catch (IllegalArgumentException e) {
            // If standard parsing fails, try removing any extra characters
            String cleaned = source.trim()
                .replaceAll("[^0-9a-fA-F-]", "")
                .toLowerCase();
            
            // Ensure proper UUID format (8-4-4-4-12)
            if (cleaned.length() == 32) {
                cleaned = cleaned.substring(0, 8) + "-" +
                         cleaned.substring(8, 12) + "-" +
                         cleaned.substring(12, 16) + "-" +
                         cleaned.substring(16, 20) + "-" +
                         cleaned.substring(20, 32);
            }
            
            try {
                return UUID.fromString(cleaned);
            } catch (IllegalArgumentException ex) {
                throw new IllegalArgumentException(
                    "Invalid UUID format: " + source + ". Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                    ex
                );
            }
        }
    }
}
