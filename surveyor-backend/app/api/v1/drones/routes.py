"""Drone flight and 3D model endpoints."""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.drones import (
    DroneFlightCreate,
    DroneFlightUpdate,
    DroneFlightResponse,
    DroneFlightDetailResponse,
    DronePhotoCreate,
    DronePhotoResponse,
    Model3DCreate,
    Model3DResponse,
)
from app.services.drone_service import DroneService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/drones", tags=["Drones"])

@router.post("/flights", response_model=DroneFlightResponse, status_code=status.HTTP_201_CREATED)
async def create_flight(
    request: DroneFlightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new drone flight."""
    try:
        service = DroneService(db)
        flight = service.create_flight(str(current_user.organization_id), request)
        return flight
    except AppException as e:
        raise http_exception(e)

@router.get("/flights", response_model=list[DroneFlightResponse])
async def list_flights(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    project_id: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List drone flights."""
    try:
        service = DroneService(db)
        flights = service.list_flights(
            str(current_user.organization_id),
            skip=skip,
            limit=limit,
            project_id=project_id
        )
        return flights
    except AppException as e:
        raise http_exception(e)

@router.get("/flights/{flight_id}", response_model=DroneFlightDetailResponse)
async def get_flight(
    flight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get flight details."""
    try:
        service = DroneService(db)
        flight = service.get_flight(flight_id, str(current_user.organization_id))
        return flight
    except AppException as e:
        raise http_exception(e)

@router.patch("/flights/{flight_id}", response_model=DroneFlightResponse)
async def update_flight(
    flight_id: str,
    request: DroneFlightUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update flight."""
    try:
        service = DroneService(db)
        flight = service.update_flight(flight_id, str(current_user.organization_id), request)
        return flight
    except AppException as e:
        raise http_exception(e)

@router.delete("/flights/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(
    flight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete flight."""
    try:
        service = DroneService(db)
        service.delete_flight(flight_id, str(current_user.organization_id))
        return None
    except AppException as e:
        raise http_exception(e)

@router.post("/flights/{flight_id}/photos", response_model=DronePhotoResponse, status_code=status.HTTP_201_CREATED)
async def add_photo(
    flight_id: str,
    request: DronePhotoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add photo to flight."""
    try:
        service = DroneService(db)
        photo = service.add_photo(flight_id, str(current_user.organization_id), request)
        return photo
    except AppException as e:
        raise http_exception(e)

@router.get("/flights/{flight_id}/photos", response_model=list[DronePhotoResponse])
async def get_flight_photos(
    flight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get flight photos."""
    try:
        service = DroneService(db)
        photos = service.get_flight_photos(flight_id, str(current_user.organization_id))
        return photos
    except AppException as e:
        raise http_exception(e)

@router.post("/models-3d", response_model=Model3DResponse, status_code=status.HTTP_201_CREATED)
async def create_3d_model(
    request: Model3DCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create 3D model."""
    try:
        service = DroneService(db)
        model = service.create_3d_model(str(current_user.organization_id), request)
        return model
    except AppException as e:
        raise http_exception(e)

@router.get("/flights/{flight_id}/models-3d", response_model=list[Model3DResponse])
async def get_flight_3d_models(
    flight_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get 3D models for flight."""
    try:
        service = DroneService(db)
        models = service.get_3d_models_for_flight(flight_id, str(current_user.organization_id))
        return models
    except AppException as e:
        raise http_exception(e)

@router.get("/projects/{project_id}/models-3d", response_model=list[Model3DResponse])
async def get_project_3d_models(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get 3D models for project."""
    try:
        service = DroneService(db)
        models = service.get_3d_models_for_project(project_id, str(current_user.organization_id))
        return models
    except AppException as e:
        raise http_exception(e)

@router.get("/summary")
async def get_drone_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get drone activity summary."""
    try:
        service = DroneService(db)
        summary = service.get_drone_summary(str(current_user.organization_id))
        return summary
    except AppException as e:
        raise http_exception(e)
