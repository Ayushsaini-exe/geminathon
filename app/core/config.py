"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the AgroFix platform."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agrofix"

    # Gemini AI
    GEMINI_API_KEY: str = ""

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # Weather API
    OPENWEATHER_API_KEY: str = ""

    # S3 Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_BUCKET: str = "agrofix-uploads"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Server
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
