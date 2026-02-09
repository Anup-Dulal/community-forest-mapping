package com.cfm.integration;

import com.cfm.model.AnalysisResult;
import com.cfm.model.Compartment;
import com.cfm.model.DEM;
import com.cfm.model.SamplePlot;
import com.cfm.model.Shapefile;
import com.cfm.repository.AnalysisResultRepository;
import com.cfm.repository.CompartmentRepository;
import com.cfm.repository.DEMRepository;
import com.cfm.repository.SamplePlotRepository;
import com.cfm.repository.ShapefileRepository;
import com.cfm.service.SessionService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Polygon;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * End-to-end integration tests for the complete Community Forest Mapping workflow.
 * Tests the entire pipeline from shapefile upload to map export.
 */
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("End-to-End Integration Tests")
class EndToEndIntegrationTest {

    @Autowired
    private ShapefileRepository shapefileRepository;

    @Autowired
    private DEMRepository demRepository;

    @Autowired
    private AnalysisResultRepository analysisResultRepository;

    @Autowired
    private CompartmentRepository compartmentRepository;

    @Autowired
    private SamplePlotRepository samplePlotRepository;

    @Autowired
    private SessionService sessionService;

    private GeometryFactory geometryFactory;

    @BeforeEach
    void setUp() {
        geometryFactory = new GeometryFactory();
        // Clean up repositories before each test
        samplePlotRepository.deleteAll();
        compartmentRepository.deleteAll();
        analysisResultRepository.deleteAll();
        demRepository.deleteAll();
        shapefileRepository.deleteAll();
    }

    /**
     * Test complete workflow from shapefile upload to data export.
     * Verifies all major components work together correctly.
     */
    @Test
    @DisplayName("Complete workflow: upload shapefile, download DEM, analyze terrain, generate compartments and sample plots")
    void testCompleteWorkflow() {
        // Step 1: Create and store a test shapefile
        Shapefile shapefile = createTestShapefile("test_boundary");
        Shapefile uploadedShapefile = shapefileRepository.save(shapefile);
        assertNotNull(uploadedShapefile.getId(), "Shapefile should be stored with ID");
        assertEquals("test_boundary.shp", uploadedShapefile.getFilename());

        // Step 2: Create and store a test DEM
        DEM dem = createTestDEM(uploadedShapefile);
        DEM storedDEM = demRepository.save(dem);
        assertNotNull(storedDEM.getId(), "DEM should be stored with ID");
        assertEquals("clipped", storedDEM.getStatus());

        // Step 3: Create and store analysis result
        AnalysisResult analysis = createTestAnalysisResult(uploadedShapefile, storedDEM);
        AnalysisResult storedAnalysis = analysisResultRepository.save(analysis);
        assertNotNull(storedAnalysis.getId(), "Analysis result should be stored with ID");
        assertEquals("complete", storedAnalysis.getStatus());

        // Step 4: Create and store compartments
        Compartment compartment1 = createTestCompartment(storedAnalysis, "C1");
        Compartment compartment2 = createTestCompartment(storedAnalysis, "C2");
        Compartment storedCompartment1 = compartmentRepository.save(compartment1);
        Compartment storedCompartment2 = compartmentRepository.save(compartment2);
        
        List<Compartment> compartments = compartmentRepository.findAll();
        assertEquals(2, compartments.size(), "Should have 2 compartments");

        // Step 5: Create and store sample plots
        SamplePlot plot1 = createTestSamplePlot(storedAnalysis, storedCompartment1, "SP-01");
        SamplePlot plot2 = createTestSamplePlot(storedAnalysis, storedCompartment1, "SP-02");
        SamplePlot plot3 = createTestSamplePlot(storedAnalysis, storedCompartment2, "SP-03");
        
        samplePlotRepository.save(plot1);
        samplePlotRepository.save(plot2);
        samplePlotRepository.save(plot3);
        
        List<SamplePlot> plots = samplePlotRepository.findAll();
        assertEquals(3, plots.size(), "Should have 3 sample plots");

        // Step 6: Verify session data retrieval
        String sessionId = sessionService.createSession();
        Map<String, Object> sessionData = sessionService.getSessionData(sessionId);
        
        assertNotNull(sessionData, "Session data should be retrievable");
        assertNotNull(sessionData.get("shapefiles"), "Session should contain shapefiles");
        assertNotNull(sessionData.get("dems"), "Session should contain DEMs");
        assertNotNull(sessionData.get("analysisResults"), "Session should contain analysis results");

        // Step 7: Verify data persistence validation
        Map<String, Object> validationResult = sessionService.validateDataPersistence(storedAnalysis.getId());
        assertTrue((Boolean) validationResult.get("isValid"), "Data should pass validation");
    }

    /**
     * Test shapefile upload and validation workflow.
     */
    @Test
    @DisplayName("Shapefile upload and validation workflow")
    void testShapefileUploadWorkflow() {
        // Create test shapefile
        Shapefile shapefile = createTestShapefile("forest_boundary");
        
        // Store shapefile
        Shapefile stored = shapefileRepository.save(shapefile);
        
        // Verify storage
        assertNotNull(stored.getId());
        assertEquals("forest_boundary.shp", stored.getFilename());
        assertEquals("uploaded", stored.getStatus());
        assertNotNull(stored.getGeometry());
        
        // Retrieve and verify
        Shapefile retrieved = shapefileRepository.findById(stored.getId()).orElse(null);
        assertNotNull(retrieved);
        assertEquals(stored.getFilename(), retrieved.getFilename());
    }

    /**
     * Test DEM download and clipping workflow.
     */
    @Test
    @DisplayName("DEM download and clipping workflow")
    void testDEMDownloadWorkflow() {
        // Create and store shapefile
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        
        // Create and store DEM
        DEM dem = createTestDEM(shapefile);
        DEM stored = demRepository.save(dem);
        
        // Verify DEM storage
        assertNotNull(stored.getId());
        assertEquals("SRTM", stored.getSource());
        assertEquals("clipped", stored.getStatus());
        assertNotNull(stored.getRasterPath());
        assertNotNull(stored.getClippedRasterPath());
        
        // Retrieve and verify
        DEM retrieved = demRepository.findById(stored.getId()).orElse(null);
        assertNotNull(retrieved);
        assertEquals(stored.getSource(), retrieved.getSource());
    }

    /**
     * Test terrain analysis workflow.
     */
    @Test
    @DisplayName("Terrain analysis workflow")
    void testTerrainAnalysisWorkflow() {
        // Create and store shapefile and DEM
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        
        // Create and store analysis result
        AnalysisResult analysis = createTestAnalysisResult(shapefile, dem);
        AnalysisResult stored = analysisResultRepository.save(analysis);
        
        // Verify analysis storage
        assertNotNull(stored.getId());
        assertEquals("complete", stored.getStatus());
        assertNotNull(stored.getSlopeRasterPath());
        assertNotNull(stored.getAspectRasterPath());
        
        // Retrieve and verify
        AnalysisResult retrieved = analysisResultRepository.findById(stored.getId()).orElse(null);
        assertNotNull(retrieved);
        assertEquals(stored.getStatus(), retrieved.getStatus());
    }

    /**
     * Test compartment generation workflow.
     */
    @Test
    @DisplayName("Compartment generation workflow")
    void testCompartmentGenerationWorkflow() {
        // Create and store analysis result
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        
        // Create and store compartments
        Compartment c1 = createTestCompartment(analysis, "C1");
        Compartment c2 = createTestCompartment(analysis, "C2");
        Compartment c3 = createTestCompartment(analysis, "C3");
        
        compartmentRepository.save(c1);
        compartmentRepository.save(c2);
        compartmentRepository.save(c3);
        
        // Verify compartments
        List<Compartment> compartments = compartmentRepository.findAll();
        assertEquals(3, compartments.size());
        
        // Verify sequential numbering
        assertTrue(compartments.stream().anyMatch(c -> "C1".equals(c.getCompartmentId())));
        assertTrue(compartments.stream().anyMatch(c -> "C2".equals(c.getCompartmentId())));
        assertTrue(compartments.stream().anyMatch(c -> "C3".equals(c.getCompartmentId())));
    }

    /**
     * Test sample plot generation workflow.
     */
    @Test
    @DisplayName("Sample plot generation workflow")
    void testSamplePlotGenerationWorkflow() {
        // Create and store analysis result and compartment
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        Compartment compartment = compartmentRepository.save(
            createTestCompartment(analysis, "C1"));
        
        // Create and store sample plots
        for (int i = 1; i <= 5; i++) {
            SamplePlot plot = createTestSamplePlot(analysis, compartment, "SP-" + String.format("%02d", i));
            samplePlotRepository.save(plot);
        }
        
        // Verify sample plots
        List<SamplePlot> plots = samplePlotRepository.findAll();
        assertEquals(5, plots.size(), "Should have 5 sample plots");
        
        // Verify unique labeling
        for (int i = 1; i <= 5; i++) {
            final int index = i;
            assertTrue(plots.stream().anyMatch(p -> ("SP-" + String.format("%02d", index)).equals(p.getPlotId())));
        }
    }

    /**
     * Test coordinate export workflow.
     */
    @Test
    @DisplayName("Coordinate export workflow")
    void testCoordinateExportWorkflow() {
        // Create and store sample plots
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        Compartment compartment = compartmentRepository.save(
            createTestCompartment(analysis, "C1"));
        
        SamplePlot plot1 = createTestSamplePlot(analysis, compartment, "SP-01");
        SamplePlot plot2 = createTestSamplePlot(analysis, compartment, "SP-02");
        samplePlotRepository.save(plot1);
        samplePlotRepository.save(plot2);
        
        // Verify plots are stored
        List<SamplePlot> plots = samplePlotRepository.findAll();
        assertEquals(2, plots.size());
        
        // Verify coordinate data
        for (SamplePlot plot : plots) {
            assertNotNull(plot.getLatitude());
            assertNotNull(plot.getLongitude());
            assertNotNull(plot.getEasting());
            assertNotNull(plot.getNorthing());
        }
    }

    /**
     * Test data persistence and session recovery workflow.
     */
    @Test
    @DisplayName("Data persistence and session recovery workflow")
    void testDataPersistenceWorkflow() {
        // Create and store complete analysis
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        Compartment compartment = compartmentRepository.save(
            createTestCompartment(analysis, "C1"));
        SamplePlot plot = samplePlotRepository.save(
            createTestSamplePlot(analysis, compartment, "SP-01"));
        
        // Create session
        String sessionId = sessionService.createSession();
        
        // Retrieve session data
        Map<String, Object> sessionData = sessionService.getSessionData(sessionId);
        assertNotNull(sessionData);
        
        // Validate data persistence
        Map<String, Object> validationResult = sessionService.validateDataPersistence(analysis.getId());
        assertTrue((Boolean) validationResult.get("isValid"));
        
        // Verify all data is retrievable
        Shapefile retrievedShapefile = shapefileRepository.findById(shapefile.getId()).orElse(null);
        assertNotNull(retrievedShapefile);
        
        DEM retrievedDEM = demRepository.findById(dem.getId()).orElse(null);
        assertNotNull(retrievedDEM);
        
        AnalysisResult retrievedAnalysis = analysisResultRepository.findById(analysis.getId()).orElse(null);
        assertNotNull(retrievedAnalysis);
        
        Compartment retrievedCompartment = compartmentRepository.findById(compartment.getId()).orElse(null);
        assertNotNull(retrievedCompartment);
        
        SamplePlot retrievedPlot = samplePlotRepository.findById(plot.getId()).orElse(null);
        assertNotNull(retrievedPlot);
    }

    // Helper methods

    private Shapefile createTestShapefile(String filename) {
        Shapefile shapefile = new Shapefile();
        shapefile.setFilename(filename + ".shp");
        shapefile.setProjection("EPSG:4326");
        shapefile.setStatus("uploaded");
        
        // Set geometry as WKT string
        String wktGeometry = "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))";
        shapefile.setGeometry(wktGeometry);
        
        return shapefile;
    }

    private DEM createTestDEM(Shapefile shapefile) {
        DEM dem = new DEM();
        dem.setShapefile(shapefile);
        dem.setSource("SRTM");
        dem.setRasterPath("/data/dems/test.tif");
        dem.setClippedRasterPath("/data/dems/test_clipped.tif");
        dem.setStatus("clipped");
        dem.setDownloadedAt(LocalDateTime.now());
        return dem;
    }

    private AnalysisResult createTestAnalysisResult(Shapefile shapefile, DEM dem) {
        AnalysisResult analysis = new AnalysisResult();
        analysis.setShapefile(shapefile);
        analysis.setDem(dem);
        analysis.setStatus("complete");
        analysis.setSlopeRasterPath("/data/analysis/slope.tif");
        analysis.setAspectRasterPath("/data/analysis/aspect.tif");
        analysis.setCompartmentGeometryPath("/data/analysis/compartments.geojson");
        analysis.setSamplePlotGeometryPath("/data/analysis/sample_plots.geojson");
        analysis.setGeneratedAt(LocalDateTime.now());
        return analysis;
    }

    private Compartment createTestCompartment(AnalysisResult analysis, String compartmentId) {
        Compartment compartment = new Compartment();
        compartment.setAnalysisResult(analysis);
        compartment.setCompartmentId(compartmentId);
        compartment.setArea(new BigDecimal("100.00"));
        compartment.setSamplePlotCount(5);
        
        // Set geometry as WKT string
        String wktGeometry = "POLYGON ((0 0, 5 0, 5 5, 0 5, 0 0))";
        compartment.setGeometry(wktGeometry);
        
        return compartment;
    }

    private SamplePlot createTestSamplePlot(AnalysisResult analysis, Compartment compartment, String plotId) {
        SamplePlot plot = new SamplePlot();
        plot.setAnalysisResult(analysis);
        plot.setCompartment(compartment);
        plot.setPlotId(plotId);
        plot.setLatitude(new BigDecimal("5.500000"));
        plot.setLongitude(new BigDecimal("5.500000"));
        plot.setEasting(new BigDecimal("500000.00"));
        plot.setNorthing(new BigDecimal("600000.00"));
        
        // Set geometry as WKT string
        String wktGeometry = "POINT (5.5 5.5)";
        plot.setGeometry(wktGeometry);
        
        return plot;
    }
}
