# Documentation Guide - Community Forest Mapping

## Quick Navigation

### 🚀 Start Here
- **[READY_FOR_TESTING.md](READY_FOR_TESTING.md)** - Executive summary and 5-minute test guide
- **[QUICK_VALIDATION_GUIDE.md](QUICK_VALIDATION_GUIDE.md)** - Quick start for testing

### 📋 Testing & Validation
- **[RAR_ZIP_UPLOAD_TEST_PLAN.md](RAR_ZIP_UPLOAD_TEST_PLAN.md)** - Comprehensive test plan with all scenarios
- **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - Current system status and what's working

### 🏗️ Technical Documentation
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Architecture, data flow, and system design

### 📚 Additional Resources
- **[LOCAL_VALIDATION_COMPLETE.md](LOCAL_VALIDATION_COMPLETE.md)** - Previous validation results
- **[QUICK_START.md](QUICK_START.md)** - General quick start guide
- **[README.md](README.md)** - Project overview

---

## Documentation by Use Case

### I want to test the application (5 minutes)
1. Read: **[READY_FOR_TESTING.md](READY_FOR_TESTING.md)** - Overview and quick test
2. Follow: 5-minute test steps
3. Verify: Upload works and database entries are created

### I want to understand the system architecture
1. Read: **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Architecture diagram and data flow
2. Review: File structure and technology stack
3. Check: API endpoints and configuration

### I want to run comprehensive tests
1. Read: **[RAR_ZIP_UPLOAD_TEST_PLAN.md](RAR_ZIP_UPLOAD_TEST_PLAN.md)** - Full test plan
2. Follow: Test scenarios for ZIP, RAR4, RAR5, and individual files
3. Verify: All test cases pass

### I want to understand the implementation
1. Read: **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical details
2. Review: Backend architecture and file upload service
3. Check: Frontend components and database schema

### I want to troubleshoot an issue
1. Check: **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - Known issues and solutions
2. Review: **[READY_FOR_TESTING.md](READY_FOR_TESTING.md)** - Common issues section
3. Check: Backend logs for specific error messages

### I want to deploy to production
1. Read: **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Deployment checklist
2. Review: **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Technology stack and configuration
3. Consider: Recommendations for production (PostGIS, streaming upload, etc.)

---

## Document Descriptions

### READY_FOR_TESTING.md
**Purpose**: Executive summary and quick start guide
**Audience**: Everyone
**Length**: 5 minutes to read
**Contains**:
- System status overview
- What's implemented
- 5-minute test procedure
- Common issues and solutions
- Quick links and next steps

### QUICK_VALIDATION_GUIDE.md
**Purpose**: Quick reference for testing
**Audience**: Testers
**Length**: 3 minutes to read
**Contains**:
- Current status
- What's new
- Quick test (5 minutes)
- What to verify
- Common issues & solutions
- File locations

### RAR_ZIP_UPLOAD_TEST_PLAN.md
**Purpose**: Comprehensive testing guide
**Audience**: QA engineers, developers
**Length**: 15 minutes to read
**Contains**:
- Implementation status
- Test scenarios (ZIP, RAR4, RAR5, individual files)
- Edge cases
- Testing procedure
- Expected outcomes
- Known issues and workarounds

### CURRENT_STATUS.md
**Purpose**: Current system status and what's working
**Audience**: Developers, project managers
**Length**: 10 minutes to read
**Contains**:
- System status
- What's working
- What's fixed
- What's ready to test
- Documentation created
- Next steps
- Key files to know

### IMPLEMENTATION_SUMMARY.md
**Purpose**: Technical implementation details
**Audience**: Developers, architects
**Length**: 20 minutes to read
**Contains**:
- Implementation timeline
- Technical architecture
- Backend components
- Frontend components
- Database schema
- API endpoints
- Error handling
- Testing strategy
- Deployment checklist

### SYSTEM_OVERVIEW.md
**Purpose**: System architecture and design
**Audience**: Architects, senior developers
**Length**: 25 minutes to read
**Contains**:
- Architecture diagram
- Data flow
- File structure
- Technology stack
- Dependencies
- Configuration
- API endpoints
- Performance characteristics
- Monitoring & logging
- Troubleshooting guide

---

## Key Information by Topic

### File Upload
- **How it works**: See SYSTEM_OVERVIEW.md → Data Flow
- **Implementation**: See IMPLEMENTATION_SUMMARY.md → Backend Architecture
- **Testing**: See RAR_ZIP_UPLOAD_TEST_PLAN.md → Test Scenarios
- **Troubleshooting**: See READY_FOR_TESTING.md → Common Issues

### RAR Support
- **RAR4**: JUnRAR library (v7.5.5)
- **RAR5**: Apache Commons Compress (v1.26.0) with BufferedInputStream
- **Details**: See IMPLEMENTATION_SUMMARY.md → Backend Architecture
- **Testing**: See RAR_ZIP_UPLOAD_TEST_PLAN.md → RAR4/RAR5 Upload Testing

### ZIP Support
- **Library**: Apache Commons Compress (v1.26.0)
- **Details**: See IMPLEMENTATION_SUMMARY.md → Backend Architecture
- **Testing**: See RAR_ZIP_UPLOAD_TEST_PLAN.md → ZIP File Upload

### Frontend
- **Upload Component**: UploadPanel.tsx
- **Map Component**: MapViewer.tsx (placeholder)
- **Details**: See IMPLEMENTATION_SUMMARY.md → Frontend Architecture
- **Location**: `frontend/src/components/`

### Backend
- **Upload Service**: ShapefileUploadService.java
- **Upload Controller**: ShapefileUploadController.java
- **Details**: See IMPLEMENTATION_SUMMARY.md → Backend Architecture
- **Location**: `backend/src/main/java/com/cfm/`

### Database
- **Type**: SQLite
- **Location**: `backend/cfm.db`
- **Schema**: See IMPLEMENTATION_SUMMARY.md → Database Schema
- **Geometry Format**: WKT (Well-Known Text)

### API Endpoints
- **Upload**: POST /api/shapefile/upload
- **Get**: GET /api/shapefile/{id}
- **Details**: See IMPLEMENTATION_SUMMARY.md → API Endpoints
- **Docs**: http://localhost:8080/api/swagger-ui.html

### Performance
- **Upload Speed**: See SYSTEM_OVERVIEW.md → Performance Characteristics
- **Frontend Performance**: See SYSTEM_OVERVIEW.md → Performance Characteristics
- **Backend Performance**: See SYSTEM_OVERVIEW.md → Performance Characteristics

### Troubleshooting
- **Common Issues**: See READY_FOR_TESTING.md → Common Issues & Solutions
- **Backend Issues**: See SYSTEM_OVERVIEW.md → Troubleshooting Guide
- **Frontend Issues**: See SYSTEM_OVERVIEW.md → Troubleshooting Guide
- **Upload Issues**: See SYSTEM_OVERVIEW.md → Troubleshooting Guide

---

## Process Management

### Check Running Services
```bash
ps aux | grep java
ps aux | grep npm
```

### Stop Services
```bash
kill 10  # Backend
kill 7   # Frontend
```

### Restart Services
```bash
# Backend
cd community-forest-mapping/backend && java -jar target/community-forest-mapping-1.0.0.jar

# Frontend
cd community-forest-mapping/frontend && npm run dev
```

### Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/api
- API Docs: http://localhost:8080/api/swagger-ui.html

---

## File Locations

### Backend
- **Upload Service**: `backend/src/main/java/com/cfm/service/ShapefileUploadService.java`
- **Upload Controller**: `backend/src/main/java/com/cfm/controller/ShapefileUploadController.java`
- **Configuration**: `backend/src/main/resources/application.yml`
- **Dependencies**: `backend/pom.xml`
- **Database**: `backend/cfm.db`
- **JAR**: `backend/target/community-forest-mapping-1.0.0.jar`

### Frontend
- **Upload Panel**: `frontend/src/components/UploadPanel.tsx`
- **Map Viewer**: `frontend/src/components/MapViewer.tsx`
- **Configuration**: `frontend/vite.config.ts`
- **Package**: `frontend/package.json`

### Database
- **Location**: `backend/cfm.db`
- **Schema**: `database/schema.sql`

### Documentation
- **This Guide**: `DOCUMENTATION_GUIDE.md`
- **Ready for Testing**: `READY_FOR_TESTING.md`
- **Quick Validation**: `QUICK_VALIDATION_GUIDE.md`
- **Test Plan**: `RAR_ZIP_UPLOAD_TEST_PLAN.md`
- **Current Status**: `CURRENT_STATUS.md`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`
- **System Overview**: `SYSTEM_OVERVIEW.md`

---

## Reading Order Recommendations

### For Quick Testing (15 minutes)
1. READY_FOR_TESTING.md (5 min)
2. QUICK_VALIDATION_GUIDE.md (3 min)
3. Run 5-minute test (5 min)
4. Check results (2 min)

### For Comprehensive Testing (1 hour)
1. READY_FOR_TESTING.md (5 min)
2. RAR_ZIP_UPLOAD_TEST_PLAN.md (20 min)
3. Run all test scenarios (30 min)
4. Document results (5 min)

### For Understanding the System (1 hour)
1. READY_FOR_TESTING.md (5 min)
2. SYSTEM_OVERVIEW.md (25 min)
3. IMPLEMENTATION_SUMMARY.md (20 min)
4. Review code (10 min)

### For Troubleshooting (30 minutes)
1. CURRENT_STATUS.md (5 min)
2. READY_FOR_TESTING.md - Common Issues (5 min)
3. SYSTEM_OVERVIEW.md - Troubleshooting (10 min)
4. Check backend logs (10 min)

### For Production Deployment (2 hours)
1. IMPLEMENTATION_SUMMARY.md (20 min)
2. SYSTEM_OVERVIEW.md (25 min)
3. Review deployment checklist (10 min)
4. Review recommendations (5 min)
5. Plan deployment (60 min)

---

## Document Status

| Document | Status | Last Updated | Purpose |
|----------|--------|--------------|---------|
| READY_FOR_TESTING.md | ✅ Complete | Feb 9, 2026 | Executive summary |
| QUICK_VALIDATION_GUIDE.md | ✅ Complete | Feb 9, 2026 | Quick start |
| RAR_ZIP_UPLOAD_TEST_PLAN.md | ✅ Complete | Feb 9, 2026 | Test plan |
| CURRENT_STATUS.md | ✅ Complete | Feb 9, 2026 | Status update |
| IMPLEMENTATION_SUMMARY.md | ✅ Complete | Feb 9, 2026 | Technical details |
| SYSTEM_OVERVIEW.md | ✅ Complete | Feb 9, 2026 | Architecture |
| DOCUMENTATION_GUIDE.md | ✅ Complete | Feb 9, 2026 | This guide |

---

## Quick Links

### Testing
- [5-Minute Test](READY_FOR_TESTING.md#how-to-test-5-minutes)
- [Full Test Plan](RAR_ZIP_UPLOAD_TEST_PLAN.md)
- [Common Issues](READY_FOR_TESTING.md#common-issues--solutions)

### Technical
- [Architecture](SYSTEM_OVERVIEW.md#architecture-diagram)
- [API Endpoints](IMPLEMENTATION_SUMMARY.md#api-endpoints)
- [Database Schema](IMPLEMENTATION_SUMMARY.md#database-schema)

### Troubleshooting
- [Backend Issues](SYSTEM_OVERVIEW.md#troubleshooting-guide)
- [Frontend Issues](SYSTEM_OVERVIEW.md#troubleshooting-guide)
- [Upload Issues](SYSTEM_OVERVIEW.md#troubleshooting-guide)

### Access
- [Frontend](http://localhost:3000)
- [Backend API](http://localhost:8080/api)
- [API Docs](http://localhost:8080/api/swagger-ui.html)

---

## Support

### Need Help?
1. Check the relevant documentation above
2. Review the troubleshooting section
3. Check backend logs for error messages
4. Verify both services are running

### Report Issues
Include:
- Error message
- Steps to reproduce
- Backend logs
- Frontend console logs
- File details (name, size, format)

---

**Last Updated**: February 9, 2026
**Status**: ✅ Complete
**Next**: Start with READY_FOR_TESTING.md
