package com.cfm.service;

import com.cfm.model.AnalysisResult;
import com.cfm.model.Compartment;
import com.cfm.model.SamplePlot;
import com.cfm.repository.SamplePlotRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.test.util.ReflectionTestUtils;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for CoordinateExportService.
 * Tests CSV and Excel export functionality.
 */
public class CoordinateExportServiceTest {

    @Mock
    private SamplePlotRepository samplePlotRepository;

    @InjectMocks
    private CoordinateExportService coordinateExportService;

    @TempDir
    Path tempDir;

    private UUID analysisResultId;
    private List<SamplePlot> testSamplePlots;

    @BeforeEach
    public void setUp() {
        MockitoAnnotations.openMocks(this);
        ReflectionTestUtils.setField(coordinateExportService, "exportDir", tempDir.toString());

        analysisResultId = UUID.randomUUID();
        testSamplePlots = createTestSamplePlots();
    }

    /**
     * Create test sample plots with realistic data.
     */
    private List<SamplePlot> createTestSamplePlots() {
        List<SamplePlot> plots = new ArrayList<>();

        for (int i = 1; i <= 10; i++) {
            AnalysisResult analysisResult = AnalysisResult.builder()
                    .id(analysisResultId)
                    .build();

            Compartment compartment = Compartment.builder()
                    .id(UUID.randomUUID())
                    .compartmentId("C" + ((i - 1) / 5 + 1))
                    .build();

            SamplePlot plot = SamplePlot.builder()
                    .id(UUID.randomUUID())
                    .analysisResult(analysisResult)
                    .compartment(compartment)
                    .plotId(String.format("SP-%02d", i))
                    .easting(new BigDecimal("500000.00").add(new BigDecimal(i * 100)))
                    .northing(new BigDecimal("5000000.00").add(new BigDecimal(i * 100)))
                    .latitude(new BigDecimal("45.5").add(new BigDecimal(i * 0.01)))
                    .longitude(new BigDecimal("-122.5").add(new BigDecimal(i * 0.01)))
                    .build();

            plots.add(plot);
        }

        return plots;
    }

    @Test
    public void testExportToCSV() throws IOException {
        // Arrange
        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(testSamplePlots);

        // Act
        String filepath = coordinateExportService.exportToCSV(analysisResultId);

        // Assert
        assertNotNull(filepath);
        assertTrue(new File(filepath).exists());

        // Verify CSV content
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String header = reader.readLine();
            assertNotNull(header);
            assertTrue(header.contains("Plot ID"));
            assertTrue(header.contains("Easting"));
            assertTrue(header.contains("Northing"));
            assertTrue(header.contains("Latitude"));
            assertTrue(header.contains("Longitude"));

            // Count data rows
            int rowCount = 0;
            String line;
            while ((line = reader.readLine()) != null) {
                rowCount++;
                assertTrue(line.contains("SP-"));
            }

            assertEquals(testSamplePlots.size(), rowCount);
        }
    }

    @Test
    public void testExportToExcel() throws IOException {
        // Arrange
        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(testSamplePlots);

        // Act
        String filepath = coordinateExportService.exportToExcel(analysisResultId);

        // Assert
        assertNotNull(filepath);
        assertTrue(new File(filepath).exists());
        assertTrue(filepath.endsWith(".xlsx"));
    }

    @Test
    public void testExportToCSVWithEmptyPlots() {
        // Arrange
        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(new ArrayList<>());

        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            coordinateExportService.exportToCSV(analysisResultId);
        });
    }

    @Test
    public void testExportToExcelWithEmptyPlots() {
        // Arrange
        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(new ArrayList<>());

        // Act & Assert
        assertThrows(IllegalArgumentException.class, () -> {
            coordinateExportService.exportToExcel(analysisResultId);
        });
    }

    @Test
    public void testGetExportStatistics() {
        // Arrange
        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(testSamplePlots);

        // Act
        Map<String, Object> stats = coordinateExportService.getExportStatistics(analysisResultId);

        // Assert
        assertNotNull(stats);
        assertEquals(testSamplePlots.size(), stats.get("totalPlots"));
        assertEquals(testSamplePlots.size(), stats.get("plotsWithUTM"));
        assertEquals(testSamplePlots.size(), stats.get("plotsWithLatLon"));

        @SuppressWarnings("unchecked")
        Map<String, Long> plotsByCompartment = (Map<String, Long>) stats.get("plotsByCompartment");
        assertNotNull(plotsByCompartment);
        assertEquals(2, plotsByCompartment.size());
    }

    @Test
    public void testCSVExportCompleteness() throws IOException {
        // Arrange
        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(testSamplePlots);

        // Act
        String filepath = coordinateExportService.exportToCSV(analysisResultId);

        // Assert - Property 14: Coordinate Export Completeness
        // For any set of sample plots, the exported coordinate table SHALL contain
        // all plots with complete information (Plot ID, Easting, Northing, Latitude, Longitude)

        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String line;
            int lineCount = 0;

            while ((line = reader.readLine()) != null) {
                if (lineCount == 0) {
                    // Skip header
                    lineCount++;
                    continue;
                }

                // Each data line should have 6 fields
                String[] fields = line.split(",");
                assertEquals(6, fields.length, "Each row should have 6 fields");

                // Verify no empty fields
                for (int i = 0; i < fields.length; i++) {
                    assertFalse(fields[i].trim().isEmpty(),
                            "Field " + i + " should not be empty in row: " + line);
                }

                lineCount++;
            }

            // Verify all plots are exported
            assertEquals(testSamplePlots.size() + 1, lineCount, "All plots should be exported");
        }
    }

    @Test
    public void testCSVEscaping() throws IOException {
        // Arrange
        AnalysisResult analysisResult = AnalysisResult.builder()
                .id(analysisResultId)
                .build();

        Compartment compartment = Compartment.builder()
                .id(UUID.randomUUID())
                .compartmentId("C1,Special")  // Contains comma
                .build();

        SamplePlot plot = SamplePlot.builder()
                .id(UUID.randomUUID())
                .analysisResult(analysisResult)
                .compartment(compartment)
                .plotId("SP-01")
                .easting(new BigDecimal("500000.00"))
                .northing(new BigDecimal("5000000.00"))
                .latitude(new BigDecimal("45.5"))
                .longitude(new BigDecimal("-122.5"))
                .build();

        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(Collections.singletonList(plot));

        // Act
        String filepath = coordinateExportService.exportToCSV(analysisResultId);

        // Assert
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            reader.readLine(); // Skip header
            String dataLine = reader.readLine();

            // Compartment ID with comma should be quoted
            assertTrue(dataLine.contains("\"C1,Special\""));
        }
    }

    @Test
    public void testExcelExportWithNullValues() throws IOException {
        // Arrange
        AnalysisResult analysisResult = AnalysisResult.builder()
                .id(analysisResultId)
                .build();

        Compartment compartment = Compartment.builder()
                .id(UUID.randomUUID())
                .compartmentId("C1")
                .build();

        SamplePlot plot = SamplePlot.builder()
                .id(UUID.randomUUID())
                .analysisResult(analysisResult)
                .compartment(compartment)
                .plotId("SP-01")
                .easting(null)  // Null value
                .northing(new BigDecimal("5000000.00"))
                .latitude(new BigDecimal("45.5"))
                .longitude(new BigDecimal("-122.5"))
                .build();

        when(samplePlotRepository.findByAnalysisResultId(analysisResultId))
                .thenReturn(Collections.singletonList(plot));

        // Act
        String filepath = coordinateExportService.exportToExcel(analysisResultId);

        // Assert
        assertNotNull(filepath);
        assertTrue(new File(filepath).exists());
    }
}
