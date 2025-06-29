from fastapi import APIRouter
from ...api.endpoints import auth, visualizations, datasets, health

api_router = APIRouter()

# Include API routes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(visualizations.router, prefix="/visualizations", tags=["visualizations"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(health.router, tags=["health"])
