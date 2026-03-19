"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the AgroFix platform."""

    # Database (SQLite local)
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrofix.db"

    # Gemini AI
    GEMINI_API_KEY: str = ""

    # JWT Auth
    JWT_SECRET_KEY: str = "agrofix-super-secret-key-change-in-production"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # Weather API
    OPENWEATHER_API_KEY: str = ""

    # Local Storage (replaces S3)
    LOCAL_STORAGE_DIR: str = "./uploads"

    # Server
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
