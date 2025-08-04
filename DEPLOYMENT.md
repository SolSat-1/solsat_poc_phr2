# Deployment Guide

This document provides instructions for deploying the Enhanced Solar Rooftop Analysis System.

## 📦 Package Structure

```
enhanced-solar-rooftop-analysis/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD pipeline
├── files/
│   └── .gitkeep                   # Output directory for generated files
├── .gitignore                     # Git ignore rules
├── CONTRIBUTING.md                # Contribution guidelines
├── DEPLOYMENT.md                  # This file
├── LICENSE                        # MIT License
├── README.md                      # Main documentation
├── demo_solar_analysis.py         # Demo script and main entry point
├── enhanced_solsat_system.py      # Enhanced visualization system
├── poc_solsat_data_layer.py       # Original data layer (legacy)
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup configuration
└── solar_prediction_engine.py     # Core prediction engine
```

## 🚀 Quick Deployment

### Local Development
```bash
# Clone the repository
git clone https://github.com/yourusername/enhanced-solar-rooftop-analysis.git
cd enhanced-solar-rooftop-analysis

# Set up environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Run the demo
python demo_solar_analysis.py
```

### Production Installation
```bash
# Install from PyPI (when published)
pip install enhanced-solar-rooftop-analysis

# Or install from source
pip install git+https://github.com/yourusername/enhanced-solar-rooftop-analysis.git
```

## 🐳 Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p files

# Expose port for web interface (if added)
EXPOSE 8000

# Run the application
CMD ["python", "demo_solar_analysis.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  solar-analysis:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./files:/app/files
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./files:/usr/share/nginx/html/files:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - solar-analysis
    restart: unless-stopped
```

## ☁️ Cloud Deployment

### AWS Deployment
```bash
# Using AWS Lambda
pip install zappa
zappa init
zappa deploy production

# Using AWS ECS
aws ecs create-cluster --cluster-name solar-analysis
# Configure task definition and service
```

### Google Cloud Platform
```bash
# Using Cloud Run
gcloud run deploy solar-analysis \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image solar-analysis .

# Deploy to Container Instances
az container create \
  --resource-group myResourceGroup \
  --name solar-analysis \
  --image myregistry.azurecr.io/solar-analysis:latest
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional configuration
export SOLAR_ELECTRICITY_RATE=0.12
export SOLAR_PANEL_COST=300
export SOLAR_INSTALLATION_COST=1.5
export SOLAR_MAINTENANCE_RATE=0.01
```

### Custom Configuration
```python
# config.py
SOLAR_CONFIG = {
    'panel_specs': {
        'power_rating': 400,
        'efficiency': 0.20,
        'area': 2.0,
    },
    'economic_params': {
        'electricity_rate': 0.12,
        'panel_cost': 300,
    }
}
```

## 📊 Monitoring and Logging

### Health Check Endpoint
```python
# Add to your deployment
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('solar_analysis.log'),
        logging.StreamHandler()
    ]
)
```

## 🔒 Security Considerations

### API Security
- Use HTTPS in production
- Implement rate limiting
- Add authentication for sensitive endpoints
- Validate all input data

### Data Protection
- Encrypt sensitive configuration
- Use environment variables for secrets
- Implement proper access controls
- Regular security updates

## 📈 Scaling

### Horizontal Scaling
- Use load balancers
- Implement caching (Redis/Memcached)
- Database clustering
- CDN for static files

### Performance Optimization
- Async processing for large datasets
- Background job queues (Celery)
- Database indexing
- Image optimization

## 🔄 CI/CD Pipeline

The included GitHub Actions workflow provides:
- Automated testing on Python 3.9, 3.10, 3.11
- Code quality checks (black, flake8, mypy)
- Security scanning (safety, bandit)
- Automated builds and deployments

### Deployment Triggers
- Push to `main` branch: Production deployment
- Push to `develop` branch: Staging deployment
- Pull requests: Testing and validation

## 📞 Support

For deployment issues:
1. Check the GitHub Issues
2. Review the logs
3. Contact the development team
4. Submit a bug report with deployment details

## 🔄 Updates

### Automated Updates
```bash
# Set up automated dependency updates
pip install dependabot-core
# Configure .github/dependabot.yml
```

### Manual Updates
```bash
# Update dependencies
uv pip install --upgrade -r requirements.txt

# Run tests
python demo_solar_analysis.py

# Deploy updates
git push origin main
```

---

**Ready for production deployment! 🚀**
