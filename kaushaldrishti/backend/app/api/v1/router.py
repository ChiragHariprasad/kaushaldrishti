"""
API v1 router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    demand,
    export,
    forecast,
    gap,
    health,
    lineage,
    quality,
    review_queue,
    scenario,
    supply,
    webhooks,
)

api_router = APIRouter()

# Health and metadata
api_router.include_router(health.router, tags=["health"])

# Labour Demand Intelligence (LDI) and Attribution
api_router.include_router(demand.router, tags=["demand"])

# Demand Forecasts & Backtest Validation
api_router.include_router(forecast.router, tags=["forecast"])

# Supply Dynamics & Forecasts
api_router.include_router(supply.router, tags=["supply"])

# Gap Analysis, Alerts & Rankings
api_router.include_router(gap.router, tags=["gap"])

# Policy Scenario Simulator
api_router.include_router(scenario.router, tags=["scenario"])

# Data Export (CSV, XLSX, JSON, GeoJSON, Parquet)
api_router.include_router(export.router, tags=["export"])

# Lineage & Provenance
api_router.include_router(lineage.router, tags=["lineage"])

# Webhooks & Outbound Notifications
api_router.include_router(webhooks.router, tags=["webhooks"])

# Data Quality & Ingest Scorecards
api_router.include_router(quality.router, tags=["quality"])

# Taxonomy Mapping Review Queue
api_router.include_router(review_queue.router, tags=["taxonomy"])
