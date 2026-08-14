"""API v1 Main Router"""

from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/status", tags=["Status"])
async def api_status():
    """API status check."""
    return {"status": "API v1 operational"}
