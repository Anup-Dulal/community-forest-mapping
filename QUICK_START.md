# Quick Start Guide: Community Forest Mapping System

## 5-Minute Setup (with Docker)

```bash
# 1. Clone repository
git clone <repository-url>
cd community-forest-mapping

# 2. Create .env file
cp .env.example .env

# 3. Start all services
docker-compose up --build

# 4. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8080
# GIS Service: http://localhost:8001
```

## Manual Setup (without Docker)

### Prerequisites
- Java 17+
- Maven 3.8+
- Node.js 18+
- Python 3.9+

### Setup Steps

#### 1. Backend Setup (10 minutes)
```bash
cd community-forest-mapping/backend

# Build
mvn clean install

# Run tests
mvn test

# Start server
mvn spring-boot:run
```

Backend will be available at: **http://localhost:8080**

The SQLite database will be automatically created at `./cfm.db` on first run.

#### 2. GIS Service Setup (5 minutes)
```bash
cd community-forest-mapping/gis-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start service
python src/main.py
```

GIS Service will be available at: **http://localhost:8001**

#### 3. Frontend Setup (5 minutes)
```bash
cd community-forest-mapping/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

## Testing the System

### Run All Tests
```bash
# Backend tests
cd community-forest-mapping/backend
mvn test

# GIS Service tests
cd community-forest-mapping/gis-service
source venv/bin/activate
pytest tests/

# Frontend tests
cd community-forest-mapping/frontend
npm test
```

### Test Complete Workflow
1. Open http://localhost:3000 in browser
2. Click "Upload" button
3. Select a test shapefile (boundary.shp, .shx, .dbf, .prj)
4. Verify upload succeeds
5. Check that boundary appears on map
6. Wait for DEM download and analysis
7. Verify compartments and sample plots appear
8. Export maps and coordinates

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8080  # Backend
lsof -i :8001  # GIS Service
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>
```

### Database Issues
```bash
# Remove old database file
rm cfm.db

# Backend will recreate on next run
mvn spring-boot:run
```

### Maven Build Failed
```bash
# Clear cache
mvn clean
rm -rf ~/.m2/repository

# Rebuild
mvn clean install
```

### Python Dependencies Failed
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt -v
```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│                    http://localhost:3000                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                  Backend API (Spring Boot)                       │
│                    http://localhost:8080                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│              GIS Processing (Python Microservice)                │
│                    http://localhost:8001                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ SQL
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer (SQLite)                           │
│                      ./cfm.db                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

✓ Shapefile upload and validation
✓ Automatic DEM download and clipping
✓ Terrain analysis (slope, aspect)
✓ Equal-area compartment generation
✓ Sample plot generation with constraints
✓ Coordinate export (CSV/Excel)
✓ Map rendering and export (PDF/PNG)
✓ Interactive web dashboard
✓ Session management and data persistence
✓ Comprehensive error handling
✓ Performance optimization with caching

## API Endpoints

### Session Management
- `POST /api/sessions/create` - Create new session
- `GET /api/sessions/{sessionId}/data` - Get session data
- `GET /api/sessions/{sessionId}/validate` - Validate data persistence
- `DELETE /api/sessions/{sessionId}` - Clear session

### Compartments
- `GET /api/compartments` - Get all compartments
- `GET /api/compartments/{id}` - Get specific compartment

### Sample Plots
- `GET /api/sample-plots` - Get all sample plots
- `GET /api/sample-plots/{id}` - Get specific sample plot

### Export
- `GET /api/export/coordinates/csv` - Export coordinates as CSV
- `GET /api/export/coordinates/excel` - Export coordinates as Excel
- `POST /api/export/maps` - Export maps

### Terrain Analysis
- `POST /api/terrain-analysis` - Trigger terrain analysis
- `GET /api/terrain-analysis/{id}` - Get analysis results

## Performance Metrics

| Operation | Expected Time |
|-----------|---------------|
| Shapefile upload | < 5 seconds |
| DEM download | 30-60 seconds |
| Terrain analysis | 10-30 seconds |
| Compartment generation | 5-15 seconds |
| Sample plot generation | 2-5 seconds |
| Map rendering | 5-10 seconds |
| Coordinate export | < 2 seconds |

## Documentation

- **VALIDATION_SUMMARY.md** - System validation status
- **LOCAL_VALIDATION_GUIDE.md** - Detailed setup and troubleshooting
- **CHECKPOINT_VERIFICATION.md** - System completion status
- **PRODUCTION_READINESS.md** - Production deployment checklist
- **IMPLEMENTATION_GUIDE.md** - Architecture and design patterns

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review LOCAL_VALIDATION_GUIDE.md for detailed help
3. Check application logs for error messages
4. Review IMPLEMENTATION_GUIDE.md for architecture details

## Next Steps

1. ✓ Complete setup following this guide
2. ✓ Run all tests to validate system
3. ✓ Test complete workflow
4. ✓ Monitor performance metrics
5. ✓ Review logs for any issues
6. ✓ Deploy to production (see PRODUCTION_READINESS.md)

---

**System Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2026-02-08
