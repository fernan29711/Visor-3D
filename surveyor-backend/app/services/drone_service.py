"""Drone flight and 3D model service."""

from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models_drone import DroneFlight, DronePhoto, Model3D, DroneFlightStatus
from app.schemas.drones import (
    DroneFlightCreate,
    DroneFlightUpdate,
    DronePhotoCreate,
    Model3DCreate,
)
from app.core.exceptions import NotFoundError, ValidationError


class DroneService:
    """Service for managing drone flights and 3D models."""

    def __init__(self, db: Session):
        self.db = db

    def create_flight(self, org_id: str, request: DroneFlightCreate) -> dict:
        """Create new drone flight."""
        flight = DroneFlight(
            id=str(uuid4()),
            organization_id=org_id,
            flight_name=request.flight_name,
            project_id=request.project_id,
            drone_model=request.drone_model,
            pilot_name=request.pilot_name,
            flight_date=request.flight_date,
            flight_duration_minutes=request.flight_duration_minutes,
            altitude_meters=request.altitude_meters,
            area_coverage_hectares=request.area_coverage_hectares,
            ground_resolution_cm=request.ground_resolution_cm,
            weather_conditions=request.weather_conditions,
            notes=request.notes,
            status=DroneFlightStatus.COMPLETED,
        )
        self.db.add(flight)
        self.db.commit()
        self.db.refresh(flight)
        return self._flight_to_dict(flight)

    def get_flight(self, flight_id: str, org_id: str) -> dict:
        """Get flight by ID."""
        flight = self.db.query(DroneFlight).filter(
            DroneFlight.id == flight_id,
            DroneFlight.organization_id == org_id
        ).first()

        if not flight:
            raise NotFoundError("Flight not found")

        return self._flight_to_dict_with_photos(flight)

    def list_flights(self, org_id: str, skip: int = 0, limit: int = 20, project_id: str = None) -> list[dict]:
        """List flights for organization."""
        query = self.db.query(DroneFlight).filter(
            DroneFlight.organization_id == org_id
        )

        if project_id:
            query = query.filter(DroneFlight.project_id == project_id)

        flights = query.offset(skip).limit(limit).all()
        return [self._flight_to_dict(f) for f in flights]

    def update_flight(self, flight_id: str, org_id: str, request: DroneFlightUpdate) -> dict:
        """Update flight."""
        flight = self.db.query(DroneFlight).filter(
            DroneFlight.id == flight_id,
            DroneFlight.organization_id == org_id
        ).first()

        if not flight:
            raise NotFoundError("Flight not found")

        if request.flight_name:
            flight.flight_name = request.flight_name
        if request.status:
            flight.status = request.status
        if request.total_photos is not None:
            flight.total_photos = request.total_photos
        if request.processed_photos is not None:
            flight.processed_photos = request.processed_photos
        if request.model_3d_status:
            flight.model_3d_status = request.model_3d_status
        if request.model_3d_url:
            flight.model_3d_url = request.model_3d_url
        if request.model_3d_file_size_mb:
            flight.model_3d_file_size_mb = request.model_3d_file_size_mb

        flight.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(flight)
        return self._flight_to_dict(flight)

    def delete_flight(self, flight_id: str, org_id: str) -> None:
        """Delete flight."""
        flight = self.db.query(DroneFlight).filter(
            DroneFlight.id == flight_id,
            DroneFlight.organization_id == org_id
        ).first()

        if not flight:
            raise NotFoundError("Flight not found")

        self.db.delete(flight)
        self.db.commit()

    def add_photo(self, flight_id: str, org_id: str, request: DronePhotoCreate) -> dict:
        """Add photo to flight."""
        flight = self.db.query(DroneFlight).filter(
            DroneFlight.id == flight_id,
            DroneFlight.organization_id == org_id
        ).first()

        if not flight:
            raise NotFoundError("Flight not found")

        photo = DronePhoto(
            id=str(uuid4()),
            organization_id=org_id,
            flight_id=flight_id,
            photo_name=request.photo_name,
            photo_url=request.photo_url,
            thumbnail_url=request.thumbnail_url,
            file_size_mb=request.file_size_mb,
            resolution_width=request.resolution_width,
            resolution_height=request.resolution_height,
            gps_latitude=request.gps_latitude,
            gps_longitude=request.gps_longitude,
            gps_altitude_meters=request.gps_altitude_meters,
            capture_time=request.capture_time,
            notes=request.notes,
        )
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return self._photo_to_dict(photo)

    def get_flight_photos(self, flight_id: str, org_id: str) -> list[dict]:
        """Get all photos for a flight."""
        flight = self.db.query(DroneFlight).filter(
            DroneFlight.id == flight_id,
            DroneFlight.organization_id == org_id
        ).first()

        if not flight:
            raise NotFoundError("Flight not found")

        photos = self.db.query(DronePhoto).filter(
            DronePhoto.flight_id == flight_id,
            DronePhoto.organization_id == org_id
        ).all()

        return [self._photo_to_dict(p) for p in photos]

    def create_3d_model(self, org_id: str, request: Model3DCreate) -> dict:
        """Create 3D model."""
        # Verify flight exists
        flight = self.db.query(DroneFlight).filter(
            DroneFlight.id == request.flight_id,
            DroneFlight.organization_id == org_id
        ).first()

        if not flight:
            raise NotFoundError("Flight not found")

        model = Model3D(
            id=str(uuid4()),
            organization_id=org_id,
            flight_id=request.flight_id,
            project_id=request.project_id,
            model_name=request.model_name,
            model_type=request.model_type,
            file_format=request.file_format,
            file_url=request.file_url,
            coverage_area_hectares=request.coverage_area_hectares,
            resolution_cm=request.resolution_cm,
            coordinate_system=request.coordinate_system,
            min_elevation=request.min_elevation,
            max_elevation=request.max_elevation,
            status="ready",
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_dict(model)

    def get_3d_models_for_flight(self, flight_id: str, org_id: str) -> list[dict]:
        """Get all 3D models for a flight."""
        models = self.db.query(Model3D).filter(
            Model3D.flight_id == flight_id,
            Model3D.organization_id == org_id
        ).all()

        return [self._model_to_dict(m) for m in models]

    def get_3d_models_for_project(self, project_id: str, org_id: str) -> list[dict]:
        """Get all 3D models for a project."""
        models = self.db.query(Model3D).filter(
            Model3D.project_id == project_id,
            Model3D.organization_id == org_id
        ).all()

        return [self._model_to_dict(m) for m in models]

    def get_drone_summary(self, org_id: str) -> dict:
        """Get drone activity summary."""
        flights = self.db.query(DroneFlight).filter(
            DroneFlight.organization_id == org_id
        ).all()

        total_flights = len(flights)
        total_photos = sum(f.total_photos for f in flights)
        total_area = sum(f.area_coverage_hectares for f in flights if f.area_coverage_hectares)

        models = self.db.query(Model3D).filter(
            Model3D.organization_id == org_id
        ).all()

        return {
            "total_flights": total_flights,
            "completed_flights": sum(1 for f in flights if f.status == DroneFlightStatus.COMPLETED),
            "total_photos_captured": total_photos,
            "total_area_covered_hectares": total_area,
            "total_3d_models": len(models),
            "models_by_type": self._count_models_by_type(models),
        }

    def _count_models_by_type(self, models: list) -> dict:
        """Count models by type."""
        counts = {}
        for model in models:
            counts[model.model_type] = counts.get(model.model_type, 0) + 1
        return counts

    def _flight_to_dict(self, flight: DroneFlight) -> dict:
        """Convert flight to dictionary."""
        return {
            "id": flight.id,
            "flight_name": flight.flight_name,
            "drone_model": flight.drone_model,
            "pilot_name": flight.pilot_name,
            "flight_date": flight.flight_date,
            "flight_duration_minutes": flight.flight_duration_minutes,
            "status": flight.status.value if isinstance(flight.status, DroneFlightStatus) else flight.status,
            "altitude_meters": flight.altitude_meters,
            "area_coverage_hectares": flight.area_coverage_hectares,
            "ground_resolution_cm": flight.ground_resolution_cm,
            "total_photos": flight.total_photos,
            "processed_photos": flight.processed_photos,
            "model_3d_status": flight.model_3d_status,
            "model_3d_url": flight.model_3d_url,
            "created_at": flight.created_at,
        }

    def _flight_to_dict_with_photos(self, flight: DroneFlight) -> dict:
        """Convert flight to dictionary with photos."""
        data = self._flight_to_dict(flight)
        data["project_id"] = flight.project_id
        data["weather_conditions"] = flight.weather_conditions
        data["notes"] = flight.notes
        data["photos"] = [self._photo_to_dict(p) for p in flight.photos]
        return data

    def _photo_to_dict(self, photo: DronePhoto) -> dict:
        """Convert photo to dictionary."""
        return {
            "id": photo.id,
            "flight_id": photo.flight_id,
            "photo_name": photo.photo_name,
            "photo_url": photo.photo_url,
            "thumbnail_url": photo.thumbnail_url,
            "resolution_width": photo.resolution_width,
            "resolution_height": photo.resolution_height,
            "gps_latitude": photo.gps_latitude,
            "gps_longitude": photo.gps_longitude,
            "gps_altitude_meters": photo.gps_altitude_meters,
            "capture_time": photo.capture_time,
            "created_at": photo.created_at,
        }

    def _model_to_dict(self, model: Model3D) -> dict:
        """Convert model to dictionary."""
        return {
            "id": model.id,
            "flight_id": model.flight_id,
            "project_id": model.project_id,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "file_format": model.file_format,
            "file_url": model.file_url,
            "file_size_mb": model.file_size_mb,
            "coverage_area_hectares": model.coverage_area_hectares,
            "resolution_cm": model.resolution_cm,
            "coordinate_system": model.coordinate_system,
            "min_elevation": model.min_elevation,
            "max_elevation": model.max_elevation,
            "status": model.status,
            "quality_score": model.quality_score,
            "created_at": model.created_at,
        }
