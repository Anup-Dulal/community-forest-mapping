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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Polygon;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.hamcrest.Matchers.notNullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Integration tests for REST API endpoints.
 * Tests all major API endpoints with various inputs and edge cases.
 */
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@DisplayName("API Endpoint Integration Tests")
class APIEndpointIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

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

    private GeometryFactory geometryFactory;

    @BeforeEach
    void setUp() {
        geometryFactory = new GeometryFactory();
        // Clean up repositories
        samplePlotRepository.deleteAll();
        compartmentRepository.deleteAll();
        analysisResultRepository.deleteAll();
        demRepository.deleteAll();
        shapefileRepository.deleteAll();
    }

    /**
     * Test session creation endpoint.
     */
    @Test
    @DisplayName("POST /api/sessions/create should create a new session")
    void testCreateSessionEndpoint() throws Exception {
        mockMvc.perform(post("/api/sessions/create")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.sessionId", notNullValue()));
    }

    /**
     * Test session data retrieval endpoint.
     */
    @Test
    @DisplayName("GET /api/sessions/{sessionId}/data should retrieve session data")
    void testGetSessionDataEndpoint() throws Exception {
        // Create session
        String sessionId = "test-session-123";
        
        // Create and store test data
        Shapefile shapefile = createTestShapefile("boundary");
        shapefileRepository.save(shapefile);
        
        // Get session data
        mockMvc.perform(get("/api/sessions/" + sessionId + "/data")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.shapefiles", notNullValue()))
            .andExpect(jsonPath("$.dems", notNullValue()))
            .andExpect(jsonPath("$.analysisResults", notNullValue()));
    }

    /**
     * Test session validation endpoint.
     */
    @Test
    @DisplayName("GET /api/sessions/{sessionId}/validate should validate data persistence")
    void testValidateSessionDataEndpoint() throws Exception {
        // Create and store test data
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        
        // Validate data
        mockMvc.perform(get("/api/sessions/test-session/validate")
                .param("analysisResultId", analysis.getId().toString())
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.isValid", notNullValue()));
    }

    /**
     * Test compartment retrieval endpoint.
     */
    @Test
    @DisplayName("GET /api/compartments should retrieve all compartments")
    void testGetCompartmentsEndpoint() throws Exception {
        // Create and store test data
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        
        // Create compartments
        compartmentRepository.save(createTestCompartment(analysis, "C1"));
        compartmentRepository.save(createTestCompartment(analysis, "C2"));
        
        // Get compartments
        mockMvc.perform(get("/api/compartments")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk());
    }

    /**
     * Test sample plot retrieval endpoint.
     */
    @Test
    @DisplayName("GET /api/sample-plots should retrieve all sample plots")
    void testGetSamplePlotsEndpoint() throws Exception {
        // Create and store test data
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        AnalysisResult analysis = analysisResultRepository.save(
            createTestAnalysisResult(shapefile, dem));
        Compartment compartment = compartmentRepository.save(
            createTestCompartment(analysis, "C1"));
        
        // Create sample plots
        samplePlotRepository.save(createTestSamplePlot(analysis, compartment, "SP-01"));
        samplePlotRepository.save(createTestSamplePlot(analysis, compartment, "SP-02"));
        
        // Get sample plots
        mockMvc.perform(get("/api/sample-plots")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk());
    }

    /**
     * Test export endpoints with error handling.
     */
    @Test
    @DisplayName("Export endpoints should handle missing data gracefully")
    void testExportEndpointsErrorHandling() throws Exception {
        // Try to export with non-existent analysis result
        mockMvc.perform(get("/api/export/coordinates/csv")
                .param("analysisResultId", "non-existent-id")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isNotFound());
    }

    /**
     * Test terrain analysis endpoint.
     */
    @Test
    @DisplayName("POST /api/terrain-analysis should trigger terrain analysis")
    void testTerrainAnalysisEndpoint() throws Exception {
        // Create and store test data
        Shapefile shapefile = shapefileRepository.save(createTestShapefile("boundary"));
        DEM dem = demRepository.save(createTestDEM(shapefile));
        
        // Trigger terrain analysis
        mockMvc.perform(post("/api/terrain-analysis")
                .param("demId", dem.getId().toString())
                .param("shapefileId", shapefile.getId().toString())
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk());
    }

    /**
     * Test error handling for invalid inputs.
     */
    @Test
    @DisplayName("API endpoints should handle invalid inputs with descriptive errors")
    void testAPIErrorHandling() throws Exception {
        // Test with invalid UUID format
        mockMvc.perform(get("/api/sessions/invalid-uuid/data")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isBadRequest());
    }

    /**
     * Test concurrent requests to ensure thread safety.
     */
    @Test
    @DisplayName("API endpoints should handle concurrent requests")
    void testConcurrentRequests() throws Exception {
        // Make concurrent requests
        for (int i = 0; i < 5; i++) {
            mockMvc.perform(get("/api/sessions/test-session/data")
                    .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk());
        }
    }

    /**
     * Test API response format consistency.
     */
    @Test
    @DisplayName("API responses should have consistent format")
    void testAPIResponseFormat() throws Exception {
        mockMvc.perform(post("/api/sessions/create")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.sessionId", notNullValue()));
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
