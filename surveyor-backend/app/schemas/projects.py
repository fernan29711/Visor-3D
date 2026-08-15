"""Project schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    """Create project schema."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    client_id: str = Field(...)
    description: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "PRJ-001",
                "name": "Levantamiento Parcela Moca",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "description": "Levantamiento topográfico de 2.5 hectáreas",
                "municipality": "Espaillat",
                "province": "Moca",
                "budget": 5000.00,
                "latitude": 19.2934,
                "longitude": -70.5271,
            }
        }

class ProjectUpdate(BaseModel):
    """Update project schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    spent: Optional[float] = Field(None, ge=0)

class ProjectResponse(BaseModel):
    """Project response schema."""
    id: str
    code: str
    name: str
    client_id: str
    status: str
    description: Optional[str]
    municipality: Optional[str]
    province: Optional[str]
    budget: Optional[float]
    spent: float
    responsible_user_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    """Project list response."""
    id: str
    code: str
    name: str
    status: str
    municipality: Optional[str]
    budget: Optional[float]
    spent: float
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectDetailResponse(BaseModel):
    """Detailed project response."""
    id: str
    code: str
    name: str
    client_id: str
    status: str
    description: Optional[str]
    municipality: Optional[str]
    province: Optional[str]
    budget: Optional[float]
    spent: float
    point_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
