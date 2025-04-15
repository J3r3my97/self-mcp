"""National Weather Service API utilities."""
from typing import Any, Dict, Optional

import httpx

# Constants
REQUEST_TIMEOUT = 30.0  # seconds
USER_AGENT = "(Weather MCP Server, contact@example.com)"

async def make_nws_request(url: str) -> Optional[Dict[str, Any]]:
    """Make a request to the NWS API with proper headers."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making NWS request: {e}")
            return None

def format_alert(alert: Dict[str, Any]) -> str:
    """Format a weather alert into a readable string."""
    properties = alert.get("properties", {})
    return f"""
Alert: {properties.get('event', 'Unknown Event')}
Area: {properties.get('areaDesc', 'Unknown Area')}
Severity: {properties.get('severity', 'Unknown')}
Description: {properties.get('description', 'No description available')}
Instructions: {properties.get('instruction', 'No specific instructions provided')}
""" 