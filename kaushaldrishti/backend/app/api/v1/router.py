"""
API v1 router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()

# Health and metadata
api_router.include_router(health.router, tags=["health"])
