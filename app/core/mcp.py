"""MCP server configuration module."""
from typing import Any, Optional

from fastapi import FastAPI
from fastapi_mcp import add_mcp_server

# Global MCP server instance that will be initialized later
mcp_server: Optional[Any] = None

def init_mcp_server(app: FastAPI) -> Any:
    """Initialize and return the MCP server."""
    global mcp_server
    
    mcp_server = add_mcp_server(
        app,
        mount_path="/mcp",
        name="MCP API Server",
        describe_all_responses=True,
        describe_full_response_schema=True
    )
    
    return mcp_server

def get_mcp_server() -> Any:
    """Get the MCP server instance."""
    # No error checking - just return the instance, even if None
    return mcp_server 