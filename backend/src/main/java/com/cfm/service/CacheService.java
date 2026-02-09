package com.cfm.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Cache service for storing and managing cached data.
 * Implements TTL (time-to-live) based cache invalidation.
 */
@Service
@Slf4j
public class CacheService {

    private static final long DEFAULT_TTL_MINUTES = 60;
    private static final long CACHE_CLEANUP_INTERVAL_MINUTES = 30;

    private final Map<String, CacheEntry<?>> cache = new ConcurrentHashMap<>();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    public CacheService() {
        // Start cache cleanup task
        scheduler.scheduleAtFixedRate(
            this::cleanupExpiredEntries,
            CACHE_CLEANUP_INTERVAL_MINUTES,
            CACHE_CLEANUP_INTERVAL_MINUTES,
            TimeUnit.MINUTES
        );
    }

    /**
     * Put a value in the cache with default TTL.
     */
    public <T> void put(String key, T value) {
        put(key, value, DEFAULT_TTL_MINUTES);
    }

    /**
     * Put a value in the cache with custom TTL.
     */
    public <T> void put(String key, T value, long ttlMinutes) {
        long expirationTime = System.currentTimeMillis() + (ttlMinutes * 60 * 1000);
        cache.put(key, new CacheEntry<>(value, expirationTime));
        log.debug("Cached value for key: {} with TTL: {} minutes", key, ttlMinutes);
    }

    /**
     * Get a value from the cache.
     */
    @SuppressWarnings("unchecked")
    public <T> T get(String key, Class<T> type) {
        CacheEntry<?> entry = cache.get(key);
        
        if (entry == null) {
            log.debug("Cache miss for key: {}", key);
            return null;
        }
        
        if (entry.isExpired()) {
            cache.remove(key);
            log.debug("Cache entry expired for key: {}", key);
            return null;
        }
        
        log.debug("Cache hit for key: {}", key);
        return (T) entry.getValue();
    }

    /**
     * Check if a key exists in the cache.
     */
    public boolean containsKey(String key) {
        CacheEntry<?> entry = cache.get(key);
        
        if (entry == null) {
            return false;
        }
        
        if (entry.isExpired()) {
            cache.remove(key);
            return false;
        }
        
        return true;
    }

    /**
     * Remove a value from the cache.
     */
    public void remove(String key) {
        cache.remove(key);
        log.debug("Removed cache entry for key: {}", key);
    }

    /**
     * Clear all cache entries.
     */
    public void clear() {
        cache.clear();
        log.info("Cache cleared");
    }

    /**
     * Get cache statistics.
     */
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalEntries", cache.size());
        stats.put("validEntries", cache.values().stream()
            .filter(entry -> !entry.isExpired())
            .count());
        stats.put("expiredEntries", cache.values().stream()
            .filter(CacheEntry::isExpired)
            .count());
        return stats;
    }

    /**
     * Clean up expired cache entries.
     */
    private void cleanupExpiredEntries() {
        int removedCount = 0;
        for (String key : cache.keySet()) {
            CacheEntry<?> entry = cache.get(key);
            if (entry != null && entry.isExpired()) {
                cache.remove(key);
                removedCount++;
            }
        }
        
        if (removedCount > 0) {
            log.info("Cleaned up {} expired cache entries", removedCount);
        }
    }

    /**
     * Shutdown the cache service.
     */
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Inner class representing a cache entry with expiration time.
     */
    private static class CacheEntry<T> {
        private final T value;
        private final long expirationTime;

        CacheEntry(T value, long expirationTime) {
            this.value = value;
            this.expirationTime = expirationTime;
        }

        T getValue() {
            return value;
        }

        boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }
    }
}
