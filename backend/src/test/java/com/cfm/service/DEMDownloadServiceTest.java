package com.cfm.service;

import com.cfm.dto.DEMStatusResponse;
import com.cfm.model.DEM;
import com.cfm.model.Shapefile;
import com.cfm.repository.DEMRepository;
import com.cfm.repository.ShapefileRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.web.client.RestTemplate;

import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

/**
 * Unit tests for DEMDownloadService.
 * Tests DEM download orchestration and status tracking.
 */
@DisplayName("DEMDownloadService Tests")
class DEMDownloadServiceTest {

    private DEMDownloadService service;

    @Mock
    private DEMRepository demRepository;

    @Mock
    private ShapefileRepository shapefileRepository;

    @Mock
    private RestTemplate restTemplate;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        service = new DEMDownloadService(demRepository, shapefileRepository, restTemplate);
    }

    @Test
    @DisplayName("Should throw exception when shapefile not found")
    void testDownloadDEMShapefileNotFound() {
        // Arrange
        UUID shapefileId = UUID.randomUUID();
        when(shapefileRepository.findById(shapefileId)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(
            RuntimeException.class,
            () -> service.downloadDEM(shapefileId, "SRTM")
        );
    }

    @Test
    @DisplayName("Should return existing DEM if already clipped")
    void testDownloadDEMAlreadyClipped() {
        // Arrange
        UUID shapefileId = UUID.randomUUID();
        UUID demId = UUID.randomUUID();

        Shapefile shapefile = Shapefile.builder()
            .id(shapefileId)
            .filename("test")
            .status("parsed")
            .build();

        DEM existingDEM = DEM.builder()
            .id(demId)
            .shapefile(shapefile)
            .source("SRTM")
            .status("clipped")
            .build();

        when(shapefileRepository.findById(shapefileId)).thenReturn(Optional.of(shapefile));
        when(demRepository.findByShapefileId(shapefileId)).thenReturn(Optional.of(existingDEM));

        // Act
        DEMStatusResponse response = service.downloadDEM(shapefileId, "SRTM");

        // Assert
        assertNotNull(response);
        assertEquals("clipped", response.getStatus());
        assertEquals(100, response.getProgressPercentage());
    }

    @Test
    @DisplayName("Should create new DEM and start download")
    void testDownloadDEMNewDEM() {
        // Arrange
        UUID shapefileId = UUID.randomUUID();
        UUID demId = UUID.randomUUID();

        Shapefile shapefile = Shapefile.builder()
            .id(shapefileId)
            .filename("test")
            .status("parsed")
            .build();

        DEM newDEM = DEM.builder()
            .id(demId)
            .shapefile(shapefile)
            .source("SRTM")
            .status("downloading")
            .build();

        when(shapefileRepository.findById(shapefileId)).thenReturn(Optional.of(shapefile));
        when(demRepository.findByShapefileId(shapefileId)).thenReturn(Optional.empty());
        when(demRepository.save(any(DEM.class))).thenReturn(newDEM);

        // Act
        DEMStatusResponse response = service.downloadDEM(shapefileId, "SRTM");

        // Assert
        assertNotNull(response);
        assertEquals("downloading", response.getStatus());
        assertEquals(25, response.getProgressPercentage());
    }

    @Test
    @DisplayName("Should retrieve DEM status")
    void testGetDEMStatus() {
        // Arrange
        UUID demId = UUID.randomUUID();
        DEM dem = DEM.builder()
            .id(demId)
            .source("SRTM")
            .status("clipped")
            .build();

        when(demRepository.findById(demId)).thenReturn(Optional.of(dem));

        // Act
        DEMStatusResponse response = service.getDEMStatus(demId);

        // Assert
        assertNotNull(response);
        assertEquals(demId, response.getDemId());
        assertEquals("clipped", response.getStatus());
    }

    @Test
    @DisplayName("Should throw exception when DEM not found")
    void testGetDEMStatusNotFound() {
        // Arrange
        UUID demId = UUID.randomUUID();
        when(demRepository.findById(demId)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(
            RuntimeException.class,
            () -> service.getDEMStatus(demId)
        );
    }

    @Test
    @DisplayName("Should calculate correct progress percentage")
    void testProgressCalculation() {
        // Arrange
        UUID demId = UUID.randomUUID();

        // Test downloading status
        DEM downloadingDEM = DEM.builder()
            .id(demId)
            .source("SRTM")
            .status("downloading")
            .build();

        when(demRepository.findById(demId)).thenReturn(Optional.of(downloadingDEM));
        DEMStatusResponse response = service.getDEMStatus(demId);
        assertEquals(25, response.getProgressPercentage());

        // Test downloaded status
        DEM downloadedDEM = DEM.builder()
            .id(demId)
            .source("SRTM")
            .status("downloaded")
            .build();

        when(demRepository.findById(demId)).thenReturn(Optional.of(downloadedDEM));
        response = service.getDEMStatus(demId);
        assertEquals(50, response.getProgressPercentage());

        // Test clipping status
        DEM clippingDEM = DEM.builder()
            .id(demId)
            .source("SRTM")
            .status("clipping")
            .build();

        when(demRepository.findById(demId)).thenReturn(Optional.of(clippingDEM));
        response = service.getDEMStatus(demId);
        assertEquals(75, response.getProgressPercentage());

        // Test clipped status
        DEM clippedDEM = DEM.builder()
            .id(demId)
            .source("SRTM")
            .status("clipped")
            .build();

        when(demRepository.findById(demId)).thenReturn(Optional.of(clippedDEM));
        response = service.getDEMStatus(demId);
        assertEquals(100, response.getProgressPercentage());
    }
}
