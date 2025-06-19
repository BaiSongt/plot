from fastapi import APIRouter

from app.api.endpoints import auth, visualizations

api_router = APIRouter()

# Include API routes
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(visualizations.router, prefix="/visualizations", tags=["可视化"])
