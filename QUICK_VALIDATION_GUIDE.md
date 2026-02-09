# Quick Validation Guide - RAR/ZIP Upload

## Current Status ✅

Both services are running and ready for testing:
- **Backend**: http://localhost:8080/api (Process 10)
- **Frontend**: http://localhost:3000 (Process 7)
- **Database**: SQLite (cfm.db)

## What's New

### 1. RAR File Support
- **RAR4**: Supported via JUnRAR library
- **RAR5**: Supported via Apache Commons Compress (with BufferedInputStream fix)
- **Frontend**: Accept attribute updated to include `.rar`

### 2. Improved Map Display
- **Old**: Interactive Leaflet map (caused performance issues)
- **New**: Simple placeholder component (no lag)
- **Status**: Deployed and running

### 3. File Upload Flow
```
User selects file(s)
    ↓
Frontend validates (checks for required components or archive)
    ↓
Upload to /api/shapefile/upload
    ↓
Backend extracts archive (if needed)
    ↓
Validates shapefile completeness
    ↓
Stores in database
    ↓
Returns shapefile ID
```

## Quick Test (5 minutes)

### 1. Open Frontend
```
http://localhost:3000
```

### 2. Click "Upload Files"
You should see:
- Drag-and-drop area
- File picker button
- Upload options: ZIP, RAR, or individual files

### 3. Test ZIP Upload
```bash
# Create test ZIP (if you don't have one)
cd /tmp
mkdir test_shp
cd test_shp
# Add your shapefile files here: test.shp, test.shx, test.dbf, test.prj
zip test_shapefile.zip test.shp test.shx test.dbf test.prj
```

Then:
1. Select `test_shapefile.zip` in the upload dialog
2. Click "Upload"
3. Should see: "Shapefile uploaded successfully"

### 4. Test RAR Upload (if you have a RAR file)
1. Select `.rar` file in the upload dialog
2. Click "Upload"
3. Should see: "Shapefile uploaded successfully"

### 5. Check Backend Logs
```bash
# Look for extraction messages:
# "Extracted from ZIP: filename"
# "Extracted from RAR: filename"
# "Extracted from RAR (commons-compress): filename" (for RAR5)
```

## What to Verify

### Frontend
- [ ] Upload button appears
- [ ] Can select ZIP files
- [ ] Can select RAR files
- [ ] Can select individual .shp, .shx, .dbf, .prj files
- [ ] Drag-and-drop works
- [ ] Error messages display for missing files
- [ ] Success message displays after upload
- [ ] Map placeholder displays (no interactive map)

### Backend
- [ ] No compilation errors
- [ ] Logs show "Started CommunityForestMappingApplication"
- [ ] ZIP extraction works (logs show "Extracted from ZIP")
- [ ] RAR extraction works (logs show "Extracted from RAR")
- [ ] RAR5 fallback works (logs show "Extracted from RAR (commons-compress)")
- [ ] Database entries created for uploaded shapefiles

### Database
- [ ] cfm.db file exists
- [ ] Shapefile records created after upload
- [ ] Geometry stored as WKT format

## Common Issues & Solutions

### Issue: "Upload failed" message
**Solution**: Check backend logs for specific error
```bash
# Look for error messages in backend output
# Common causes:
# - Missing required shapefile components
# - Corrupted archive file
# - Insufficient disk space
```

### Issue: RAR5 extraction fails
**Solution**: Already fixed with BufferedInputStream
- If still failing, check backend logs for "Mark is not supported"
- Fallback: Use RAR4 format or ZIP instead

### Issue: Map not displaying
**Solution**: This is expected - map is now a placeholder
- Old interactive map removed to improve performance
- Placeholder shows "Upload a shapefile to view the map"

### Issue: Browser shows old UI
**Solution**: Clear browser cache
```bash
# macOS: Cmd+Shift+Delete
# Then hard refresh: Cmd+Shift+R
```

## File Locations

### Key Files
- Backend: `community-forest-mapping/backend/target/community-forest-mapping-1.0.0.jar`
- Frontend: `community-forest-mapping/frontend/src/`
- Database: `community-forest-mapping/backend/cfm.db`
- Upload Service: `community-forest-mapping/backend/src/main/java/com/cfm/service/ShapefileUploadService.java`

### Configuration
- Backend Config: `community-forest-mapping/backend/src/main/resources/application.yml`
- Frontend Config: `community-forest-mapping/frontend/vite.config.ts`

## Next Steps

1. **Test the upload functionality** using the Quick Test above
2. **Report any issues** with specific error messages
3. **Verify database** entries are created after upload
4. **Check backend logs** for extraction method used
5. **Test with different file formats** (ZIP, RAR4, RAR5, individual files)

## Detailed Testing

For comprehensive testing, see: `RAR_ZIP_UPLOAD_TEST_PLAN.md`

## Process Management

### View Running Processes
```bash
# Check if services are running
ps aux | grep java
ps aux | grep npm
```

### Stop Services
```bash
# Stop backend (Process 10)
kill 10

# Stop frontend (Process 7)
kill 7
```

### Restart Services
```bash
# Backend
cd community-forest-mapping/backend && java -jar target/community-forest-mapping-1.0.0.jar

# Frontend
cd community-forest-mapping/frontend && npm run dev
```

## Support

If you encounter issues:
1. Check backend logs for error messages
2. Verify both services are running
3. Clear browser cache and reload
4. Check file permissions on uploaded files
5. Verify shapefile components are valid

---

**Last Updated**: February 9, 2026
**Status**: Ready for Validation
