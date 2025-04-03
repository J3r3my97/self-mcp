from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "MCP App"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    
    # CORS settings
    CORS_ORIGINS: str = "*"
    
    # API Keys (can be overridden with environment variables)
    ANTHROPIC_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings():
    """Dependency for getting application settings."""
    return Settings() 