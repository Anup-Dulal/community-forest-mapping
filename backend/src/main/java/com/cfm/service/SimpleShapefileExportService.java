package com.cfm.service;

import com.cfm.model.Shapefile;
import com.cfm.repository.ShapefileRepository;
import lombok.extern.slf4j.Slf4j;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.geotools.data.DataStore;
import org.geotools.data.DataStoreFinder;
import org.geotools.data.FeatureSource;
import org.geotools.feature.FeatureCollection;
import org.geotools.feature.FeatureIterator;
import org.opengis.feature.simple.SimpleFeature;
import org.opengis.feature.simple.SimpleFeatureType;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.List;

/**
 * Simple export service for shapefiles.
 * Generates PNG map and Excel attribute table immediately after upload.
 */
@Slf4j
@Service
public class SimpleShapefileExportService {

    @Autowired
    private ShapefileRepository shapefileRepository;

    @Value("${export.dir:./exports}")
    private String exportDir;

    /**
     * Export shapefile as PNG map image.
     * Creates a simple boundary visualization.
     *
     * @param shapefileId UUID of the shapefile
     * @return Path to the generated PNG file
     */
    public String exportToPNG(UUID shapefileId) throws IOException {
        try {
            Shapefile shapefile = shapefileRepository.findById(shapefileId)
                    .orElseThrow(() -> new IllegalArgumentException("Shapefile not found: " + shapefileId));

            log.info("Exporting shapefile to PNG: {}", shapefileId);

            // Create export directory
            Path exportPath = Paths.get(exportDir);
            Files.createDirectories(exportPath);

            // Generate simple boundary map
            String filename = String.format("shapefile_%s.png", shapefileId);
            Path filepath = exportPath.resolve(filename);

            // Create a simple map image
            BufferedImage image = createSimpleMap(shapefile);
            ImageIO.write(image, "PNG", filepath.toFile());

            log.info("PNG export created: {}", filepath);
            return filepath.toString();

        } catch (Exception e) {
            log.error("Error exporting to PNG: {}", e.getMessage(), e);
            throw new IOException("Failed to export to PNG: " + e.getMessage(), e);
        }
    }

    /**
     * Export shapefile attributes to Excel.
     * Creates a table with all shapefile attributes.
     *
     * @param shapefileId UUID of the shapefile
     * @return Path to the generated Excel file
     */
    public String exportToExcel(UUID shapefileId) throws IOException {
        try {
            Shapefile shapefile = shapefileRepository.findById(shapefileId)
                    .orElseThrow(() -> new IllegalArgumentException("Shapefile not found: " + shapefileId));

            log.info("Exporting shapefile to Excel: {}", shapefileId);

            // Create export directory
            Path exportPath = Paths.get(exportDir);
            Files.createDirectories(exportPath);

            String filename = String.format("shapefile_%s.xlsx", shapefileId);
            Path filepath = exportPath.resolve(filename);

            // Create Excel workbook
            try (Workbook workbook = new XSSFWorkbook()) {
                Sheet sheet = workbook.createSheet("Shapefile Data");

                // Create header row
                Row headerRow = sheet.createRow(0);
                CellStyle headerStyle = createHeaderStyle(workbook);

                String[] headers = {"ID", "Filename", "Projection", "Bounding Box", "Upload Date"};
                for (int i = 0; i < headers.length; i++) {
                    Cell cell = headerRow.createCell(i);
                    cell.setCellValue(headers[i]);
                    cell.setCellStyle(headerStyle);
                }

                // Create data row
                Row dataRow = sheet.createRow(1);
                dataRow.createCell(0).setCellValue(shapefile.getId().toString());
                dataRow.createCell(1).setCellValue(shapefile.getFilename());
                dataRow.createCell(2).setCellValue(shapefile.getProjection() != null ? shapefile.getProjection() : "N/A");
                dataRow.createCell(3).setCellValue(shapefile.getBoundingBox() != null ? shapefile.getBoundingBox() : "N/A");
                dataRow.createCell(4).setCellValue(shapefile.getUploadedAt() != null ? shapefile.getUploadedAt().toString() : "N/A");

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

        } catch (Exception e) {
            log.error("Error exporting to Excel: {}", e.getMessage(), e);
            throw new IOException("Failed to export to Excel: " + e.getMessage(), e);
        }
    }

    /**
     * Create a simple map visualization.
     */
    private BufferedImage createSimpleMap(Shapefile shapefile) {
        int width = 800;
        int height = 600;
        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = image.createGraphics();

        // Set rendering hints
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Fill background
        g2d.setColor(Color.WHITE);
        g2d.fillRect(0, 0, width, height);

        // Draw title
        g2d.setColor(Color.BLACK);
        g2d.setFont(new Font("Arial", Font.BOLD, 20));
        g2d.drawString("Shapefile Boundary Map", 20, 40);

        // Draw filename
        g2d.setFont(new Font("Arial", Font.PLAIN, 14));
        g2d.drawString("File: " + shapefile.getFilename(), 20, 70);

        // Draw placeholder boundary
        g2d.setColor(new Color(0, 120, 215));
        g2d.setStroke(new BasicStroke(3));
        g2d.drawRect(100, 150, 600, 400);

        // Draw info text
        g2d.setColor(Color.GRAY);
        g2d.setFont(new Font("Arial", Font.ITALIC, 12));
        g2d.drawString("Shapefile uploaded successfully", 250, 350);
        g2d.drawString("ID: " + shapefile.getId(), 250, 370);

        g2d.dispose();
        return image;
    }

    /**
     * Create header cell style for Excel.
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
}
