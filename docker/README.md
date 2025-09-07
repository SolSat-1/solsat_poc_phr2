# Docker Configuration

This directory contains all Docker-related configuration files for the Solar Analysis API.

## Files

- **Dockerfile**: Development Docker configuration
- **Dockerfile.prod**: Production-optimized multi-stage Docker build
- **docker-compose.yml**: Docker Compose configuration for local development
- **.dockerignore**: Files and directories to ignore during Docker builds
- **nginx.conf**: Nginx reverse proxy configuration

## Usage

### Development with Docker Compose

From the project root directory:

```bash
# Start the application with Docker Compose
docker-compose -f docker/docker-compose.yml up --build

# Run in background
docker-compose -f docker/docker-compose.yml up -d --build

# Stop the application
docker-compose -f docker/docker-compose.yml down
```

### Production Build

```bash
# Build production image from project root
docker build -f docker/Dockerfile.prod -t solsat-api:latest .

# Run production container
docker run -p 8000:8000 --env ENV=production solsat-api:latest
```

### Development Build

```bash
# Build development image from project root
docker build -f docker/Dockerfile -t solsat-api:dev .

# Run development container
docker run -p 8000:8000 --env ENV=development solsat-api:dev
```

## Environment Variables

- `ENV`: Set to `production` or `development`
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `PORT`: Port to run on (default: `8000`)

## Notes

- All Docker commands should be run from the project root directory
- The application will be available at `http://localhost:8000`
- Health check endpoint: `http://localhost:8000/api/v1/health`
- API documentation: `http://localhost:8000/docs`
