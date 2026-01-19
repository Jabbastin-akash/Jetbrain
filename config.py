"""
Configuration settings for the VALORANT Scouting Assistant.
Loads environment variables and provides application-wide settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # GRID API Settings
    grid_api_key: str = ""
    grid_api_base_url: str = "https://api.grid.gg"

    # Google Gemini Settings
    gemini_api_key: str = ""

    # Application Settings
    debug: bool = True
    cache_ttl_seconds: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
