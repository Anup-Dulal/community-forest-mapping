package com.cfm.service;

import com.cfm.model.SamplePlot;
import com.cfm.repository.SamplePlotRepository;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

/**
 * Service for exporting sample plot coordinates to CSV and Excel formats.
 * Generates coordinate tables with Plot ID, Easting, Northing, Latitude, Longitude.
 */
@Slf4j
@Service
public class CoordinateExportService {

    @Autowired
    private SamplePlotRepository samplePlotRepository;

    @Value("${export.dir:./exports}")
    private String exportDir;

    /**
     * Export sample plot coordinates to CSV format.
     *
     * @param analysisResultId ID of the analysis result
     * @return Path to the generated CSV file
     * @throws IOException if file writing fails
     */
    public String exportToCSV(UUID analysisResultId) throws IOException {
        try {
            // Retrieve sample plots
            List<SamplePlot> samplePlots = samplePlotRepository.findByAnalysisResultId(analysisResultId);

            if (samplePlots.isEmpty()) {
                throw new IllegalArgumentException("No sample plots found for analysis: " + analysisResultId);
            }

            // Create CSV file
            String filename = String.format("sample_plots_%s.csv", analysisResultId);
            Path filepath = Paths.get(exportDir, filename);

            // Ensure export directory exists
            Files.createDirectories(filepath.getParent());

            // Write CSV
            try (FileWriter writer = new FileWriter(filepath.toFile())) {
                // Write header
                writer.write("Plot ID,Compartment ID,Easting (m),Northing (m),Latitude,Longitude\n");

                // Write data rows
                for (SamplePlot plot : samplePlots) {
                    String row = String.format(
                            "%s,%s,%s,%s,%s,%s\n",
                            escapeCSV(plot.getPlotId()),
                            escapeCSV(plot.getCompartment().getCompartmentId()),
                            formatNumber(plot.getEasting()),
                            formatNumber(plot.getNorthing()),
                            formatNumber(plot.getLatitude()),
                            formatNumber(plot.getLongitude())
                    );
                    writer.write(row);
                }
            }

            log.info("CSV export created: {}", filepath);
            return filepath.toString();

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for CSV export: {}", e.getMessage());
            throw e;
        } catch (IOException e) {
            log.error("Error writing CSV file: {}", e.getMessage(), e);
            throw new IOException("Failed to export to CSV: " + e.getMessage(), e);
        } catch (Exception e) {
            log.error("Error exporting to CSV: {}", e.getMessage(), e);
            throw new IOException("Failed to export to CSV: " + e.getMessage(), e);
        }
    }

    /**
     * Export sample plot coordinates to Excel format.
     *
     * @param analysisResultId ID of the analysis result
     * @return Path to the generated Excel file
     * @throws IOException if file writing fails
     */
    public String exportToExcel(UUID analysisResultId) throws IOException {
        try {
            // Retrieve sample plots
            List<SamplePlot> samplePlots = samplePlotRepository.findByAnalysisResultId(analysisResultId);

            if (samplePlots.isEmpty()) {
                throw new IllegalArgumentException("No sample plots found for analysis: " + analysisResultId);
            }

            // Create Excel file
            String filename = String.format("sample_plots_%s.xlsx", analysisResultId);
            Path filepath = Paths.get(exportDir, filename);

            // Ensure export directory exists
            Files.createDirectories(filepath.getParent());

            // Create workbook and sheet
            try (Workbook workbook = new XSSFWorkbook()) {
                Sheet sheet = workbook.createSheet("Sample Plots");

                // Create header row
                Row headerRow = sheet.createRow(0);
                String[] headers = {"Plot ID", "Compartment ID", "Easting (m)", "Northing (m)", "Latitude", "Longitude"};

                CellStyle headerStyle = createHeaderStyle(workbook);

                for (int i = 0; i < headers.length; i++) {
                    Cell cell = headerRow.createCell(i);
                    cell.setCellValue(headers[i]);
                    cell.setCellStyle(headerStyle);
                }

                // Create data rows
                int rowNum = 1;
                CellStyle numberStyle = createNumberStyle(workbook);

                for (SamplePlot plot : samplePlots) {
                    Row row = sheet.createRow(rowNum++);

                    // Plot ID
                    row.createCell(0).setCellValue(plot.getPlotId());

                    // Compartment ID
                    row.createCell(1).setCellValue(plot.getCompartment().getCompartmentId());

                    // Easting
                    Cell eastingCell = row.createCell(2);
                    if (plot.getEasting() != null) {
                        eastingCell.setCellValue(plot.getEasting().doubleValue());
                        eastingCell.setCellStyle(numberStyle);
                    }

                    // Northing
                    Cell northingCell = row.createCell(3);
                    if (plot.getNorthing() != null) {
                        northingCell.setCellValue(plot.getNorthing().doubleValue());
                        northingCell.setCellStyle(numberStyle);
                    }

                    // Latitude
                    Cell latCell = row.createCell(4);
                    if (plot.getLatitude() != null) {
                        latCell.setCellValue(plot.getLatitude().doubleValue());
                        latCell.setCellStyle(numberStyle);
                    }

                    // Longitude
                    Cell lonCell = row.createCell(5);
                    if (plot.getLongitude() != null) {
                        lonCell.setCellValue(plot.getLongitude().doubleValue());
                        lonCell.setCellStyle(numberStyle);
                    }
                }

                // Auto-size columns
                for (int i = 0; i < headers.length; i++) {
                    sheet.autoSizeColumn(i);
                }

                // Write to file
                try (FileOutputStream fos = new FileOutputStream(filepath.toFile())) {
                    workbook.write(fos);
                }
            }

            log.info("Excel export created: {}", filepath);
            return filepath.toString();

        } catch (IllegalArgumentException e) {
            log.error("Invalid argument for Excel export: {}", e.getMessage());
            throw e;
        } catch (IOException e) {
            log.error("Error writing Excel file: {}", e.getMessage(), e);
            throw new IOException("Failed to export to Excel: " + e.getMessage(), e);
        } catch (Exception e) {
            log.error("Error exporting to Excel: {}", e.getMessage(), e);
            throw new IOException("Failed to export to Excel: " + e.getMessage(), e);
        }
    }

    /**
     * Get coordinate export statistics.
     *
     * @param analysisResultId ID of the analysis result
     * @return Map with export statistics
     */
    public Map<String, Object> getExportStatistics(UUID analysisResultId) {
        try {
            List<SamplePlot> samplePlots = samplePlotRepository.findByAnalysisResultId(analysisResultId);

            Map<String, Object> stats = new HashMap<>();
            stats.put("totalPlots", samplePlots.size());
            stats.put("plotsWithUTM", samplePlots.stream()
                    .filter(p -> p.getEasting() != null && p.getNorthing() != null)
                    .count());
            stats.put("plotsWithLatLon", samplePlots.stream()
                    .filter(p -> p.getLatitude() != null && p.getLongitude() != null)
                    .count());

            // Group by compartment
            Map<String, Long> plotsByCompartment = new HashMap<>();
            for (SamplePlot plot : samplePlots) {
                String compartmentId = plot.getCompartment().getCompartmentId();
                plotsByCompartment.put(compartmentId, plotsByCompartment.getOrDefault(compartmentId, 0L) + 1);
            }
            stats.put("plotsByCompartment", plotsByCompartment);

            return stats;

        } catch (Exception e) {
            log.error("Error calculating export statistics: {}", e.getMessage(), e);
            throw new RuntimeException("Failed to calculate statistics: " + e.getMessage(), e);
        }
    }

    /**
     * Create header cell style for Excel.
     *
     * @param workbook The workbook
     * @return CellStyle for headers
     */
    private CellStyle createHeaderStyle(Workbook workbook) {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setBold(true);
        font.setColor(IndexedColors.WHITE.getIndex());
        style.setFont(font);
        style.setFillForegroundColor(IndexedColors.BLUE.getIndex());
        style.setFillPattern(FillPatternType.SOLID_FOREGROUND);
        style.setAlignment(HorizontalAlignment.CENTER);
        style.setVerticalAlignment(VerticalAlignment.CENTER);
        return style;
    }

    /**
     * Create number cell style for Excel.
     *
     * @param workbook The workbook
     * @return CellStyle for numbers
     */
    private CellStyle createNumberStyle(Workbook workbook) {
        CellStyle style = workbook.createCellStyle();
        DataFormat format = workbook.createDataFormat();
        style.setDataFormat(format.getFormat("0.00"));
        return style;
    }

    /**
     * Escape special characters in CSV values.
     *
     * @param value The value to escape
     * @return Escaped value
     */
    private String escapeCSV(String value) {
        if (value == null) {
            return "";
        }
        if (value.contains(",") || value.contains("\"") || value.contains("\n")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

    /**
     * Format BigDecimal number for output.
     *
     * @param value The value to format
     * @return Formatted string
     */
    private String formatNumber(BigDecimal value) {
        if (value == null) {
            return "";
        }
        return value.setScale(2, java.math.RoundingMode.HALF_UP).toString();
    }
}
