# Solar Analysis API - Makefile

.PHONY: help install dev test build run clean docker-dev docker-prod docker-clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  dev          - Run in development mode"
	@echo "  test         - Run tests"
	@echo "  build        - Build production Docker image"
	@echo "  run          - Run the application"
	@echo "  clean        - Clean up generated files"
	@echo "  docker-dev   - Run with Docker Compose (development)"
	@echo "  docker-prod  - Build and run production Docker image"
	@echo "  docker-clean - Clean up Docker containers and images"

# Python environment
install:
	pip install -r requirements.txt

install-test:
	pip install -r requirements-test.txt

# Development
dev:
	ENV=development python run.py

dev-old:
	uvicorn main.main:app --host 0.0.0.0 --port 8000 --reload

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src.api --cov=src.core --cov=src.utils

# Production
run:
	python run.py

# Docker commands
docker-dev:
	docker-compose -f docker/docker-compose.yml up --build

docker-dev-bg:
	docker-compose -f docker/docker-compose.yml up -d --build

docker-prod:
	docker build -f docker/Dockerfile.prod -t solsat-api:latest .
	docker run -p 8000:8000 --env ENV=production solsat-api:latest

# Build commands
build:
	./scripts/deploy/build.sh

build-dev:
	docker build -f docker/Dockerfile -t solsat-api:dev .

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf output/maps/*.html
	rm -rf output/overlays/*.png
	rm -rf output/reports/*.txt
	rm -rf output/reports/*.json

docker-clean:
	docker-compose -f docker/docker-compose.yml down --rmi all --volumes
	docker system prune -f

# Linting and formatting
install-dev:
	pip install -r requirements-test.txt

lint:
	python scripts/formatting/format_code.py --check

lint-report:
	python scripts/formatting/format_code.py --report

format:
	python scripts/formatting/format_code.py --fix

format-check:
	python scripts/formatting/format_code.py --check

pylint:
	python scripts/formatting/format_code.py --tool pylint

black:
	python scripts/formatting/format_code.py --tool black --fix

black-check:
	python scripts/formatting/format_code.py --tool black --check

isort:
	python scripts/formatting/format_code.py --tool isort --fix

isort-check:
	python scripts/formatting/format_code.py --tool isort --check

flake8:
	python scripts/formatting/format_code.py --tool flake8

mypy:
	python scripts/formatting/format_code.py --tool mypy

# Health check
health:
	curl -f http://localhost:8000/api/v1/health || echo "API not running"

# Documentation
docs:
	@echo "API Documentation available at:"
	@echo "  - Interactive: http://localhost:8000/docs"
	@echo "  - OpenAPI JSON: http://localhost:8000/openapi.json"
	@echo "  - OpenAPI YAML: http://localhost:8000/api/v1/openapi.yaml"