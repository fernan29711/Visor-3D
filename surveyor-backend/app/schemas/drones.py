"""Drone flight and 3D model schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional


class DronePhotoCreate(BaseModel):
    """Create drone photo."""
    photo_name: str
    photo_url: str
    thumbnail_url: Optional[str] = None
    file_size_mb: Optional[float] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude_meters: Optional[float] = None
    capture_time: Optional[datetime] = None
    notes: Optional[str] = None


class DronePhotoResponse(BaseModel):
    """Drone photo response."""
    id: str
    flight_id: str
    photo_name: str
    photo_url: str
    thumbnail_url: Optional[str] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude_meters: Optional[float] = None
    capture_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DroneFlightCreate(BaseModel):
    """Create drone flight."""
    flight_name: str
    project_id: Optional[str] = None
    drone_model: Optional[str] = None
    pilot_name: Optional[str] = None
    flight_date: datetime
    flight_duration_minutes: Optional[int] = None
    altitude_meters: Optional[float] = None
    area_coverage_hectares: Optional[float] = None
    ground_resolution_cm: Optional[float] = None
    weather_conditions: Optional[str] = None
    notes: Optional[str] = None


class DroneFlightUpdate(BaseModel):
    """Update drone flight."""
    flight_name: Optional[str] = None
    status: Optional[str] = None
    total_photos: Optional[int] = None
    processed_photos: Optional[int] = None
    model_3d_status: Optional[str] = None
    model_3d_url: Optional[str] = None
    model_3d_file_size_mb: Optional[float] = None


class DroneFlightResponse(BaseModel):
    """Drone flight response."""
    id: str
    flight_name: str
    drone_model: Optional[str] = None
    pilot_name: Optional[str] = None
    flight_date: datetime
    status: str
    altitude_meters: Optional[float] = None
    area_coverage_hectares: Optional[float] = None
    ground_resolution_cm: Optional[float] = None
    total_photos: int
    processed_photos: int
    model_3d_status: Optional[str] = None
    model_3d_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DroneFlightDetailResponse(DroneFlightResponse):
    """Drone flight detail with photos."""
    project_id: Optional[str] = None
    flight_duration_minutes: Optional[int] = None
    weather_conditions: Optional[str] = None
    notes: Optional[str] = None
    photos: list[DronePhotoResponse] = []


class Model3DCreate(BaseModel):
    """Create 3D model."""
    flight_id: str
    project_id: Optional[str] = None
    model_name: str
    model_type: str  # "orthomosaic", "pointcloud", "mesh", "dem"
    file_format: str  # "las", "ply", "obj", "tiff", "geotiff"
    file_url: str
    coverage_area_hectares: Optional[float] = None
    resolution_cm: Optional[float] = None
    coordinate_system: Optional[str] = None
    min_elevation: Optional[float] = None
    max_elevation: Optional[float] = None


class Model3DResponse(BaseModel):
    """3D model response."""
    id: str
    flight_id: str
    model_name: str
    model_type: str
    file_format: str
    file_url: str
    file_size_mb: Optional[float] = None
    coverage_area_hectares: Optional[float] = None
    resolution_cm: Optional[float] = None
    status: str
    quality_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class Model3DDetailResponse(Model3DResponse):
    """3D model detail response."""
    project_id: Optional[str] = None
    coordinate_system: Optional[str] = None
    min_elevation: Optional[float] = None
    max_elevation: Optional[float] = None
    processing_time_minutes: Optional[int] = None
