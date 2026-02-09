package com.cfm.controller;

import com.cfm.service.SessionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/sessions")
public class SessionController {

    @Autowired
    private SessionService sessionService;

    @PostMapping("/create")
    public ResponseEntity<Map<String, String>> createSession() {
        String sessionId = sessionService.createSession();
        return ResponseEntity.ok(Map.of("sessionId", sessionId));
    }

    @GetMapping("/{sessionId}/data")
    public ResponseEntity<Map<String, Object>> getSessionData(@PathVariable String sessionId) {
        Map<String, Object> sessionData = sessionService.getSessionData(sessionId);
        return ResponseEntity.ok(sessionData);
    }

    @GetMapping("/{sessionId}/analysis-results")
    public ResponseEntity<Object> getAnalysisResults(@PathVariable String sessionId) {
        return ResponseEntity.ok(sessionService.getAnalysisResults(sessionId));
    }

    @GetMapping("/{sessionId}/validate")
    public ResponseEntity<Map<String, Object>> validateDataPersistence(
            @RequestParam UUID analysisResultId) {
        Map<String, Object> validationResult = sessionService.validateDataPersistence(analysisResultId);
        return ResponseEntity.ok(validationResult);
    }

    @DeleteMapping("/{sessionId}")
    public ResponseEntity<Map<String, String>> clearSession(@PathVariable String sessionId) {
        sessionService.clearSession(sessionId);
        return ResponseEntity.ok(Map.of("message", "Session cleared successfully"));
    }
}
