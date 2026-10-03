"""
Health and metadata endpoints.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings


router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
    uptime_seconds: float
    timestamp: str


class MetadataResponse(BaseModel):
    """System metadata response."""
    app_name: str
    version: str
    environment: str
    pilot_states: list[str]
    pilot_sectors: list[str]
    languages: list[str]
    data_mode_counts: Dict[str, int]
    sources: list[Dict[str, Any]]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    Returns service status, version, and uptime.
    """
    from app.main import app

    uptime = time.time() - getattr(app.state, "start_time", time.time())

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        uptime_seconds=round(uptime, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/metadata", response_model=MetadataResponse)
async def get_metadata() -> MetadataResponse:
    """
    System metadata: sources, freshness, pilot scope, data_mode counts.
    Populated as data layers come online.
    """
    return MetadataResponse(
        app_name=settings.APP_NAME,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        pilot_states=["Karnataka", "Tamil Nadu", "Uttar Pradesh"],
        pilot_sectors=[
            "Construction",
            "Electronics and Hardware",
            "Healthcare",
            "Automotive",
            "Logistics and Supply Chain",
        ],
        languages=["en", "hi", "kn", "ta"],
        data_mode_counts={
            "live": 0,
            "public_aggregate": 0,
            "partner": 0,
            "synthetic": 0,
        },
        sources=[],
    )
