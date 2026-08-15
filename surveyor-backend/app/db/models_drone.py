"""Drone flight and 3D model database models."""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Text, DECIMAL, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class DroneFlightStatus(str, enum.Enum):
    """Drone flight status enumeration."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DroneFlight(Base):
    """Drone flight record model."""
    __tablename__ = "drone_flights"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)

    flight_name = Column(String(255), nullable=False)
    drone_model = Column(String(100), nullable=True)  # e.g., "DJI Phantom 4 Pro"
    pilot_name = Column(String(255), nullable=True)

    flight_date = Column(DateTime, nullable=False, index=True)
    flight_duration_minutes = Column(Integer, nullable=True)
    status = Column(SQLEnum(DroneFlightStatus), default=DroneFlightStatus.COMPLETED, nullable=False)

    altitude_meters = Column(Float, nullable=True)
    area_coverage_hectares = Column(Float, nullable=True)
    ground_resolution_cm = Column(Float, nullable=True)  # GSD - Ground Sample Distance

    total_photos = Column(Integer, default=0, nullable=False)
    processed_photos = Column(Integer, default=0, nullable=False)

    model_3d_status = Column(String(50), nullable=True)  # "pending", "processing", "ready", "failed"
    model_3d_url = Column(String(500), nullable=True)
    model_3d_file_size_mb = Column(Float, nullable=True)

    weather_conditions = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="drone_flights")
    project = relationship("Project", back_populates="drone_flights")
    photos = relationship("DronePhoto", back_populates="flight", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DroneFlight {self.flight_name} ({self.flight_date.strftime('%Y-%m-%d')})>"


class DronePhoto(Base):
    """Drone photo record model."""
    __tablename__ = "drone_photos"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    flight_id = Column(String(36), ForeignKey("drone_flights.id"), nullable=False, index=True)

    photo_name = Column(String(255), nullable=False)
    photo_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)

    file_size_mb = Column(Float, nullable=True)
    resolution_width = Column(Integer, nullable=True)
    resolution_height = Column(Integer, nullable=True)

    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    gps_altitude_meters = Column(Float, nullable=True)

    capture_time = Column(DateTime, nullable=True)
    processing_status = Column(String(50), nullable=True)  # "original", "ortho", "3d_processed"

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    flight = relationship("DroneFlight", back_populates="photos")
    organization = relationship("Organization")

    def __repr__(self):
        return f"<DronePhoto {self.photo_name}>"


class Model3D(Base):
    """3D model generated from drone data."""
    __tablename__ = "models_3d"

    id = Column(String(36), primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    flight_id = Column(String(36), ForeignKey("drone_flights.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True, index=True)

    model_name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # "orthomosaic", "pointcloud", "mesh", "dem"
    file_format = Column(String(20), nullable=False)  # "las", "ply", "obj", "tiff", "geotiff"

    file_url = Column(String(500), nullable=False)
    file_size_mb = Column(Float, nullable=True)

    coverage_area_hectares = Column(Float, nullable=True)
    resolution_cm = Column(Float, nullable=True)  # GSD

    coordinate_system = Column(String(50), nullable=True)  # "WGS84", "UTM", etc.
    min_elevation = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)

    processing_time_minutes = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)  # 0-100

    status = Column(String(50), nullable=False)  # "ready", "processing", "archived"

    metadata = Column(Text, nullable=True)  # JSON string with additional metadata

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization")
    flight = relationship("DroneFlight")
    project = relationship("Project")

    def __repr__(self):
        return f"<Model3D {self.model_name} ({self.model_type})>"
