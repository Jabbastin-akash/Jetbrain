"""
Configuration settings for the VALORANT Scouting Assistant.
Loads environment variables and provides application-wide settings.

SECURITY: Loads from .env.local (private, not committed) first,
then falls back to .env (template with placeholders)
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path


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
        # Try .env.local first (private keys), then .env (template)
        env_file = ".env.local" if Path(".env.local").exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
