"""Start the MCP weather server."""
from app.weather import mcp

if __name__ == "__main__":
    mcp.run(transport='stdio') 