# Community Forest Mapping and Terrain Analysis System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://www.oracle.com/java/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2.5-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)

A full-stack GIS web application that automates the generation of forestry analysis maps from community forest boundary shapefiles. Upload a shapefile, and the system automatically processes terrain data, generates compartments, creates sample plots, and exports professional forestry maps.

## ✨ Key Features

### 🗂️ Archive Support
- **RAR5 Support**: Pure Java implementation using unrar5j (no native dependencies)
- **RAR4 Support**: JUnRAR library integration
- **ZIP Support**: Apache Commons Compress
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Automatic Detection**: Magic byte-based format detection
- **Recursive Extraction**: Handles nested directories in archives

### 🗺️ GIS Processing
- **Automatic DEM Download**: Fetches elevation data from SRTM/OpenTopography
- **Terrain Analysis**: Calculates slope (0-20°, 20-30°, >30°) and aspect (8 directions)
- **Compartment Division**: Equal-area forest subdivision algorithm
- **Sample Plot Generation**: 2% sampling intensity with systematic distribution
- **Map Rendering**: Professional forestry-standard layouts with legends, scale bars, north arrows

### 📊 Export Capabilities
- **PNG/PDF Maps**: High-quality map exports for reports
- **Excel/CSV**: Sample plot coordinates for field work
- **Multiple Formats**: Flexible export options for different use cases

### 🚀 Deployment Ready
- **Docker Compose**: One-command deployment
- **Self-contained**: No cloud dependencies
- **Free Hosting Compatible**: Deploy to Render, Railway, Fly.io, Heroku
- **SQLite Database**: Lightweight, portable database

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                 │
│              Upload → Visualize → Export                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│                Backend (Spring Boot + Java 17)                   │
│  Archive Processing → Validation → Database → Export             │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────────┐
│           GIS Service (Python + GDAL + GeoPandas)                │
│  DEM Download → Terrain Analysis → Compartments → Sample Plots   │
└──────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (recommended) - [Download here](https://www.docker.com/products/docker-desktop)
- OR manually install:
  - Java 17+
  - Node.js 18+
  - Python 3.9+
  - GDAL 3.7+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Anup-Dulal/community-forest-mapping.git
cd community-forest-mapping

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8080
# GIS Service: http://localhost:8001
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
mvn clean package
java -jar target/community-forest-mapping-1.0.0.jar
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**GIS Service:**
```bash
cd gis-service
pip install -r requirements.txt
python src/main.py
```

## 📖 Usage

1. **Upload Shapefile**: 
   - Drag and drop a RAR5/RAR4/ZIP archive containing shapefile components
   - Or select individual .shp, .shx, .dbf, .prj files

2. **Automatic Processing**:
   - System extracts bounding box
   - Downloads DEM data
   - Calculates slope and aspect
   - Generates compartments and sample plots

3. **Download Results**:
   - PNG/PDF maps for reports
   - Excel/CSV coordinates for field work

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React 18, TypeScript 5, Vite, Zustand |
| **Backend** | Spring Boot 3.2.5, Java 17, SQLite |
| **GIS Processing** | Python 3.9, GDAL, GeoPandas, Rasterio |
| **Archive Support** | unrar5j (RAR5), JUnRAR (RAR4), Commons Compress (ZIP) |
| **Containerization** | Docker, Docker Compose |

## 📁 Project Structure

```
community-forest-mapping/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   └── store/           # State management
│   └── package.json
├── backend/                  # Spring Boot application
│   ├── src/main/java/com/cfm/
│   │   ├── archive/         # RAR5/RAR4/ZIP extraction
│   │   ├── controller/      # REST endpoints
│   │   ├── service/         # Business logic
│   │   └── repository/      # Data access
│   └── pom.xml
├── gis-service/              # Python GIS microservice
│   ├── src/
│   │   ├── dem_downloader.py
│   │   ├── slope_calculator.py
│   │   ├── aspect_calculator.py
│   │   ├── compartment_generator.py
│   │   └── sample_plot_generator.py
│   └── requirements.txt
├── docker-compose.yml        # Docker orchestration
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Optional: API keys for DEM download
OPENTOPOGRAPHY_API_KEY=your_key_here
NASA_API_KEY=your_key_here

# Optional: Google Maps API key for basemap
GOOGLE_MAPS_API_KEY=your_key_here
```

### Application Configuration

Backend configuration in `backend/src/main/resources/application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:sqlite:cfm.db
  servlet:
    multipart:
      max-file-size: 100MB
      max-request-size: 100MB

server:
  port: 8080
  servlet:
    context-path: /api
```

## 🧪 Testing

### Run All Tests

```bash
# Backend tests
cd backend && mvn test

# Frontend tests
cd frontend && npm test

# GIS service tests
cd gis-service && pytest
```

### Property-Based Tests

The project includes property-based tests for critical functionality:
- Shapefile completeness validation
- Equal-area compartment distribution
- Sample plot constraints
- Coordinate conversion accuracy

## 📦 Deployment

### Free Hosting Options

1. **Render.com** (Recommended)
   - Supports Docker
   - Free tier available
   - Automatic deployments from GitHub

2. **Railway.app**
   - Docker support
   - Free tier with 500 hours/month
   - Easy GitHub integration

3. **Fly.io**
   - Docker-native platform
   - Free tier available
   - Global deployment

### Deployment Steps

```bash
# 1. Push to GitHub (already done!)
git push origin main

# 2. Connect to hosting platform
# - Link your GitHub repository
# - Select docker-compose.yml
# - Deploy!
```

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8080  # Backend
lsof -i :3000  # Frontend
lsof -i :8001  # GIS Service

# Kill the process
kill -9 <PID>
```

**Docker build fails:**
```bash
# Clean Docker cache
docker-compose down -v
docker system prune -a
docker-compose up --build
```

**RAR5 extraction fails:**
- Check backend logs for detailed error messages
- Verify the RAR5 file is not corrupted
- Ensure the archive contains all required shapefile components

## 📝 API Documentation

### Upload Shapefile

```http
POST /api/shapefile/upload
Content-Type: multipart/form-data

files: [shapefile components or archive]
```

### Get Shapefile

```http
GET /api/shapefile/{id}
```

### Export Maps

```http
POST /api/maps/export/slope?analysisResultId={id}&format=png
POST /api/maps/export/aspect?analysisResultId={id}&format=pdf
POST /api/maps/export/compartment?analysisResultId={id}&format=png
POST /api/maps/export/sample-plots?analysisResultId={id}&format=png
```

### Export Coordinates

```http
GET /api/export/coordinates/csv?analysisResultId={id}
GET /api/export/coordinates/excel?analysisResultId={id}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Anup Dulal**
- GitHub: [@Anup-Dulal](https://github.com/Anup-Dulal)

## 🙏 Acknowledgments

- SRTM/OpenTopography for DEM data
- unrar5j library for RAR5 support
- Spring Boot and React communities
- GDAL and GeoPandas projects

## 📞 Support

For issues and questions:
- Open an issue on [GitHub Issues](https://github.com/Anup-Dulal/community-forest-mapping/issues)
- Check existing documentation in the `/docs` folder

---

**Made with ❤️ for forestry professionals**
