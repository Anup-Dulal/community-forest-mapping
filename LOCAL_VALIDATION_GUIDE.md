# Local Validation Guide: Community Forest Mapping System

## Prerequisites

Before running the system locally, ensure you have the following installed:

### Required
- Java 17+ (for Spring Boot 3.x)
- Maven 3.8+
- Node.js 18+ (for React frontend)
- Python 3.9+ (for GIS service)
- Docker & Docker Compose (optional, for containerized setup)

### Optional
- Git (for version control)
- IDE (IntelliJ IDEA, VS Code, etc.)

## Installation Steps

### 1. Install Java
```bash
# macOS
brew install openjdk@17

# Linux (Ubuntu/Debian)
sudo apt-get install openjdk-17-jdk

# Verify installation
java -version
```

### 2. Install Maven
```bash
# macOS
brew install maven

# Linux (Ubuntu/Debian)
sudo apt-get install maven

# Verify installation
mvn -version
```

### 3. Install Node.js
```bash
# macOS
brew install node

# Linux (Ubuntu/Debian)
sudo apt-get install nodejs npm

# Verify installation
node -v
npm -v
```

### 4. Install Python
```bash
# macOS
brew install python@3.11

# Linux (Ubuntu/Debian)
sudo apt-get install python3.11 python3-pip

# Verify installation
python3 --version
pip3 --version
```

## Local Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd community-forest-mapping
```

### 2. Create Environment File
```bash
cp .env.example .env
```

The `.env` file contains SQLite database configuration. No additional database setup is needed - SQLite will create the database file automatically on first run.

### 3. Backend Setup

#### Build Backend
```bash
cd community-forest-mapping/backend

# Clean and build
mvn clean install

# This will:
# - Download all dependencies
# - Compile Java code
# - Run unit tests
# - Package the application
```

#### Run Backend
```bash
# Start Spring Boot application
mvn spring-boot:run

# Or run the packaged JAR
java -jar target/community-forest-mapping-1.0.0.jar
```

Backend will be available at: **http://localhost:8080**

The SQLite database file `cfm.db` will be created automatically in the project root on first run.

#### Verify Backend
```bash
# Check if backend is running
curl http://localhost:8080/api/swagger-ui.html

# View API documentation
# Open http://localhost:8080/api/swagger-ui.html in browser
```

### 4. GIS Service Setup

#### Create Python Virtual Environment
```bash
cd community-forest-mapping/gis-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

#### Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Run GIS Service
```bash
# Start the service
python src/main.py

# Service will start on http://localhost:8001
```

#### Verify GIS Service
```bash
# In another terminal, test the service
curl http://localhost:8001/health

# Or check specific endpoints
curl http://localhost:8001/api/shapefile/validate
```

### 5. Frontend Setup

#### Install Dependencies
```bash
cd community-forest-mapping/frontend

# Install npm packages
npm install
```

#### Run Frontend
```bash
# Start development server
npm run dev

# Or build for production
npm run build
```

Frontend will be available at: **http://localhost:3000**

#### Verify Frontend
```bash
# Open browser and navigate to
http://localhost:3000

# You should see the Community Forest Mapping dashboard
```

## Running Tests

### Backend Tests
```bash
cd community-forest-mapping/backend

# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=ShapefileUploadServiceTest

# Run with coverage
mvn test jacoco:report
```

### GIS Service Tests
```bash
cd community-forest-mapping/gis-service
source venv/bin/activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_shapefile_parser.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

### Frontend Tests
```bash
cd community-forest-mapping/frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## Complete Workflow Test

### Step 1: Prepare Test Data
```bash
# Create test directory
mkdir -p test_data

# You'll need a shapefile with these files:
# - boundary.shp (geometry)
# - boundary.shx (index)
# - boundary.dbf (attributes)
# - boundary.prj (projection)
```

### Step 2: Start All Services
```bash
# Terminal 1: Backend
cd community-forest-mapping/backend
mvn spring-boot:run

# Terminal 2: GIS Service
cd community-forest-mapping/gis-service
source venv/bin/activate
python src/main.py

# Terminal 3: Frontend
cd community-forest-mapping/frontend
npm run dev
```

### Step 3: Test in Browser
1. Open http://localhost:3000
2. Click "Upload" button
3. Select your test shapefile
4. Verify upload succeeds
5. Wait for DEM download (30-60 seconds)
6. Verify terrain analysis completes
7. Check compartments and sample plots appear
8. Test export functionality

### Step 4: Verify Data Persistence
```bash
# Check SQLite database
sqlite3 cfm.db

# List tables
.tables

# Query sample data
SELECT COUNT(*) FROM shapefiles;
SELECT COUNT(*) FROM compartments;
SELECT COUNT(*) FROM sample_plots;

# Exit
.quit
```

## Troubleshooting

### Backend Issues

#### Port 8080 Already in Use
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port
mvn spring-boot:run -Dspring-boot.run.arguments="--server.port=8081"
```

#### Database Connection Error
```bash
# Check if cfm.db exists
ls -la cfm.db

# If not, backend will create it on startup
# Check backend logs for errors
tail -f logs/application.log
```

#### Maven Build Fails
```bash
# Clear Maven cache
mvn clean
rm -rf ~/.m2/repository

# Rebuild
mvn clean install -U
```

#### Tests Fail
```bash
# Run tests with debug output
mvn test -X

# Run single test
mvn test -Dtest=TestClassName#testMethodName
```

### GIS Service Issues

#### Port 8001 Already in Use
```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>

# Or modify port in gis-service/src/main.py
```

#### Python Dependencies Missing
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for conflicts
pip check
```

#### Service Won't Start
```bash
# Check Python version
python3 --version

# Verify virtual environment is activated
which python

# Check logs
python src/main.py 2>&1 | tee gis-service.log
```

### Frontend Issues

#### Port 3000 Already in Use
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
npm run dev -- --port 3001
```

#### Dependencies Won't Install
```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Build Fails
```bash
# Check Node version
node -v

# Rebuild
npm run build

# Check for errors
npm run build 2>&1 | tee build.log
```

### Database Issues

#### SQLite Database Corrupted
```bash
# Backup old database
mv cfm.db cfm.db.backup

# Backend will create new database on startup
mvn spring-boot:run
```

#### Check Database Integrity
```bash
# Verify database
sqlite3 cfm.db "PRAGMA integrity_check;"

# Vacuum database
sqlite3 cfm.db "VACUUM;"
```

## Performance Monitoring

### Monitor Backend
```bash
# Check memory usage
jps -l

# Monitor with jconsole
jconsole

# Check logs
tail -f logs/application.log
```

### Monitor GIS Service
```bash
# Check process
ps aux | grep python

# Monitor with top
top -p <PID>
```

### Monitor Frontend
```bash
# Check browser console for errors
# Open DevTools: F12 or Cmd+Option+I

# Check network requests
# Network tab in DevTools
```

## Database Inspection

### Using SQLite CLI
```bash
# Connect to database
sqlite3 cfm.db

# List all tables
.tables

# Show schema
.schema

# Query data
SELECT * FROM shapefiles LIMIT 5;
SELECT * FROM compartments LIMIT 5;
SELECT * FROM sample_plots LIMIT 5;

# Export data
.mode csv
.output data.csv
SELECT * FROM shapefiles;
.quit
```

### Using SQLite Browser
```bash
# Install SQLite Browser
brew install sqlitebrowser

# Open database
sqlitebrowser cfm.db
```

## Validation Checklist

- [ ] Java 17+ installed and working
- [ ] Maven 3.8+ installed and working
- [ ] Node.js 18+ installed and working
- [ ] Python 3.9+ installed and working
- [ ] Repository cloned successfully
- [ ] .env file created
- [ ] Backend builds without errors
- [ ] Backend starts successfully
- [ ] GIS Service starts successfully
- [ ] Frontend starts successfully
- [ ] All services accessible via HTTP
- [ ] Database file created (cfm.db)
- [ ] Can upload shapefile
- [ ] Can download DEM
- [ ] Can generate compartments
- [ ] Can generate sample plots
- [ ] Can export data
- [ ] All tests pass

## Next Steps

1. Complete all setup steps above
2. Run the complete workflow test
3. Verify all services are working
4. Check database contains expected data
5. Review logs for any warnings
6. Proceed to PRODUCTION_READINESS.md for deployment

## Support

For additional help:
- Check QUICK_START.md for quick reference
- Review IMPLEMENTATION_GUIDE.md for architecture details
- Check application logs for error messages
- Review test output for specific failures

---

**Last Updated**: 2026-02-08
**Database**: SQLite (cfm.db)
**Status**: Ready for Local Testing
