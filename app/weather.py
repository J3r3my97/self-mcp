"""Weather MCP Server for providing weather information via NWS API."""
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url, 
                headers={"Accept": "application/geo+json"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    try:
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_request(forecast_url)

        if not forecast_data:
            return "Unable to fetch detailed forecast."

        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}"""
            forecasts.append(forecast)

        return "\n---\n".join(forecasts)
    except KeyError:
        return "Error processing forecast data"

if __name__ == "__main__":
    mcp.run(transport='stdio') 