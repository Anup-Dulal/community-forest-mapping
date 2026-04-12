package com.cfm.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

/**
 * WebSocket configuration for real-time progress streaming.
 * Enables STOMP messaging over WebSocket for progress updates.
 * Requirements: 15.1, 15.4, 15.6, 19.1, 19.2
 */
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    /**
     * Configure message broker for WebSocket communication.
     */
    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        // Enable simple message broker for /topic destinations
        config.enableSimpleBroker("/topic");
        
        // Set application destination prefix for client messages
        config.setApplicationDestinationPrefixes("/app");
    }

    /**
     * Register STOMP endpoints for WebSocket connections.
     */
    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // Register WebSocket endpoint for progress streaming
        registry.addEndpoint("/ws/progress")
                .setAllowedOrigins("*")
                .withSockJS();
    }
}
