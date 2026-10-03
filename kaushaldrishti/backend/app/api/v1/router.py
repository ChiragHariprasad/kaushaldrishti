"""
API v1 router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, quality, review_queue

api_router = APIRouter()

# Health and metadata
api_router.include_router(health.router, tags=["health"])

# Data Quality & Ingest Scorecards
api_router.include_router(quality.router, tags=["quality"])

# Taxonomy Mapping Review Queue
api_router.include_router(review_queue.router, tags=["taxonomy"])
