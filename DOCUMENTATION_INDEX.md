# Community Forest Mapping - Documentation Index

## Quick Navigation

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide (START HERE)
- **[LOCAL_VALIDATION_GUIDE.md](LOCAL_VALIDATION_GUIDE.md)** - Detailed local setup with troubleshooting

### System Overview
- **[README.md](README.md)** - Project overview and features
- **[SYSTEM_COMPLETE.md](SYSTEM_COMPLETE.md)** - System completion status
- **[CHECKPOINT_VERIFICATION.md](CHECKPOINT_VERIFICATION.md)** - Implementation checklist

### SQLite Migration
- **[SQLITE_MIGRATION_COMPLETE.md](SQLITE_MIGRATION_COMPLETE.md)** - Migration completion report
- **[SQLITE_MIGRATION_GUIDE.md](SQLITE_MIGRATION_GUIDE.md)** - Detailed migration documentation
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - Summary of all changes

### Deployment
- **[PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)** - Production deployment checklist
- **[GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md)** - GitHub Pages + backend deployment

### Architecture & Implementation
- **[IMPLEMENTATION_GUIDE.md](.kiro/specs/community-forest-mapping/IMPLEMENTATION_GUIDE.md)** - Architecture and design patterns
- **[INDEX.md](INDEX.md)** - System architecture overview

### Validation & Testing
- **[VALIDATION_SUMMARY.md](VALIDATION_SUMMARY.md)** - System validation status

---

## Documentation by Use Case

### I Want to...

#### Set Up Locally
1. Read: [QUICK_START.md](QUICK_START.md)
2. Follow: [LOCAL_VALIDATION_GUIDE.md](LOCAL_VALIDATION_GUIDE.md)
3. Troubleshoot: [LOCAL_VALIDATION_GUIDE.md#troubleshooting](LOCAL_VALIDATION_GUIDE.md#troubleshooting)

#### Understand the System
1. Read: [README.md](README.md)
2. Review: [SYSTEM_COMPLETE.md](SYSTEM_COMPLETE.md)
3. Study: [IMPLEMENTATION_GUIDE.md](.kiro/specs/community-forest-mapping/IMPLEMENTATION_GUIDE.md)

#### Deploy to Production
1. Review: [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)
2. Follow: [GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md)
3. Monitor: [PRODUCTION_READINESS.md#post-deployment-verification](PRODUCTION_READINESS.md#post-deployment-verification)

#### Understand SQLite Migration
1. Read: [SQLITE_MIGRATION_COMPLETE.md](SQLITE_MIGRATION_COMPLETE.md)
2. Review: [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)
3. Study: [SQLITE_MIGRATION_GUIDE.md](SQLITE_MIGRATION_GUIDE.md)

#### Run Tests
1. Backend: `cd backend && mvn test`
2. GIS Service: `cd gis-service && pytest tests/`
3. Frontend: `cd frontend && npm test`
4. See: [LOCAL_VALIDATION_GUIDE.md#running-tests](LOCAL_VALIDATION_GUIDE.md#running-tests)

#### Troubleshoot Issues
1. Check: [LOCAL_VALIDATION_GUIDE.md#troubleshooting](LOCAL_VALIDATION_GUIDE.md#troubleshooting)
2. Review: Application logs
3. See: [PRODUCTION_READINESS.md#support-and-troubleshooting](PRODUCTION_READINESS.md#support-and-troubleshooting)

---

## File Structure

```
community-forest-mapping/
├── README.md                           # Project overview
├── QUICK_START.md                      # 5-minute setup
├── LOCAL_VALIDATION_GUIDE.md           # Detailed local setup
├── SYSTEM_COMPLETE.md                  # System completion status
├── CHECKPOINT_VERIFICATION.md          # Implementation checklist
├── VALIDATION_SUMMARY.md               # Validation status
├── PRODUCTION_READINESS.md             # Production checklist
├── GITHUB_DEPLOYMENT_GUIDE.md          # GitHub deployment
├── SQLITE_MIGRATION_COMPLETE.md        # Migration completion
├── SQLITE_MIGRATION_GUIDE.md           # Migration details
├── MIGRATION_SUMMARY.md                # Migration summary
├── DOCUMENTATION_INDEX.md              # This file
├── INDEX.md                            # Architecture overview
│
├── .kiro/specs/community-forest-mapping/
│   ├── requirements.md                 # Feature requirements
│   ├── design.md                       # System design
│   ├── tasks.md                        # Implementation tasks
│   └── IMPLEMENTATION_GUIDE.md         # Architecture guide
│
├── backend/                            # Spring Boot backend
│   ├── pom.xml                         # Maven configuration (SQLite)
│   ├── src/main/resources/
│   │   └── application.yml             # Spring Boot config (SQLite)
│   └── src/main/java/com/cfm/
│       ├── model/
│       │   ├── Shapefile.java          # Updated for SQLite
│       │   ├── Compartment.java        # Updated for SQLite
│       │   └── SamplePlot.java         # Updated for SQLite
│       └── ...
│
├── gis-service/                        # Python GIS service
│   ├── src/
│   │   ├── main.py
│   │   ├── shapefile_parser.py
│   │   ├── dem_downloader.py
│   │   ├── slope_calculator.py
│   │   ├── aspect_calculator.py
│   │   ├── compartment_generator.py
│   │   ├── sample_plot_generator.py
│   │   ├── coordinate_converter.py
│   │   ├── dem_clipper.py
│   │   ├── map_renderer.py
│   │   └── error_handler.py
│   └── tests/
│
├── frontend/                           # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.ts
│   │   └── styles/
│   └── index.html
│
├── database/
│   └── schema.sql                      # SQLite schema
│
├── docker-compose.yml                  # Docker configuration (SQLite)
├── .env.example                        # Environment template (SQLite)
└── .gitignore
```

---

## Key Technologies

### Backend
- **Java 17** - Programming language
- **Spring Boot 3.1.5** - Web framework
- **Spring Data JPA** - ORM
- **SQLite** - Database (migrated from PostgreSQL)
- **Hibernate** - JPA implementation
- **JTS** - Geometry operations

### GIS Service
- **Python 3.9+** - Programming language
- **GDAL/OGR** - Geospatial data processing
- **Rasterio** - Raster data handling
- **Shapely** - Geometry operations
- **NumPy** - Numerical computing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool
- **Leaflet** - Map library
- **Axios** - HTTP client

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Maven** - Java build tool
- **npm** - Node package manager
- **pytest** - Python testing

---

## Database

### Current: SQLite
- **File**: `cfm.db`
- **Location**: Project root
- **Backup**: Single file copy
- **Suitable for**: Small to medium deployments

### Schema
- **shapefiles** - Uploaded boundary data
- **dems** - Digital elevation models
- **analysis_results** - Analysis results
- **compartments** - Forest compartments
- **sample_plots** - Sample plot locations
- **sessions** - User sessions
- **audit_logs** - Audit trail

---

## API Endpoints

### Session Management
- `POST /api/sessions/create` - Create session
- `GET /api/sessions/{id}/data` - Get session data
- `DELETE /api/sessions/{id}` - Delete session

### Compartments
- `GET /api/compartments` - List all
- `GET /api/compartments/{id}` - Get specific

### Sample Plots
- `GET /api/sample-plots` - List all
- `GET /api/sample-plots/{id}` - Get specific

### Export
- `GET /api/export/coordinates/csv` - CSV export
- `GET /api/export/coordinates/excel` - Excel export
- `POST /api/export/maps` - Map export

### Terrain Analysis
- `POST /api/terrain-analysis` - Start analysis
- `GET /api/terrain-analysis/{id}` - Get results

---

## Testing

### Test Coverage
- **Unit Tests**: 40+ tests
- **Property-Based Tests**: 18 tests
- **Integration Tests**: 2 test suites
- **Total**: 60+ automated tests

### Running Tests
```bash
# Backend
cd backend && mvn test

# GIS Service
cd gis-service && pytest tests/

# Frontend
cd frontend && npm test
```

---

## Deployment Options

### Local Development
- No external database needed
- SQLite created automatically
- See: [QUICK_START.md](QUICK_START.md)

### Docker
- All services containerized
- SQLite in volume
- See: [QUICK_START.md](QUICK_START.md)

### GitHub Pages + Backend Service
- Frontend on GitHub Pages
- Backend on Railway/Render/Fly.io
- See: [GITHUB_DEPLOYMENT_GUIDE.md](GITHUB_DEPLOYMENT_GUIDE.md)

### Production
- Full deployment checklist
- Monitoring and backups
- See: [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)

---

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

---

## Support & Troubleshooting

### Common Issues
- **Port already in use**: See [LOCAL_VALIDATION_GUIDE.md#troubleshooting](LOCAL_VALIDATION_GUIDE.md#troubleshooting)
- **Database errors**: See [LOCAL_VALIDATION_GUIDE.md#database-issues](LOCAL_VALIDATION_GUIDE.md#database-issues)
- **Build failures**: See [LOCAL_VALIDATION_GUIDE.md#maven-build-failed](LOCAL_VALIDATION_GUIDE.md#maven-build-failed)
- **Deployment issues**: See [GITHUB_DEPLOYMENT_GUIDE.md#troubleshooting](GITHUB_DEPLOYMENT_GUIDE.md#troubleshooting)

### Getting Help
1. Check relevant documentation
2. Review application logs
3. Check error messages
4. Review test output
5. Consult IMPLEMENTATION_GUIDE.md for architecture details

---

## Version Information

- **System Version**: 1.0.0
- **Database**: SQLite (cfm.db)
- **Java**: 17+
- **Node.js**: 18+
- **Python**: 3.9+
- **Status**: Production Ready
- **Last Updated**: 2026-02-08

---

## Quick Links

- [GitHub Repository](https://github.com/username/community-forest-mapping)
- [Live Demo](https://username.github.io/community-forest-mapping/)
- [API Documentation](http://localhost:8080/api/swagger-ui.html)
- [Issue Tracker](https://github.com/username/community-forest-mapping/issues)

---

## Document Maintenance

This index is maintained as the primary navigation point for all documentation. When adding new documentation:

1. Add entry to appropriate section
2. Update file structure if needed
3. Add to "Use Case" section if applicable
4. Update version/date if significant changes

---

**Last Updated**: 2026-02-08
**Maintained By**: Development Team
**Status**: Current and Complete
