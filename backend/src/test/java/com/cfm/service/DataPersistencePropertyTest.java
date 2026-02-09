package com.cfm.service;

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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;
import org.locationtech.jts.geom.Polygon;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Property-based tests for data persistence round trip validation.
 * 
 * Property 18: Data Persistence Round Trip
 * For any uploaded shapefile or generated analysis result, storing it in persistent storage 
 * and then retrieving it SHALL produce data equivalent to the original.
 * 
 * Validates: Requirements 11.1, 11.2, 11.3, 11.4
 */
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("Property 18: Data Persistence Round Trip")
class DataPersistencePropertyTest {

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
     * Property test: Shapefile persistence round trip.
     * Store a shapefile and retrieve it, verifying all data is preserved.
     */
    @ParameterizedTest(name = "Shapefile persistence iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should persist and retrieve shapefile data without loss")
    void testShapefilePersistenceRoundTrip(int iteration) {
        // Arrange
        Shapefile originalShapefile = createTestShapefile("test_boundary_" + iteration);
        
        // Act - Store
        Shapefile storedShapefile = shapefileRepository.save(originalShapefile);
        
        // Act - Retrieve
        Shapefile retrievedShapefile = shapefileRepository.findById(storedShapefile.getId()).orElse(null);
        
        // Assert
        assertNotNull(retrievedShapefile, "Shapefile should be retrievable from storage");
        assertEquals(originalShapefile.getFilename(), retrievedShapefile.getFilename(), 
            "Filename should be preserved");
        assertNotNull(retrievedShapefile.getGeometry(), 
            "Boundary geometry should be preserved");
        assertEquals(originalShapefile.getProjection(), retrievedShapefile.getProjection(), 
            "Projection should be preserved");
        assertEquals(originalShapefile.getStatus(), retrievedShapefile.getStatus(), 
            "Status should be preserved");
    }

    /**
     * Property test: DEM persistence round trip.
     * Store a DEM and retrieve it, verifying all data is preserved.
     */
    @ParameterizedTest(name = "DEM persistence iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should persist and retrieve DEM data without loss")
    void testDEMPersistenceRoundTrip(int iteration) {
        // Arrange
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary_" + iteration));
        DEM originalDEM = createTestDEM(shapefile, "dem_" + iteration);
        
        // Act - Store
        DEM storedDEM = demRepository.save(originalDEM);
        
        // Act - Retrieve
        DEM retrievedDEM = demRepository.findById(storedDEM.getId()).orElse(null);
        
        // Assert
        assertNotNull(retrievedDEM, "DEM should be retrievable from storage");
        assertEquals(originalDEM.getSource(), retrievedDEM.getSource(), 
            "Source should be preserved");
        assertEquals(originalDEM.getRasterPath(), retrievedDEM.getRasterPath(), 
            "Raster path should be preserved");
        assertEquals(originalDEM.getStatus(), retrievedDEM.getStatus(), 
            "Status should be preserved");
    }

    /**
     * Property test: Analysis result persistence round trip.
     * Store analysis results and retrieve them, verifying all data is preserved.
     */
    @ParameterizedTest(name = "Analysis result persistence iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should persist and retrieve analysis results without loss")
    void testAnalysisResultPersistenceRoundTrip(int iteration) {
        // Arrange
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary_" + iteration));
        DEM dem = demRepository.save(createTestDEM(shapefile, "dem_" + iteration));
        AnalysisResult originalAnalysis = createTestAnalysisResult(shapefile, dem, iteration);
        
        // Act - Store
        AnalysisResult storedAnalysis = analysisResultRepository.save(originalAnalysis);
        
        // Act - Retrieve
        AnalysisResult retrievedAnalysis = analysisResultRepository.findById(storedAnalysis.getId()).orElse(null);
        
        // Assert
        assertNotNull(retrievedAnalysis, "Analysis result should be retrievable from storage");
        assertEquals(originalAnalysis.getStatus(), retrievedAnalysis.getStatus(), 
            "Status should be preserved");
        assertNotNull(retrievedAnalysis.getShapefile(), 
            "Associated shapefile reference should be preserved");
        assertNotNull(retrievedAnalysis.getDem(), 
            "Associated DEM reference should be preserved");
    }

    /**
     * Property test: Compartment persistence round trip.
     * Store compartments and retrieve them, verifying all data is preserved.
     */
    @ParameterizedTest(name = "Compartment persistence iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should persist and retrieve compartment data without loss")
    void testCompartmentPersistenceRoundTrip(int iteration) {
        // Arrange
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary_" + iteration));
        DEM dem = demRepository.save(createTestDEM(shapefile, "dem_" + iteration));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem, iteration));
        Compartment originalCompartment = createTestCompartment(analysis, "C" + iteration);
        
        // Act - Store
        Compartment storedCompartment = compartmentRepository.save(originalCompartment);
        
        // Act - Retrieve
        Compartment retrievedCompartment = compartmentRepository.findById(storedCompartment.getId()).orElse(null);
        
        // Assert
        assertNotNull(retrievedCompartment, "Compartment should be retrievable from storage");
        assertEquals(originalCompartment.getCompartmentId(), retrievedCompartment.getCompartmentId(), 
            "Compartment ID should be preserved");
        assertEquals(originalCompartment.getArea(), retrievedCompartment.getArea(), 
            "Area should be preserved");
        assertNotNull(retrievedCompartment.getGeometry(), 
            "Geometry should be preserved");
    }

    /**
     * Property test: Sample plot persistence round trip.
     * Store sample plots and retrieve them, verifying all data is preserved.
     */
    @ParameterizedTest(name = "Sample plot persistence iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should persist and retrieve sample plot data without loss")
    void testSamplePlotPersistenceRoundTrip(int iteration) {
        // Arrange
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary_" + iteration));
        DEM dem = demRepository.save(createTestDEM(shapefile, "dem_" + iteration));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem, iteration));
        Compartment compartment = compartmentRepository.save(
            createTestCompartment(analysis, "C" + iteration));
        SamplePlot originalPlot = createTestSamplePlot(analysis, compartment, "SP-" + String.format("%02d", iteration));
        
        // Act - Store
        SamplePlot storedPlot = samplePlotRepository.save(originalPlot);
        
        // Act - Retrieve
        SamplePlot retrievedPlot = samplePlotRepository.findById(storedPlot.getId()).orElse(null);
        
        // Assert
        assertNotNull(retrievedPlot, "Sample plot should be retrievable from storage");
        assertEquals(originalPlot.getPlotId(), retrievedPlot.getPlotId(), 
            "Plot ID should be preserved");
        assertEquals(originalPlot.getLatitude(), retrievedPlot.getLatitude(), 
            "Latitude should be preserved");
        assertEquals(originalPlot.getLongitude(), retrievedPlot.getLongitude(), 
            "Longitude should be preserved");
        assertEquals(originalPlot.getEasting(), retrievedPlot.getEasting(), 
            "Easting should be preserved");
        assertEquals(originalPlot.getNorthing(), retrievedPlot.getNorthing(), 
            "Northing should be preserved");
    }

    /**
     * Property test: Session data persistence round trip.
     * Create a session, store data, and retrieve it, verifying all data is preserved.
     */
    @ParameterizedTest(name = "Session data persistence iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should persist and retrieve session data without loss")
    void testSessionDataPersistenceRoundTrip(int iteration) {
        // Arrange
        String sessionId = sessionService.createSession();
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary_" + iteration));
        DEM dem = demRepository.save(createTestDEM(shapefile, "dem_" + iteration));
        analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem, iteration));
        
        // Act - Retrieve session data
        Map<String, Object> sessionData = sessionService.getSessionData(sessionId);
        
        // Assert
        assertNotNull(sessionData, "Session data should be retrievable");
        assertNotNull(sessionData.get("shapefiles"), "Shapefiles should be in session data");
        assertNotNull(sessionData.get("dems"), "DEMs should be in session data");
        assertNotNull(sessionData.get("analysisResults"), "Analysis results should be in session data");
        
        // Verify data integrity
        @SuppressWarnings("unchecked")
        List<Shapefile> shapefiles = (List<Shapefile>) sessionData.get("shapefiles");
        @SuppressWarnings("unchecked")
        List<DEM> dems = (List<DEM>) sessionData.get("dems");
        @SuppressWarnings("unchecked")
        List<AnalysisResult> results = (List<AnalysisResult>) sessionData.get("analysisResults");
        
        assertTrue(shapefiles.size() > 0, "Session should contain stored shapefiles");
        assertTrue(dems.size() > 0, "Session should contain stored DEMs");
        assertTrue(results.size() > 0, "Session should contain stored analysis results");
    }

    /**
     * Property test: Data validation after persistence.
     * Store data and validate it using the validation method, verifying integrity.
     */
    @ParameterizedTest(name = "Data validation iteration {0}")
    @ValueSource(ints = {1, 2, 3, 4, 5})
    @DisplayName("Should validate data integrity after persistence")
    void testDataValidationAfterPersistence(int iteration) {
        // Arrange
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary_" + iteration));
        DEM dem = demRepository.save(createTestDEM(shapefile, "dem_" + iteration));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem, iteration));
        
        // Act
        Map<String, Object> validationResult = sessionService.validateDataPersistence(analysis.getId());
        
        // Assert
        assertNotNull(validationResult, "Validation result should not be null");
        assertTrue((Boolean) validationResult.get("isValid"), 
            "Stored data should pass validation");
        assertNotNull(validationResult.get("timestamp"), 
            "Validation timestamp should be present");
    }

    // Helper methods

    private Shapefile createTestShapefile(String filename) {
        Shapefile shapefile = new Shapefile();
        shapefile.setFilename(filename + ".shp");
        shapefile.setProjection("EPSG:4326");
        shapefile.setStatus("uploaded");
        
        // Create a simple polygon boundary
        // Set geometry as WKT string
        String wktGeometry = "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))";
        shapefile.setGeometry(wktGeometry);
        
        return shapefile;
    }

    private DEM createTestDEM(Shapefile shapefile, String name) {
        DEM dem = new DEM();
        dem.setShapefile(shapefile);
        dem.setSource("SRTM");
        dem.setRasterPath("/data/dems/" + name + ".tif");
        dem.setStatus("clipped");
        
        return dem;
    }

    private AnalysisResult createTestAnalysisResult(Shapefile shapefile, DEM dem, int iteration) {
        AnalysisResult analysis = new AnalysisResult();
        analysis.setShapefile(shapefile);
        analysis.setDem(dem);
        analysis.setStatus("complete");
        analysis.setSlopeRasterPath("/data/analysis/slope_" + iteration + ".tif");
        analysis.setAspectRasterPath("/data/analysis/aspect_" + iteration + ".tif");
        
        return analysis;
    }

    private Compartment createTestCompartment(AnalysisResult analysis, String compartmentId) {
        Compartment compartment = new Compartment();
        compartment.setAnalysisResult(analysis);
        compartment.setCompartmentId(compartmentId);
        compartment.setArea(new java.math.BigDecimal("100.00"));
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
        plot.setLatitude(new java.math.BigDecimal("5.500000"));
        plot.setLongitude(new java.math.BigDecimal("5.500000"));
        plot.setEasting(new java.math.BigDecimal("500000.00"));
        plot.setNorthing(new java.math.BigDecimal("600000.00"));
        
        // Set geometry as WKT string
        String wktGeometry = "POINT (5.5 5.5)";
        plot.setGeometry(wktGeometry);
        
        return plot;
    }
}
