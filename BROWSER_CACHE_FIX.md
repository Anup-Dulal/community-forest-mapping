# Browser Cache Issue - File Upload Dialog Showing RAR

## Problem
The file upload dialog is still showing RAR files as an option even though we removed RAR support.

## Root Cause
Browser caching - the old version of the UploadPanel component is cached in your browser.

## Solution

### Option 1: Hard Refresh (Recommended)
**Mac:**
- Press `Cmd + Shift + R`

**Windows/Linux:**
- Press `Ctrl + Shift + F5` or `Ctrl + Shift + Delete`

### Option 2: Clear Browser Cache
**Chrome/Edge:**
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "All time" for time range
3. Check "Cookies and other site data" and "Cached images and files"
4. Click "Clear data"
5. Refresh the page

**Firefox:**
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "Everything" for time range
3. Click "Clear Now"
4. Refresh the page

**Safari:**
1. Click "Safari" menu → "Preferences"
2. Click "Privacy" tab
3. Click "Manage Website Data"
4. Select the website and click "Remove"
5. Refresh the page

### Option 3: Incognito/Private Mode
Open the application in a new incognito/private window:
- Chrome: `Ctrl + Shift + N` (Windows) or `Cmd + Shift + N` (Mac)
- Firefox: `Ctrl + Shift + P` (Windows) or `Cmd + Shift + P` (Mac)
- Safari: `Cmd + Shift + N` (Mac)

Then navigate to http://localhost:3000

## After Clearing Cache

The file upload dialog should now show:
- ✅ .shp files
- ✅ .shx files
- ✅ .dbf files
- ✅ .prj files
- ✅ .zip files
- ❌ .rar files (removed)

## Verification

1. Open http://localhost:3000
2. Click "Upload" button
3. Click "Select files" or drag-and-drop area
4. The file picker should NOT show .rar files
5. You should only see .shp, .shx, .dbf, .prj, and .zip files

## If Issue Persists

1. **Restart browser completely** - Close all windows and reopen
2. **Check browser console** - Press `F12` and look for any errors
3. **Check backend logs** - Verify backend is running correctly
4. **Try different browser** - Test with Chrome, Firefox, or Safari

## Technical Details

The file input accept attribute has been updated to:
```
accept=".shp,.shx,.dbf,.prj,.zip"
```

This restricts the file picker to only show these file types.

---

**Last Updated**: February 9, 2026
**Status**: ✅ Fixed in code, requires browser cache clear
