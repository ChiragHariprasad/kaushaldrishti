"""
KaushalDrishti — FastAPI Application Entry Point
"""

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    app.state.start_time = time.time()
    yield


app = FastAPI(
    title="KaushalDrishti API",
    description=(
        "AI-enabled Labour Market Intelligence System (LMIS) for MSDE. "
        "Provides district-level labour demand indices, supply forecasts, "
        "gap analysis, early warnings, and policy scenario simulation."
    ),
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS — allow all in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router, prefix="/api/v1")
