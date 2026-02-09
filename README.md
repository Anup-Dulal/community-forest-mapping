# Community Forest Mapping and Terrain Analysis System

A full-stack GIS web application that automates the generation of forestry analysis maps from community forest boundary shapefiles.

## Features

- **Shapefile Upload**: Upload and validate community forest boundary shapefiles
- **Automatic DEM Download**: Automatically download and process Digital Elevation Model data
- **Terrain Analysis**: Calculate slope and aspect from DEM data
- **Compartment Division**: Automatically divide forest into equal-area compartments
- **Sample Plot Generation**: Generate systematic sample plots for forest inventory
- **Map Export**: Export professional forestry-standard maps as PDF/PNG
- **Coordinate Export**: Export sample plot coordinates as CSV/Excel

## Technology Stack

- **Frontend**: React + TypeScript + Leaflet
- **Backend**: Java Spring Boot
- **GIS Processing**: Python with GDAL/GeoPandas
- **Database**: PostgreSQL with PostGIS
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Java 17+ (for local backend development)
- Python 3.9+ (for local GIS service development)

### Setup

1. Clone the repository
```bash
git clone https://github.com/your-org/community-forest-mapping.git
cd community-forest-mapping
```

2. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services with Docker Compose
```bash
docker-compose up -d
```

4. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- GIS Service: http://localhost:8001
- Database: localhost:5432

## Project Structure

```
community-forest-mapping/
├── frontend/                 # React TypeScript application
├── backend/                  # Spring Boot application
├── gis-service/              # Python microservice
├── database/                 # Database initialization scripts
├── docker-compose.yml        # Docker Compose configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
mvn spring-boot:run
```

### GIS Service Development
```bash
cd gis-service
pip install -r requirements.txt
python src/main.py
```

## API Documentation

API documentation is available at `http://localhost:8080/swagger-ui.html` when the backend is running.

## Testing

### Frontend Tests
```bash
cd frontend
npm test
```

### Backend Tests
```bash
cd backend
mvn test
```

### GIS Service Tests
```bash
cd gis-service
pytest
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
