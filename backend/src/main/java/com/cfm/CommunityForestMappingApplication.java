package com.cfm;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

/**
 * Main Spring Boot application class for Community Forest Mapping system.
 * Initializes the application and configures core beans.
 */
@SpringBootApplication
public class CommunityForestMappingApplication {

    public static void main(String[] args) {
        SpringApplication.run(CommunityForestMappingApplication.class, args);
    }

    /**
     * Configure RestTemplate bean for HTTP communication with GIS service.
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
