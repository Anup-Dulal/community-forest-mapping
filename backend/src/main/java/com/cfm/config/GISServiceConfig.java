package com.cfm.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

/**
 * Configuration properties for GIS microservice integration.
 */
@Configuration
@ConfigurationProperties(prefix = "app")
@Data
public class GISServiceConfig {
    private String name;
    private String version;
    private String uploadDir;
    private String demCacheDir;
    private String exportDir;
    private String gisServiceUrl;
    private Integer gisServiceTimeout;
}
