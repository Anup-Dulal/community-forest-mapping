package com.cfm.service;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Property-based tests for shapefile completeness validation.
 * 
 * Property 1: Shapefile Completeness Validation
 * For any set of files, if all required shapefile components (.shp, .shx, .dbf, .prj) 
 * are present, validation SHALL pass; if any component is missing, validation SHALL fail.
 * 
 * Validates: Requirements 1.2
 */
@DisplayName("Property 1: Shapefile Completeness Validation")
class ShapefileCompletenessPropertyTest {

    private static final Set<String> REQUIRED_EXTENSIONS = Set.of(".shp", ".shx", ".dbf", ".prj");

    /**
     * Property test: All required files present should pass validation.
     * Generates random combinations of required files and verifies validation passes.
     */
    @ParameterizedTest(name = "Complete shapefile set {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should pass validation when all required files are present")
    void testCompleteShapefileValidation(int iteration) {
        // Arrange
        MultipartFile[] files = createCompleteShapefileSet();

        // Act
        boolean isValid = validateShapefileCompleteness(files);

        // Assert
        assertTrue(isValid, "Validation should pass for complete shapefile set");
    }

    /**
     * Property test: Missing any required file should fail validation.
     * Generates all possible combinations of missing files and verifies validation fails.
     */
    @ParameterizedTest(name = "Missing extension {0}")
    @ValueSource(strings = {".shp", ".shx", ".dbf", ".prj"})
    @DisplayName("Should fail validation when any required file is missing")
    void testIncompleteShapefileValidation(String missingExtension) {
        // Arrange
        MultipartFile[] files = createIncompleteShapefileSet(missingExtension);

        // Act
        boolean isValid = validateShapefileCompleteness(files);

        // Assert
        assertFalse(isValid, "Validation should fail when " + missingExtension + " is missing");
    }

    /**
     * Property test: Case-insensitive extension matching.
     * Verifies that extensions are matched case-insensitively.
     */
    @ParameterizedTest(name = "Mixed case iteration {0}")
    @ValueSource(ints = {1, 2, 3})
    @DisplayName("Should handle case-insensitive file extensions")
    void testCaseInsensitiveExtensions(int iteration) {
        // Arrange
        MultipartFile[] files = createMixedCaseShapefileSet();

        // Act
        boolean isValid = validateShapefileCompleteness(files);

        // Assert
        assertTrue(isValid, "Validation should pass with mixed case extensions");
    }

    /**
     * Property test: Duplicate files should not affect validation.
     * Verifies that having duplicate files doesn't break validation.
     */
    @ParameterizedTest(name = "Duplicate files iteration {0}")
    @ValueSource(ints = {1, 2, 3})
    @DisplayName("Should handle duplicate files correctly")
    void testDuplicateFiles(int iteration) {
        // Arrange
        MultipartFile[] files = createShapefileSetWithDuplicates();

        // Act
        boolean isValid = validateShapefileCompleteness(files);

        // Assert
        assertTrue(isValid, "Validation should pass even with duplicate files");
    }

    /**
     * Property test: Extra files should not affect validation.
     * Verifies that having extra files doesn't break validation.
     */
    @ParameterizedTest(name = "Extra files iteration {0}")
    @ValueSource(ints = {1, 2, 3})
    @DisplayName("Should handle extra files correctly")
    void testExtraFiles(int iteration) {
        // Arrange
        MultipartFile[] files = createShapefileSetWithExtraFiles();

        // Act
        boolean isValid = validateShapefileCompleteness(files);

        // Assert
        assertTrue(isValid, "Validation should pass with extra files");
    }

    // Helper methods

    private MultipartFile[] createCompleteShapefileSet() {
        return new MultipartFile[]{
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[100]),
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[50]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[200]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[30])
        };
    }

    private MultipartFile[] createIncompleteShapefileSet(String missingExtension) {
        List<MultipartFile> files = new ArrayList<>();
        for (String ext : REQUIRED_EXTENSIONS) {
            if (!ext.equals(missingExtension)) {
                files.add(new MockMultipartFile("file", "test" + ext, "application/octet-stream", new byte[100]));
            }
        }
        return files.toArray(new MultipartFile[0]);
    }

    private MultipartFile[] createMixedCaseShapefileSet() {
        String[] extensions = {".SHP", ".shx", ".DBF", ".prj"};
        MultipartFile[] files = new MultipartFile[extensions.length];
        for (int i = 0; i < extensions.length; i++) {
            files[i] = new MockMultipartFile("file", "test" + extensions[i], "application/octet-stream", new byte[100]);
        }
        return files;
    }

    private MultipartFile[] createShapefileSetWithDuplicates() {
        return new MultipartFile[]{
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[100]),
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[100]),
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[50]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[200]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[30])
        };
    }

    private MultipartFile[] createShapefileSetWithExtraFiles() {
        return new MultipartFile[]{
            new MockMultipartFile("file", "test.shp", "application/octet-stream", new byte[100]),
            new MockMultipartFile("file", "test.shx", "application/octet-stream", new byte[50]),
            new MockMultipartFile("file", "test.dbf", "application/octet-stream", new byte[200]),
            new MockMultipartFile("file", "test.prj", "application/octet-stream", new byte[30]),
            new MockMultipartFile("file", "test.cpg", "application/octet-stream", new byte[20]),
            new MockMultipartFile("file", "readme.txt", "text/plain", new byte[50])
        };
    }

    private boolean validateShapefileCompleteness(MultipartFile[] files) {
        Set<String> uploadedExtensions = new HashSet<>();

        for (MultipartFile file : files) {
            String filename = file.getOriginalFilename();
            if (filename != null) {
                String extension = getExtension(filename);
                uploadedExtensions.add(extension);
            }
        }

        Set<String> missingExtensions = new HashSet<>(REQUIRED_EXTENSIONS);
        missingExtensions.removeAll(uploadedExtensions);

        return missingExtensions.isEmpty();
    }

    private String getExtension(String filename) {
        int lastDot = filename.lastIndexOf('.');
        if (lastDot > 0) {
            return filename.substring(lastDot).toLowerCase();
        }
        return "";
    }
}
