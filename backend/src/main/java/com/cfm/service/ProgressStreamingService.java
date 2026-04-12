package com.cfm.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Service for streaming progress updates via WebSocket.
 * Broadcasts progress updates to connected clients.
 * Requirements: 15.1, 15.4, 15.6, 19.1, 19.2, 19.3, 19.4
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class ProgressStreamingService {

    private final SimpMessagingTemplate messagingTemplate;

    /**
     * Send progress update to connected clients.
     * Requirements: 19.1, 19.2, 19.3
     *
     * @param operationId Unique identifier for the operation
     * @param operation Type of operation (compartment_generation, slope_calculation, etc.)
     * @param percentage Progress percentage (0-100)
     * @param estimatedTimeRemaining Estimated time remaining in seconds
     * @param statusMessage Current status message
     * @param currentStep Current step being executed
     */
    public void sendProgressUpdate(
            String operationId,
            String operation,
            int percentage,
            long estimatedTimeRemaining,
            String statusMessage,
            String currentStep
    ) {
        try {
            Map<String, Object> progressUpdate = new HashMap<>();
            progressUpdate.put("operationId", operationId);
            progressUpdate.put("operation", operation);
            progressUpdate.put("percentage", Math.min(100, Math.max(0, percentage)));
            progressUpdate.put("estimatedTimeRemaining", estimatedTimeRemaining);
            progressUpdate.put("statusMessage", statusMessage);
            progressUpdate.put("currentStep", currentStep);
            progressUpdate.put("timestamp", LocalDateTime.now().toString());

            // Send to all subscribers of the progress topic
            String destination = "/topic/progress/" + operationId;
            messagingTemplate.convertAndSend(destination, progressUpdate);

            log.debug("Progress update sent: {} - {}%", operationId, percentage);
        } catch (Exception e) {
            log.error("Error sending progress update", e);
        }
    }

    /**
     * Send completion notification.
     * Requirements: 15.8, 19.6
     *
     * @param operationId Unique identifier for the operation
     * @param operation Type of operation
     * @param statusMessage Completion message
     * @param summary Summary statistics
     */
    public void sendCompletionNotification(
            String operationId,
            String operation,
            String statusMessage,
            Map<String, Object> summary
    ) {
        try {
            Map<String, Object> notification = new HashMap<>();
            notification.put("operationId", operationId);
            notification.put("operation", operation);
            notification.put("percentage", 100);
            notification.put("statusMessage", statusMessage);
            notification.put("status", "completed");
            notification.put("summary", summary);
            notification.put("timestamp", LocalDateTime.now().toString());

            String destination = "/topic/progress/" + operationId;
            messagingTemplate.convertAndSend(destination, notification);

            log.info("Completion notification sent: {}", operationId);
        } catch (Exception e) {
            log.error("Error sending completion notification", e);
        }
    }

    /**
     * Send error notification.
     * Requirements: 19.7
     *
     * @param operationId Unique identifier for the operation
     * @param operation Type of operation
     * @param errorMessage Error message
     * @param troubleshootingSteps Suggested troubleshooting steps
     */
    public void sendErrorNotification(
            String operationId,
            String operation,
            String errorMessage,
            String troubleshootingSteps
    ) {
        try {
            Map<String, Object> errorNotification = new HashMap<>();
            errorNotification.put("operationId", operationId);
            errorNotification.put("operation", operation);
            errorNotification.put("status", "error");
            errorNotification.put("errorMessage", errorMessage);
            errorNotification.put("troubleshootingSteps", troubleshootingSteps);
            errorNotification.put("timestamp", LocalDateTime.now().toString());

            String destination = "/topic/progress/" + operationId;
            messagingTemplate.convertAndSend(destination, errorNotification);

            log.error("Error notification sent: {} - {}", operationId, errorMessage);
        } catch (Exception e) {
            log.error("Error sending error notification", e);
        }
    }

    /**
     * Generate a unique operation ID.
     *
     * @return UUID as string
     */
    public String generateOperationId() {
        return UUID.randomUUID().toString();
    }
}
