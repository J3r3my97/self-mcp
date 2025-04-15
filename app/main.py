"""Weather MCP Server main application."""
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import add_mcp_server
from pydantic import BaseModel, Field

from app.utils.nws import format_alert, make_nws_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
NWS_API_BASE = "https://api.weather.gov"

# Initialize FastAPI app
app = FastAPI(
    title="Weather MCP Server",
    description="MCP-compliant server for weather information",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp = add_mcp_server(
    app,
    mount_path="/mcp",
    name="Weather Information Service",
    describe_all_responses=True,
    describe_full_response_schema=True
)

@mcp.tool()
async def get_weather_forecast(latitude: float = Field(..., ge=-90, le=90), 
                             longitude: float = Field(..., ge=-180, le=180)) -> str:
    """Get weather forecast for a specific location.
    
    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    
    Returns:
        A formatted string containing the weather forecast
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        raise HTTPException(status_code=500, detail="Unable to fetch forecast data")

    # Get the forecast URL from the points response
    try:
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_request(forecast_url)

        if not forecast_data:
            raise HTTPException(status_code=500, detail="Unable to fetch detailed forecast")

        # Format the periods into a readable forecast
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
            forecasts.append(forecast)

        return "\n---\n".join(forecasts)
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Invalid data format: {str(e)}")

@mcp.tool()
async def get_weather_alerts(state: str = Field(..., min_length=2, max_length=2, description="Two-letter US state code")) -> str:
    """Get active weather alerts for a US state.
    
    Args:
        state: Two-letter US state code (e.g., CA, NY)
    
    Returns:
        A formatted string containing active weather alerts
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        raise HTTPException(status_code=500, detail="Unable to fetch alerts")

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_current_conditions(latitude: float = Field(..., ge=-90, le=90),
                               longitude: float = Field(..., ge=-180, le=180)) -> str:
    """Get current weather conditions for a specific location.
    
    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
    
    Returns:
        A formatted string containing current weather conditions
    """
    # First get the station endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        raise HTTPException(status_code=500, detail="Unable to fetch location data")

    try:
        # Get the observations URL from the points response
        station_url = points_data["properties"]["observationStations"]
        stations_data = await make_nws_request(station_url)

        if not stations_data or not stations_data.get("features"):
            raise HTTPException(status_code=500, detail="No weather stations found")

        # Get the first station
        station_id = stations_data["features"][0]["properties"]["stationIdentifier"]
        observations_url = f"{NWS_API_BASE}/stations/{station_id}/observations/latest"
        
        obs_data = await make_nws_request(observations_url)
        if not obs_data:
            raise HTTPException(status_code=500, detail="Unable to fetch current conditions")

        props = obs_data["properties"]
        
        return f"""
Current Conditions at {props.get('station', 'Unknown Station')}:
Temperature: {props.get('temperature', {}).get('value', 'N/A')}°C
Humidity: {props.get('relativeHumidity', {}).get('value', 'N/A')}%
Wind Speed: {props.get('windSpeed', {}).get('value', 'N/A')} km/h
Wind Direction: {props.get('windDirection', {}).get('value', 'N/A')}°
Description: {props.get('textDescription', 'No description available')}
Last Updated: {props.get('timestamp', 'Unknown')}
"""
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Invalid data format: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)