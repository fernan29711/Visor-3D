"""API v1 Main Router"""

from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.organizations.routes import router as org_router
from app.api.v1.users.routes import router as user_router
from app.api.v1.clients.routes import router as clients_router
from app.api.v1.projects.routes import router as projects_router
from app.api.v1.survey_points.routes import router as survey_points_router
from app.api.v1.calculations.routes import router as calculations_router
from app.api.v1.quotes.routes import router as quotes_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router)
api_router.include_router(org_router)
api_router.include_router(user_router)
api_router.include_router(clients_router)
api_router.include_router(projects_router)
api_router.include_router(survey_points_router)
api_router.include_router(calculations_router)
api_router.include_router(quotes_router)

@api_router.get("/status", tags=["Status"])
async def api_status():
    """API status check."""
    return {"status": "API v1 operational"}
