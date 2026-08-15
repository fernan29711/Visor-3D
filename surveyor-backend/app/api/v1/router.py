"""API v1 Main Router"""

from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.organizations.routes import router as org_router
from app.api.v1.users.routes import router as user_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router)
api_router.include_router(org_router)
api_router.include_router(user_router)

@api_router.get("/status", tags=["Status"])
async def api_status():
    """API status check."""
    return {"status": "API v1 operational"}
