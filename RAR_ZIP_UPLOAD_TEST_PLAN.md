# RAR/ZIP Upload Test Plan

## Overview
This document outlines the comprehensive testing strategy for RAR and ZIP file upload functionality in the Community Forest Mapping application.

## Current Implementation Status

### Backend
- **RAR4 Support**: JUnRAR library (v7.5.5)
- **RAR5 Support**: Apache Commons Compress (v1.26.0) with BufferedInputStream fix
- **ZIP Support**: Apache Commons Compress (v1.26.0)
- **File Wrapper**: Custom FileWrapper class to convert extracted files to MultipartFile format

### Frontend
- **Accept Attribute**: `.shp,.shx,.dbf,.prj,.zip,.rar`
- **Validation**: Checks for required shapefile components or archive files
- **UI**: Drag-and-drop and file picker support

## Test Scenarios

### 1. ZIP File Upload
**Objective**: Verify ZIP archive extraction and shapefile validation

**Test Cases**:
1. **Valid ZIP with all components**
   - Create ZIP containing: shapefile.shp, shapefile.shx, shapefile.dbf, shapefile.prj
   - Upload via frontend
   - Expected: Success message, shapefile ID returned
   - Verify: Files extracted correctly, database entry created

2. **ZIP with missing components**
   - Create ZIP missing .prj file
   - Upload via frontend
   - Expected: Error message "Missing required files: .prj"
   - Verify: Upload rejected, no database entry created

3. **ZIP with extra files**
   - Create ZIP with shapefile components + extra .txt file
   - Upload via frontend
   - Expected: Success (extra files ignored)
   - Verify: Only shapefile components processed

### 2. RAR4 File Upload
**Objective**: Verify RAR4 archive extraction using JUnRAR

**Test Cases**:
1. **Valid RAR4 with all components**
   - Create RAR4 containing: shapefile.shp, shapefile.shx, shapefile.dbf, shapefile.prj
   - Upload via frontend
   - Expected: Success message, shapefile ID returned
   - Verify: Files extracted correctly, database entry created

2. **RAR4 with missing components**
   - Create RAR4 missing .shx file
   - Upload via frontend
   - Expected: Error message "Missing required files: .shx"
   - Verify: Upload rejected, no database entry created

3. **RAR4 with nested directories**
   - Create RAR4 with shapefile components in subdirectory
   - Upload via frontend
   - Expected: Success (files extracted from subdirectory)
   - Verify: Filenames extracted correctly (no path prefixes)

### 3. RAR5 File Upload
**Objective**: Verify RAR5 archive extraction using Apache Commons Compress

**Test Cases**:
1. **Valid RAR5 with all components**
   - Create RAR5 containing: shapefile.shp, shapefile.shx, shapefile.dbf, shapefile.prj
   - Upload via frontend
   - Expected: Success message, shapefile ID returned
   - Verify: Files extracted correctly, database entry created
   - Note: JUnRAR will throw UnsupportedRarV5Exception, triggering commons-compress fallback

2. **RAR5 with missing components**
   - Create RAR5 missing .dbf file
   - Upload via frontend
   - Expected: Error message "Missing required files: .dbf"
   - Verify: Upload rejected, no database entry created

3. **RAR5 with nested directories**
   - Create RAR5 with shapefile components in subdirectory
   - Upload via frontend
   - Expected: Success (files extracted from subdirectory)
   - Verify: Filenames extracted correctly (no path prefixes)

### 4. Individual File Upload
**Objective**: Verify individual shapefile component upload

**Test Cases**:
1. **Valid individual files**
   - Select all 4 files: .shp, .shx, .dbf, .prj
   - Upload via frontend
   - Expected: Success message, shapefile ID returned
   - Verify: Files stored correctly, database entry created

2. **Missing individual files**
   - Select only .shp and .shx files
   - Upload via frontend
   - Expected: Error message "Missing required files: .dbf, .prj"
   - Verify: Upload rejected, no database entry created

3. **Mixed archive and individual files**
   - Select ZIP file + individual .shp file
   - Upload via frontend
   - Expected: Error message "Upload either an archive file OR individual shapefile components, not both"
   - Verify: Upload rejected

### 5. Edge Cases
**Objective**: Verify robustness and error handling

**Test Cases**:
1. **Large file upload**
   - Create ZIP/RAR with large shapefile (>100MB)
   - Upload via frontend
   - Expected: Success or appropriate error message
   - Verify: Timeout handling, memory management

2. **Corrupted archive**
   - Create corrupted ZIP/RAR file
   - Upload via frontend
   - Expected: Error message "Failed to extract archive"
   - Verify: Graceful error handling, no partial data stored

3. **Invalid file extension**
   - Rename ZIP to .txt
   - Upload via frontend
   - Expected: File picker rejects (accept attribute)
   - Verify: Frontend validation works

4. **Empty archive**
   - Create empty ZIP/RAR file
   - Upload via frontend
   - Expected: Error message "Missing required files"
   - Verify: Validation catches empty archives

5. **Duplicate filenames**
   - Create archive with duplicate shapefile names (e.g., two .shp files)
   - Upload via frontend
   - Expected: Success (last file wins) or error
   - Verify: Consistent behavior documented

## Testing Procedure

### Prerequisites
1. Backend running on http://localhost:8080/api
2. Frontend running on http://localhost:3000
3. Browser cache cleared
4. Test shapefile files available

### Step-by-Step Testing

#### Phase 1: ZIP Upload Testing
```bash
# 1. Create test ZIP file
cd /tmp
mkdir test_shapefile
cd test_shapefile
# Copy or create: test.shp, test.shx, test.dbf, test.prj
zip test_shapefile.zip test.shp test.shx test.dbf test.prj

# 2. Open frontend at http://localhost:3000
# 3. Click "Upload Files" button
# 4. Select test_shapefile.zip
# 5. Click "Upload"
# 6. Verify success message and shapefile ID
```

#### Phase 2: RAR4 Upload Testing
```bash
# 1. Create test RAR4 file (requires WinRAR or similar)
# 2. Open frontend at http://localhost:3000
# 3. Click "Upload Files" button
# 4. Select test_shapefile.rar (RAR4 format)
# 5. Click "Upload"
# 6. Verify success message and shapefile ID
```

#### Phase 3: RAR5 Upload Testing
```bash
# 1. Create test RAR5 file (requires WinRAR or similar)
# 2. Open frontend at http://localhost:3000
# 3. Click "Upload Files" button
# 4. Select test_shapefile.rar (RAR5 format)
# 5. Click "Upload"
# 6. Verify success message and shapefile ID
# 7. Check backend logs for commons-compress fallback message
```

#### Phase 4: Individual File Upload Testing
```bash
# 1. Open frontend at http://localhost:3000
# 2. Click "Upload Files" button
# 3. Select all 4 files: test.shp, test.shx, test.dbf, test.prj
# 4. Click "Upload"
# 5. Verify success message and shapefile ID
```

### Backend Log Monitoring

Monitor backend logs for extraction messages:
```bash
# For ZIP extraction:
# "Extracted from ZIP: filename"

# For RAR4 extraction:
# "Extracted from RAR: filename"

# For RAR5 extraction (commons-compress fallback):
# "RAR5 format detected, trying commons-compress"
# "Extracted from RAR (commons-compress): filename"

# For errors:
# "Error extracting [ZIP|RAR] archive"
# "Failed to extract RAR5 with commons-compress"
```

## Expected Outcomes

### Success Criteria
- ✅ ZIP files with all components upload successfully
- ✅ RAR4 files with all components upload successfully
- ✅ RAR5 files with all components upload successfully
- ✅ Individual shapefile components upload successfully
- ✅ Missing components are detected and rejected
- ✅ Mixed archive and individual files are rejected
- ✅ Corrupted archives are handled gracefully
- ✅ Backend logs show correct extraction method used
- ✅ Database entries created with correct shapefile data
- ✅ Frontend displays success/error messages appropriately

### Failure Criteria
- ❌ Upload fails for valid archives
- ❌ Corrupted archives cause application crash
- ❌ Missing components not detected
- ❌ Backend logs show extraction errors
- ❌ Database entries not created
- ❌ Frontend displays generic error messages

## Known Issues and Workarounds

### Issue 1: RAR5 Format Not Supported by JUnRAR
- **Symptom**: UnsupportedRarV5Exception thrown
- **Root Cause**: JUnRAR only supports RAR4 format
- **Solution**: Fallback to Apache Commons Compress
- **Status**: ✅ Fixed with BufferedInputStream

### Issue 2: Commons Compress Mark Not Supported
- **Symptom**: "Mark is not supported" error
- **Root Cause**: ArchiveStreamFactory requires BufferedInputStream
- **Solution**: Wrap FileInputStream in BufferedInputStream
- **Status**: ✅ Fixed in extractRarWithCommonsCompress method

## Performance Considerations

- **ZIP Extraction**: Fast, typically <1 second for small files
- **RAR4 Extraction**: Fast, typically <1 second for small files
- **RAR5 Extraction**: Slower due to commons-compress fallback, typically 1-2 seconds
- **Large Files**: May require timeout adjustment in application.yml

## Browser Cache Considerations

After deploying new frontend code:
1. Clear browser cache (Cmd+Shift+Delete on macOS)
2. Hard refresh (Cmd+Shift+R on macOS)
3. Verify new MapViewer placeholder is displayed

## Rollback Plan

If issues occur:
1. Stop backend: `kill <process-id>`
2. Revert to previous version: `git checkout HEAD~1`
3. Rebuild: `mvn clean package`
4. Restart: `java -jar target/community-forest-mapping-1.0.0.jar`

## Sign-Off

- [ ] ZIP upload testing complete
- [ ] RAR4 upload testing complete
- [ ] RAR5 upload testing complete
- [ ] Individual file upload testing complete
- [ ] Edge case testing complete
- [ ] Performance testing complete
- [ ] All tests passed

---

**Last Updated**: February 9, 2026
**Status**: Ready for Testing
