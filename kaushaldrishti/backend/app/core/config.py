"""
Application configuration via environment variables.
"""

import os
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB_FILE = (_BACKEND_DIR / "kaushaldrishti_dev.db").as_posix()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "KaushalDrishti"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    DEBUG: bool = True

    # Database URLs
    DATABASE_URL: str = f"sqlite+aiosqlite:///{_DEFAULT_DB_FILE}"
    DATABASE_URL_SYNC: str = f"sqlite:///{_DEFAULT_DB_FILE}"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def sanitize_db_url(cls, v: str) -> str:
        # Override with KD_DATABASE_URL if explicitly given
        kd_url = os.getenv("KD_DATABASE_URL")
        if kd_url:
            v = kd_url
        if not v or "ihorms" in v:
            return f"sqlite+aiosqlite:///{_DEFAULT_DB_FILE}"
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("DATABASE_URL_SYNC", mode="after")
    @classmethod
    def sanitize_sync_db_url(cls, v: str) -> str:
        kd_sync = os.getenv("KD_DATABASE_URL_SYNC")
        if kd_sync:
            v = kd_sync
        if not v or "ihorms" in v:
            return f"sqlite:///{_DEFAULT_DB_FILE}"
        if "+asyncpg" in v:
            return v.replace("+asyncpg", "")
        return v

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
