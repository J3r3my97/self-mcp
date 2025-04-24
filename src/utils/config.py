from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Gate-Release.io"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "*"
    
    # Firebase Settings
    FIREBASE_DATABASE_URL: str = "https://bubbleit-dev-default-rtdb.firebaseio.com"
    FIREBASE_STORAGE_BUCKET: str = "bubbleit-dev.firebasestorage.app"
    
    # Model Settings
    MODEL_DEVICE: str = "cuda"  # or "cpu"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Storage Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # API Keys (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 