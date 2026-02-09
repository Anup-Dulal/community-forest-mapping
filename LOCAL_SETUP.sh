#!/bin/bash

# Community Forest Mapping - Local Setup Script
# This script sets up and runs all three services locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MAVEN_PATH="/tmp/apache-maven-3.9.6/bin"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
GIS_SERVICE_DIR="$PROJECT_ROOT/gis-service"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Community Forest Mapping - Local Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check Java
if ! command -v java &> /dev/null; then
    echo -e "${RED}✗ Java not found${NC}"
    exit 1
fi
JAVA_VERSION=$(java -version 2>&1 | head -1)
echo -e "${GREEN}✓ Java: $JAVA_VERSION${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi
NODE_VERSION=$(node -v)
echo -e "${GREEN}✓ Node.js: $NODE_VERSION${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found${NC}"
    exit 1
fi
NPM_VERSION=$(npm -v)
echo -e "${GREEN}✓ npm: $NPM_VERSION${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# Check Maven
if [ ! -f "$MAVEN_PATH/mvn" ]; then
    echo -e "${YELLOW}Maven not found at $MAVEN_PATH, downloading...${NC}"
    curl -s https://archive.apache.org/dist/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz -o /tmp/maven.tar.gz
    tar -xzf /tmp/maven.tar.gz -C /tmp
    echo -e "${GREEN}✓ Maven downloaded${NC}"
else
    echo -e "${GREEN}✓ Maven found${NC}"
fi

export PATH="$MAVEN_PATH:$PATH"

echo ""
echo -e "${YELLOW}Setting up environment...${NC}"

# Create .env if it doesn't exist
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo -e "${YELLOW}Building Backend...${NC}"
echo "This may take a few minutes on first run..."

if mvn -f "$BACKEND_DIR/pom.xml" clean package -q -DskipTests; then
    echo -e "${GREEN}✓ Backend built successfully${NC}"
else
    echo -e "${RED}✗ Backend build failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Setting up GIS Service...${NC}"

# Create Python virtual environment
if [ ! -d "$GIS_SERVICE_DIR/venv" ]; then
    python3 -m venv "$GIS_SERVICE_DIR/venv"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment and install dependencies
source "$GIS_SERVICE_DIR/venv/bin/activate"
pip install -q -r "$GIS_SERVICE_DIR/requirements.txt" 2>/dev/null || true
echo -e "${GREEN}✓ GIS Service dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Setting up Frontend...${NC}"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    npm install -q --prefix "$FRONTEND_DIR"
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies exist${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}To start the services, run:${NC}"
echo ""
echo -e "${BLUE}Terminal 1 - Backend:${NC}"
echo "  export PATH=\"$MAVEN_PATH:\$PATH\""
echo "  cd $BACKEND_DIR"
echo "  mvn spring-boot:run"
echo ""
echo -e "${BLUE}Terminal 2 - GIS Service:${NC}"
echo "  source $GIS_SERVICE_DIR/venv/bin/activate"
echo "  cd $GIS_SERVICE_DIR"
echo "  python src/main.py"
echo ""
echo -e "${BLUE}Terminal 3 - Frontend:${NC}"
echo "  cd $FRONTEND_DIR"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Then open your browser to:${NC}"
echo "  http://localhost:3000"
echo ""
echo -e "${YELLOW}API Documentation:${NC}"
echo "  http://localhost:8080/api/swagger-ui.html"
echo ""
