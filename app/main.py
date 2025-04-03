# app/main.py
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.utils.logging import setup_logging
from app.utils.settings import get_settings


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    # Set up logging
    setup_logging(settings.LOG_LEVEL)
    
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description="Model Context Protocol (MCP) API for interacting with different LLMs",
        version="0.1.0",
        debug=settings.DEBUG,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "app": settings.APP_NAME,
            "version": "0.1.0",
            "status": "running"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    # Use port from settings instead of directly from environment
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)