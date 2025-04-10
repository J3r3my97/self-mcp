# app/main.py
import logging

from fastapi import FastAPI, HTTPException
from fastapi_mcp import add_mcp_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AI Model API",
        description="API for interacting with various AI models through a unified interface",
        version="1.0.0"
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint to verify service status."""
        try:
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=500, detail="Service unhealthy")

    # Initialize MCP server
    try:
        logger.info("Initializing MCP server...")
        mcp_server = add_mcp_server(
            app,
            mount_path="/mcp",
            name="AI Model API",
            describe_all_responses=True,
            describe_full_response_schema=True
        )
        logger.info("MCP server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        raise

    return app

app = create_app()

if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("Starting server...")
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise