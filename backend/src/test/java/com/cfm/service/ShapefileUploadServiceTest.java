package com.cfm.service;

import com.cfm.dto.UploadResponse;
import com.cfm.model.Shapefile;
import com.cfm.repository.ShapefileRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.client.RestTemplate;

import java.io.IOException;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

/**
 * Unit tests for ShapefileUploadService.
 * Tests shapefile validation and upload functionality.
 */
@DisplayName("ShapefileUploadService Tests")
class ShapefileUploadServiceTest {

    @Mock
    private ShapefileRepository shapefileRepository;

    private ShapefileUploadService service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        service = new ShapefileUploadService();
        // Manually inject mocks using reflection
        try {
            java.lang.reflect.Field shapefileRepoField = ShapefileUploadService.class.getDeclaredField("shapefileRepository");
            shapefileRepoField.setAccessible(true);
            shapefileRepoField.set(service, shapefileRepository);
            
            java.lang.reflect.Field uploadDirField = ShapefileUploadService.class.getDeclaredField("uploadDir");
            uploadDirField.setAccessible(true);
            uploadDirField.set(service, "./test-uploads");
            
            java.lang.reflect.Field gisServiceUrlField = ShapefileUploadService.class.getDeclaredField("gisServiceUrl");
            gisServiceUrlField.setAccessible(true);
            gisServiceUrlField.set(service, "http://localhost:8001");
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    @DisplayName("Should reject upload with missing .shp file")
    void testUploadWithMissingShpFile() {
        // Arrange
        MultipartFile[] files = {
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[0])
        };

        // Act & Assert
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> service.uploadAndValidate(files)
        );

        assertTrue(exception.getMessage().contains(".shp"));
    }

    @Test
    @DisplayName("Should reject upload with missing .shx file")
    void testUploadWithMissingShxFile() {
        // Arrange
        MultipartFile[] files = {
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[0])
        };

        // Act & Assert
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> service.uploadAndValidate(files)
        );

        assertTrue(exception.getMessage().contains(".shx"));
    }

    @Test
    @DisplayName("Should reject upload with missing .dbf file")
    void testUploadWithMissingDbfFile() {
        // Arrange
        MultipartFile[] files = {
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[0])
        };

        // Act & Assert
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> service.uploadAndValidate(files)
        );

        assertTrue(exception.getMessage().contains(".dbf"));
    }

    @Test
    @DisplayName("Should reject upload with missing .prj file")
    void testUploadWithMissingPrjFile() {
        // Arrange
        MultipartFile[] files = {
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[0]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[0])
        };

        // Act & Assert
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> service.uploadAndValidate(files)
        );

        assertTrue(exception.getMessage().contains(".prj"));
    }

    @Test
    @DisplayName("Should accept upload with all required files")
    void testUploadWithAllRequiredFiles() throws IOException {
        // Arrange
        MultipartFile[] files = {
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[100]),
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[50]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[200]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[30])
        };

        Shapefile mockShapefile = Shapefile.builder()
            .id(UUID.randomUUID())
            .filename("test")
            .status("uploaded")
            .build();

        when(shapefileRepository.save(any(Shapefile.class))).thenReturn(mockShapefile);

        // Act
        UploadResponse response = service.uploadAndValidate(files);

        // Assert
        assertNotNull(response);
        assertEquals("uploaded", response.getStatus());
        assertEquals("test", response.getFilename());
        assertNotNull(response.getShapefileId());
    }

    @Test
    @DisplayName("Should handle case-insensitive file extensions")
    void testUploadWithMixedCaseExtensions() throws IOException {
        // Arrange
        MultipartFile[] files = {
            new MockMultipartFile("file", "test.SHP", "application/octet-stream", new byte[100]),
            new MockMultipartFile("file", "test.SHX", "application/octet-stream", new byte[50]),
            new MockMultipartFile("file", "test.DBF", "application/octet-stream", new byte[200]),
            new MockMultipartFile("file", "test.PRJ", "application/octet-stream", new byte[30])
        };

        Shapefile mockShapefile = Shapefile.builder()
            .id(UUID.randomUUID())
            .filename("test")
            .status("uploaded")
            .build();

        when(shapefileRepository.save(any(Shapefile.class))).thenReturn(mockShapefile);

        // Act
        UploadResponse response = service.uploadAndValidate(files);

        // Assert
        assertNotNull(response);
        assertEquals("uploaded", response.getStatus());
    }

    @Test
    @DisplayName("Should retrieve shapefile by ID")
    void testGetShapefileById() {
        // Arrange
        UUID shapefileId = UUID.randomUUID();
        Shapefile mockShapefile = Shapefile.builder()
            .id(shapefileId)
            .filename("test")
            .status("uploaded")
            .build();

        when(shapefileRepository.findById(shapefileId)).thenReturn(Optional.of(mockShapefile));

        // Act
        Shapefile result = service.getShapefileById(shapefileId);

        // Assert
        assertNotNull(result);
        assertEquals(shapefileId, result.getId());
        assertEquals("test", result.getFilename());
    }

    @Test
    @DisplayName("Should throw exception when shapefile not found")
    void testGetShapefileByIdNotFound() {
        // Arrange
        UUID shapefileId = UUID.randomUUID();
        when(shapefileRepository.findById(shapefileId)).thenReturn(Optional.empty());

        // Act & Assert
        IllegalArgumentException exception = assertThrows(
            IllegalArgumentException.class,
            () -> service.getShapefileById(shapefileId)
        );

        assertTrue(exception.getMessage().contains("not found"));
    }
}
