"""
Environment-based application settings using Pydantic.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # App
    APP_NAME: str = "FaceStream API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://facestream:facestream@db:5432/facestream"

    # Detection
    DETECTION_CONFIDENCE: float = 0.5
    DETECTION_INTERVAL: int = 3  # Run detection every N frames
    FRAME_QUEUE_SIZE: int = 30   # Max frames in processing queue

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
