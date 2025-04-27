import base64
import json
import os
from typing import Any, Dict, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Gate-Release.io"
    PROJECT_ID: str = "bubbleit-dev"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Authentication Settings
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 100

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Security Settings
    ALLOWED_HOSTS: List[str] = ["*"]
    MAX_REQUESTS_PER_MINUTE: int = 60
    ENABLE_HTTPS_REDIRECT: bool = False

    # Firebase Settings
    FIREBASE_DATABASE_URL: str = "https://bubbleit-dev-default-rtdb.firebaseio.com"
    FIREBASE_STORAGE_BUCKET: str = "bubbleit-dev.firebasestorage.app"
    FIREBASE_SERVICE_ACCOUNT: Optional[Dict[str, Any]] = None

    # Model Settings
    MODEL_DEVICE: str = "cuda"  # or "cpu"
    CONFIDENCE_THRESHOLD: float = 0.7

    # Storage Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Compression Settings
    GZIP_MIN_SIZE: int = 1000  # bytes

    # API Keys (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None

    @field_validator(
        "CORS_ORIGINS", "CORS_METHODS", "CORS_HEADERS", "ALLOWED_HOSTS", mode="before"
    )
    @classmethod
    def parse_list(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma and strip whitespace
                return [x.strip() for x in v.split(",")]
        return v

    @field_validator("FIREBASE_SERVICE_ACCOUNT", mode="before")
    @classmethod
    def parse_service_account(cls, v):
        if isinstance(v, str):
            try:
                # Try to decode base64 if it's encoded
                try:
                    decoded = base64.b64decode(v).decode("utf-8")
                    return json.loads(decoded)
                except:
                    # If not base64, try to parse as JSON directly
                    return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "APP_"
        env_nested_delimiter = "__"


settings = Settings()
