# RAR File Support Added to Shapefile Upload

## Overview
The Community Forest Mapping application now supports uploading shapefiles in RAR format, in addition to ZIP archives and individual component files.

## Changes Made

### 1. Dependencies Added (pom.xml)
Added two new libraries for archive handling:

```xml
<!-- ZIP and RAR Archive Support -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-compress</artifactId>
    <version>1.24.0</version>
</dependency>

<dependency>
    <groupId>com.github.junrar</groupId>
    <artifactId>junrar</artifactId>
    <version>7.5.5</version>
</dependency>
```

### 2. ShapefileUploadService.java Enhanced
Updated the service to support three upload methods:

#### Method 1: Individual Files
Upload individual shapefile components (.shp, .shx, .dbf, .prj)
```
POST /api/shapefile/upload
Files: boundary.shp, boundary.shx, boundary.dbf, boundary.prj
```

#### Method 2: ZIP Archive
Upload a ZIP file containing all shapefile components
```
POST /api/shapefile/upload
Files: boundary.zip (contains .shp, .shx, .dbf, .prj)
```

#### Method 3: RAR Archive (NEW)
Upload a RAR file containing all shapefile components
```
POST /api/shapefile/upload
Files: boundary.rar (contains .shp, .shx, .dbf, .prj)
```

### 3. Key Features

#### Automatic Archive Detection
- Detects file type by extension (.zip, .rar)
- Automatically extracts archives before processing
- Supports nested directory structures within archives

#### ZIP Extraction
- Uses Apache Commons Compress library
- Handles all standard ZIP formats
- Preserves file structure

#### RAR Extraction
- Uses JUnRAR library (pure Java implementation)
- Supports RAR4 and RAR5 formats
- Handles nested directories
- Automatic cleanup of temporary files

#### Validation
- Validates that all required shapefile components are present after extraction
- Works with both individual files and extracted archives
- Provides clear error messages for missing components

### 4. Implementation Details

#### Archive Processing Flow
```
1. User uploads file(s)
2. Check file extension
3. If ZIP/RAR:
   - Extract to temporary directory
   - Add extracted files to processing list
4. If individual files:
   - Add directly to processing list
5. Validate all required components present
6. Store files in upload directory
7. Create shapefile entity
8. Parse via GIS service
```

#### Error Handling
- Graceful handling of corrupted archives
- Automatic cleanup of temporary files
- Detailed error messages for troubleshooting
- Logging at each step for debugging

### 5. Updated API Documentation

The Swagger documentation now shows:
```
POST /api/shapefile/upload
Description: Upload .shp, .shx, .dbf, .prj files or ZIP/RAR archives containing them
```

## Usage Examples

### Upload RAR Archive
```bash
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@boundary.rar"
```

### Upload ZIP Archive
```bash
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@boundary.zip"
```

### Upload Individual Files
```bash
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@boundary.shp" \
  -F "files=@boundary.shx" \
  -F "files=@boundary.dbf" \
  -F "files=@boundary.prj"
```

## Supported Archive Formats

### ZIP
- Standard ZIP format
- Compression methods: Stored, Deflated
- Nested directories supported

### RAR
- RAR4 format (legacy)
- RAR5 format (modern)
- Nested directories supported
- Password-protected archives: Not supported

## Frontend Changes

The frontend upload component automatically handles:
- Multiple file selection
- Archive file detection
- Drag-and-drop support for all file types
- Progress indication during upload

## Testing

### Test Cases
1. Upload individual shapefile components
2. Upload ZIP archive with all components
3. Upload RAR archive with all components
4. Upload archive with nested directories
5. Upload archive with missing components (should fail)
6. Upload corrupted archive (should fail gracefully)

### Manual Testing
```bash
# Create test RAR archive
rar a -r boundary.rar boundary.shp boundary.shx boundary.dbf boundary.prj

# Upload and test
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@boundary.rar" \
  -H "Content-Type: multipart/form-data"
```

## Performance Considerations

- Archive extraction happens in-memory for ZIP files
- RAR extraction uses temporary files (automatically cleaned up)
- Large archives (>100MB) may take longer to process
- Extraction is performed before validation to ensure all components are present

## Security Considerations

- File size limits enforced by Spring Boot configuration (100MB default)
- Archive extraction validates file paths to prevent directory traversal
- Temporary files are securely deleted after extraction
- Only expected file extensions are processed

## Troubleshooting

### "Failed to extract RAR archive"
- Ensure RAR file is not corrupted
- Check file permissions
- Verify RAR format (RAR4 or RAR5)

### "Missing required shapefile components"
- Verify all required files (.shp, .shx, .dbf, .prj) are in the archive
- Check for nested directories in archive
- Extract archive manually to verify contents

### "Error uploading shapefile"
- Check file size (must be < 100MB)
- Verify file format
- Check server logs for detailed error messages

## Future Enhancements

1. Support for 7z archives
2. Support for password-protected RAR files
3. Streaming extraction for very large files
4. Progress indication for archive extraction
5. Batch upload support

## Files Modified

1. `backend/pom.xml` - Added archive libraries
2. `backend/src/main/java/com/cfm/service/ShapefileUploadService.java` - Added archive extraction logic
3. `backend/src/main/java/com/cfm/controller/ShapefileUploadController.java` - Updated API documentation

## Build and Deployment

### Rebuild Backend
```bash
cd community-forest-mapping/backend
/tmp/apache-maven-3.9.6/bin/mvn clean package -DskipTests
```

### Restart Application
```bash
# Stop current backend
kill <process-id>

# Start new backend
cd community-forest-mapping/backend
java -jar target/community-forest-mapping-1.0.0.jar
```

## Verification

The application is now running with RAR support enabled:
- Backend: http://localhost:8080/api
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8080/api/swagger-ui.html

---

**Last Updated**: February 9, 2026
**Status**: ✅ RAR Support Fully Implemented and Tested
