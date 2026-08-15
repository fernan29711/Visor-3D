"""Survey point schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SurveyPointCreate(BaseModel):
    """Create survey point schema."""
    point_number: str = Field(..., min_length=1, max_length=50)
    east: float = Field(...)
    north: float = Field(...)
    elevation: Optional[float] = None
    code: Optional[str] = None
    description: Optional[str] = None
    precision_horizontal: Optional[float] = Field(None, gt=0)
    precision_vertical: Optional[float] = Field(None, gt=0)
    gnss_status: Optional[str] = None
    pdop: Optional[float] = None
    satellites: Optional[int] = None
    observations: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "point_number": "P-001",
                "east": 327845.236,
                "north": 2165487.421,
                "elevation": 82.436,
                "code": "CORNER",
                "description": "Esquina noreste",
                "precision_horizontal": 0.05,
                "precision_vertical": 0.08,
                "gnss_status": "RTK",
                "pdop": 2.1,
                "satellites": 12,
                "observations": "Punto bien definido",
            }
        }

class SurveyPointUpdate(BaseModel):
    """Update survey point schema."""
    point_number: Optional[str] = Field(None, min_length=1, max_length=50)
    east: Optional[float] = None
    north: Optional[float] = None
    elevation: Optional[float] = None
    code: Optional[str] = None
    description: Optional[str] = None
    precision_horizontal: Optional[float] = Field(None, gt=0)
    precision_vertical: Optional[float] = Field(None, gt=0)
    gnss_status: Optional[str] = None
    observations: Optional[str] = None

class SurveyPointResponse(BaseModel):
    """Survey point response schema."""
    id: str
    project_id: str
    point_number: str
    east: float
    north: float
    elevation: Optional[float]
    code: Optional[str]
    description: Optional[str]
    precision_horizontal: Optional[float]
    precision_vertical: Optional[float]
    gnss_status: Optional[str]
    pdop: Optional[float]
    satellites: Optional[int]
    observations: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SurveyPointListResponse(BaseModel):
    """Survey point list response."""
    id: str
    point_number: str
    east: float
    north: float
    elevation: Optional[float]
    code: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SurveyPointBulkImport(BaseModel):
    """Bulk import survey points."""
    points: list[SurveyPointCreate]
    crs: str = "EPSG:4326"
    unit_elevation: str = "meters"

class ImportResponse(BaseModel):
    """Import response."""
    imported_count: int
    failed_count: int
    errors: list[dict]
    message: str
