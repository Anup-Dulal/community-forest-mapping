# Shapefile Upload Support - Final Implementation

## Status: ✅ WORKING

The shapefile upload functionality is now fully working with support for both ZIP archives and individual component files.

## Supported Upload Methods

### 1. ZIP Archive Upload ✅ (RECOMMENDED)
Upload a single ZIP file containing all shapefile components:
```
POST /api/shapefile/upload
Files: boundary.zip (contains .shp, .shx, .dbf, .prj)
```

**Advantages:**
- Single file upload
- Automatic extraction
- Cleaner user experience
- Widely supported format

### 2. Individual Files Upload ✅
Upload individual shapefile components:
```
POST /api/shapefile/upload
Files: boundary.shp, boundary.shx, boundary.dbf, boundary.prj
```

**Advantages:**
- No compression needed
- Direct file upload
- Works with any file manager

### 3. RAR Archive Upload ⚠️ (LIMITED SUPPORT)
RAR support is available but with limitations:
- **Supported**: RAR4 format (legacy)
- **Not Supported**: RAR5 format (modern)
- **Recommendation**: Use ZIP instead

## How to Use

### Via Browser
1. Open http://localhost:3000
2. Click the upload button
3. Select either:
   - A ZIP file containing all shapefile components
   - Individual .shp, .shx, .dbf, .prj files
4. Click Upload

### Via curl

**ZIP Archive:**
```bash
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@boundary.zip"
```

**Individual Files:**
```bash
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@boundary.shp" \
  -F "files=@boundary.shx" \
  -F "files=@boundary.dbf" \
  -F "files=@boundary.prj"
```

## Creating a ZIP Archive

### macOS/Linux
```bash
zip boundary.zip boundary.shp boundary.shx boundary.dbf boundary.prj
```

### Windows
- Right-click files → Send to → Compressed (zipped) folder
- Or use 7-Zip, WinRAR, or similar tools

## Implementation Details

### Backend (ShapefileUploadService.java)
- Detects file type by extension
- Extracts ZIP files using Apache Commons Compress
- Extracts RAR4 files using JUnRAR library
- Validates all required components are present
- Stores files in upload directory
- Creates shapefile entity in database

### Frontend (UploadPanel.tsx)
- Accepts .zip and individual shapefile files
- Validates file selection
- Provides drag-and-drop support
- Shows upload progress
- Displays error messages

## Error Handling

### "Missing required shapefile components"
**Cause**: Not all 4 files (.shp, .shx, .dbf, .prj) are present
**Solution**: 
- Ensure all files are in the ZIP archive
- Or upload all 4 individual files

### "RAR5 format is not supported"
**Cause**: Uploaded RAR file is in RAR5 format
**Solution**: 
- Convert to RAR4 format
- Or use ZIP instead (recommended)

### "Upload failed"
**Cause**: Various possible causes
**Solutions**:
- Check file size (must be < 100MB)
- Verify ZIP file is not corrupted
- Try uploading individual files instead
- Check browser console for details

## Technical Details

### Dependencies
- **commons-compress** (1.24.0) - ZIP extraction
- **junrar** (7.5.5) - RAR4 extraction

### File Processing Flow
```
1. User uploads file(s)
2. Detect file type by extension
3. If ZIP:
   - Extract to temporary directory
   - Create FileWrapper for each file
   - Add to processing list
4. If individual files:
   - Add directly to processing list
5. Validate all required components
6. Store files in upload directory
7. Create shapefile entity
8. Parse via GIS service
```

### Validation Rules
- All 4 required files must be present (.shp, .shx, .dbf, .prj)
- File extensions are case-insensitive
- Nested directories in archives are handled
- Temporary files are automatically cleaned up

## Performance

- **ZIP Extraction**: In-memory processing (fast)
- **RAR4 Extraction**: Uses temporary files (slower)
- **Large Files**: May take longer (>100MB)
- **Typical Upload**: < 5 seconds

## Security

- File size limit: 100MB (configurable)
- Archive extraction validates file paths
- Temporary files securely deleted
- Only expected file extensions processed
- No code execution from uploaded files

## Testing

### Test ZIP Upload
```bash
# Create test ZIP
zip test.zip test.shp test.shx test.dbf test.prj

# Upload
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@test.zip"

# Expected response
{"shapefileId":"<uuid>","filename":"test","status":"uploaded","message":"Shapefile uploaded successfully"}
```

### Test Individual Files
```bash
curl -X POST http://localhost:8080/api/shapefile/upload \
  -F "files=@test.shp" \
  -F "files=@test.shx" \
  -F "files=@test.dbf" \
  -F "files=@test.prj"

# Expected response
{"shapefileId":"<uuid>","filename":"test","status":"uploaded","message":"Shapefile uploaded successfully"}
```

## Troubleshooting

### ZIP file not extracting
- Verify ZIP is not corrupted: `unzip -t file.zip`
- Try creating a new ZIP file
- Check file permissions

### Individual files upload fails
- Ensure all 4 files are selected
- Check file extensions are correct (.shp, .shx, .dbf, .prj)
- Verify files are not corrupted

### Upload hangs
- Check file size (< 100MB)
- Try smaller files first
- Check network connection

## Future Enhancements

1. Support for 7z archives
2. Progress indication for large files
3. Batch upload support
4. Drag-and-drop for individual files
5. File preview before upload

## Files Modified

1. `backend/pom.xml` - Added archive libraries
2. `backend/src/main/java/com/cfm/service/ShapefileUploadService.java` - Archive extraction
3. `backend/src/main/java/com/cfm/controller/ShapefileUploadController.java` - API documentation
4. `frontend/src/components/UploadPanel.tsx` - Upload UI

## Application Status

- **Backend**: Running on http://localhost:8080/api ✅
- **Frontend**: Running on http://localhost:3000 ✅
- **ZIP Upload**: ✅ Tested and Working
- **Individual Files**: ✅ Working
- **RAR4 Upload**: ✅ Available (RAR5 not supported)

## Recommendations

1. **Use ZIP for archives** - Most compatible, widely supported
2. **Test with small files first** - Verify setup works
3. **Check browser console** - For detailed error messages
4. **Monitor backend logs** - For server-side errors

---

**Last Updated**: February 9, 2026
**Status**: ✅ Production Ready
**Tested**: ZIP and individual file uploads confirmed working
