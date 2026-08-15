"""Geospatial schemas for map visualization."""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from uuid import UUID
from decimal import Decimal
from datetime import datetime


class Point(BaseModel):
    """GeoJSON Point geometry."""
    type: str = Field("Point", const=True)
    coordinates: List[float]


class Polygon(BaseModel):
    """GeoJSON Polygon geometry."""
    type: str = Field("Polygon", const=True)
    coordinates: List[List[List[float]]]


class LineString(BaseModel):
    """GeoJSON LineString geometry."""
    type: str = Field("LineString", const=True)
    coordinates: List[List[float]]


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature."""
    type: str = Field("Feature", const=True)
    geometry: Optional[Any] = None
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection."""
    type: str = Field("FeatureCollection", const=True)
    features: List[GeoJSONFeature]


class SurveyPointMapResponse(BaseModel):
    """Survey point for map display."""
    id: UUID
    project_id: UUID
    point_number: str
    coordinates: List[float]
    elevation: Optional[Decimal]
    code: Optional[str]
    description: Optional[str]
    precision_horizontal: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class ParcelMapResponse(BaseModel):
    """Parcel for map display."""
    id: UUID
    project_id: UUID
    parcel_number: str
    owner_name: Optional[str]
    area: Optional[Decimal]
    municipality: Optional[str]
    province: Optional[str]

    class Config:
        from_attributes = True


class DronePhotoLocationResponse(BaseModel):
    """Drone photo location for coverage visualization."""
    photo_id: str
    flight_id: str
    latitude: float
    longitude: float
    altitude: float
    capture_time: Optional[datetime]

    class Config:
        from_attributes = True


class DroneCoverageResponse(BaseModel):
    """Drone flight coverage area."""
    flight_id: str
    flight_name: str
    flight_date: datetime
    altitude_meters: float
    area_coverage_hectares: float
    ground_resolution_cm: float
    photo_count: int
    convex_hull_coordinates: Optional[List[List[float]]]

    class Config:
        from_attributes = True


class ProjectMapDataResponse(BaseModel):
    """Complete map data for a project."""
    project_id: UUID
    project_name: str
    project_location: Optional[List[float]]
    survey_points: List[SurveyPointMapResponse]
    parcels: List[ParcelMapResponse]
    drone_coverage: List[DroneCoverageResponse]
    boundary_coordinates: Optional[List[List[float]]]

    class Config:
        from_attributes = True


class HeatmapDataResponse(BaseModel):
    """Heatmap data for drone coverage density."""
    type: str = Field("FeatureCollection", const=True)
    features: List[GeoJSONFeature]

    class Config:
        from_attributes = True


class MapBoundsResponse(BaseModel):
    """Geographic bounds for map viewport."""
    north: float
    south: float
    east: float
    west: float

    class Config:
        from_attributes = True


class ProjectLocationUpdateRequest(BaseModel):
    """Request to update project location."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_name: Optional[str] = None
