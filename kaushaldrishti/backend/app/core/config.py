"""
Application configuration via environment variables.
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "KaushalDrishti"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./kaushaldrishti_dev.db"
    )
    DATABASE_URL_SYNC: str = os.getenv(
        "DATABASE_URL_SYNC",
        "sqlite:///./kaushaldrishti_dev.db"
    )

    # API Security
    API_KEY: str = "dev-key-2026"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80", "http://localhost"]

    # Data paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    INCOMING_DIR: str = os.getenv("INCOMING_DIR", "data/incoming")
    REFERENCE_DIR: str = os.getenv("REFERENCE_DIR", "data/reference")
    GEO_DIR: str = os.getenv("GEO_DIR", "data/geo")
    SYNTHETIC_DIR: str = os.getenv("SYNTHETIC_DIR", "data/synthetic")
    LAKE_DIR: str = os.getenv("LAKE_DIR", "data/lake")

    # Pipeline
    MINIMUM_CELL_SIZE: int = 10  # For privacy (e-Shram derived figures)
    RANDOM_SEED: int = 42

    model_config = {"env_prefix": "", "case_sensitive": True}


settings = Settings()
