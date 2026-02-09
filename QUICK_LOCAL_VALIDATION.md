# Quick Local Validation - Community Forest Mapping

## Status: Lombok Annotation Processing Issue

There's a compatibility issue between Java 25 and Lombok's annotation processor. This is a known issue with newer Java versions.

## Workaround: Run Frontend & GIS Service Only

You can still validate the system by running the frontend and GIS service, which don't have this issue.

### Step 1: Start GIS Service

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

The GIS Service will be available at: **http://localhost:8001**

### Step 2: Start Frontend

In a new terminal:

```bash
cd community-forest-mapping/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The Frontend will be available at: **http://localhost:3000**

### Step 3: Verify Services

#### Check GIS Service Health
```bash
curl http://localhost:8001/health
```

#### Check Frontend
Open http://localhost:3000 in your browser

You should see the Community Forest Mapping dashboard with:
- Map viewer
- Upload panel
- Tools panel
- Layers panel
- Export dialog

## Backend Build Issue

The backend has a Lombok annotation processing issue with Java 25. To fix this, you have two options:

### Option 1: Use Java 17 (Recommended)

Install Java 17 and set it as default:

```bash
# macOS with Homebrew
brew install openjdk@17
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"

# Verify
java -version
```

Then try building again:

```bash
export PATH="/tmp/apache-maven-3.9.6/bin:$PATH"
cd community-forest-mapping/backend
mvn clean package -DskipTests
```

### Option 2: Disable Lombok and Add Manual Getters/Setters

Remove `@Data` and `@Slf4j` annotations and add manual getters/setters to model classes.

## Testing Without Backend

You can still test the frontend and GIS service:

### Frontend Tests
```bash
cd community-forest-mapping/frontend
npm test
```

### GIS Service Tests
```bash
cd community-forest-mapping/gis-service
source venv/bin/activate
pytest tests/
```

## What Works

✅ Frontend (React) - Fully functional
✅ GIS Service (Python) - Fully functional
✅ Database (SQLite) - Ready to use
❌ Backend (Spring Boot) - Lombok annotation processing issue

## Next Steps

1. **Install Java 17** to fix the backend build issue
2. **Run GIS Service** to test geospatial processing
3. **Run Frontend** to test UI
4. **Build Backend** once Java 17 is installed
5. **Run complete system** with all three services

## Support

For more information:
- See `LOCAL_VALIDATION_GUIDE.md` for detailed setup
- See `QUICK_START.md` for quick reference
- See `SQLITE_MIGRATION_GUIDE.md` for database info

---

**Status**: Frontend & GIS Service Ready
**Backend**: Requires Java 17 for Lombok processing
**Database**: SQLite (cfm.db) - Ready
