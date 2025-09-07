"""
Tests for the Solar Analysis API
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_openapi_yaml():
    """Test OpenAPI YAML endpoint"""
    response = client.get("/api/v1/openapi.yaml")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_solar_analysis():
    """Test solar analysis endpoint"""
    test_data = {
        "polygon_coordinates": [
            {"longitude": 100.540148, "latitude": 13.671842},
            {"longitude": 100.540164, "latitude": 13.671602},
            {"longitude": 100.540577, "latitude": 13.67167},
        ],
        "monthly_consumption_kwh": 500,
    }

    response = client.post("/api/v1/analyze", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_invalid_polygon():
    """Test analysis with invalid polygon (less than 3 points)"""
    test_data = {
        "polygon_coordinates": [
            {"longitude": 100.540148, "latitude": 13.671842},
            {"longitude": 100.540164, "latitude": 13.671602},
        ],
        "monthly_consumption_kwh": 500,
    }

    response = client.post("/api/v1/analyze", json=test_data)
    assert response.status_code == 422  # Validation error


def test_geojson_analysis():
    """Test GeoJSON analysis endpoint"""
    test_data = {
        "polygons_data": [
            {
                "polygon_coordinates": [
                    {"longitude": 100.540148, "latitude": 13.671842},
                    {"longitude": 100.540164, "latitude": 13.671602},
                    {"longitude": 100.540577, "latitude": 13.67167},
                ],
                "monthly_consumption_kwh": 500,
            }
        ]
    }

    response = client.post("/api/v1/analyze/geojson", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["type"] == "FeatureCollection"
    assert "features" in data


if __name__ == "__main__":
    pytest.main([__file__])
