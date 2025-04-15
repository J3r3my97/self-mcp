"""Tests for the Weather MCP Server API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_weather_forecast():
    """Test the weather forecast endpoint."""
    # Test valid coordinates (San Francisco)
    response = client.post(
        "/mcp/tools/get_weather_forecast",
        json={"latitude": 37.7749, "longitude": -122.4194}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)
    assert "Temperature" in response.json()

    # Test invalid coordinates
    response = client.post(
        "/mcp/tools/get_weather_forecast",
        json={"latitude": 91, "longitude": 0}  # Invalid latitude
    )
    assert response.status_code == 422

def test_get_weather_alerts():
    """Test the weather alerts endpoint."""
    # Test valid state code
    response = client.post(
        "/mcp/tools/get_weather_alerts",
        json={"state": "CA"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)

    # Test invalid state code
    response = client.post(
        "/mcp/tools/get_weather_alerts",
        json={"state": "INVALID"}
    )
    assert response.status_code == 422

def test_get_current_conditions():
    """Test the current conditions endpoint."""
    # Test valid coordinates (New York City)
    response = client.post(
        "/mcp/tools/get_current_conditions",
        json={"latitude": 40.7128, "longitude": -74.0060}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)
    assert "Temperature" in response.json()

    # Test invalid coordinates
    response = client.post(
        "/mcp/tools/get_current_conditions",
        json={"latitude": 0, "longitude": 181}  # Invalid longitude
    )
    assert response.status_code == 422 