"""Topographic calculations endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Tuple

from app.db.models import User
from app.dependencies import get_current_user
from app.utils.calculations import SurveyCalculations

router = APIRouter(prefix="/calculations", tags=["Calculations"])

# Request/Response models
class Point(BaseModel):
    """Point coordinates."""
    east: float
    north: float
    elevation: float = 0

class DistanceRequest(BaseModel):
    """Distance calculation request."""
    point1: Point
    point2: Point

class DistanceResponse(BaseModel):
    """Distance calculation response."""
    horizontal_distance: float
    inclined_distance: float
    elevation_difference: float

class AzimuthRequest(BaseModel):
    """Azimuth calculation request."""
    point1: Point
    point2: Point

class AzimuthResponse(BaseModel):
    """Azimuth calculation response."""
    azimuth_degrees: float
    bearing: str
    quadrant: str

class AreaRequest(BaseModel):
    """Area calculation request."""
    points: List[Tuple[float, float]] = Field(..., min_items=3)

class AreaResponse(BaseModel):
    """Area calculation response."""
    area: float
    perimeter: float
    unit: str = "square_units"

class SlopeRequest(BaseModel):
    """Slope calculation request."""
    horizontal_distance: float
    vertical_distance: float

class SlopeResponse(BaseModel):
    """Slope calculation response."""
    angle_degrees: float
    grade_percentage: float

@router.post("/distance", response_model=DistanceResponse)
async def calculate_distance(
    request: DistanceRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate distance between two points."""
    calc = SurveyCalculations

    horizontal = calc.distance_horizontal(
        request.point1.east,
        request.point1.north,
        request.point2.east,
        request.point2.north
    )

    inclined = calc.distance_inclined(
        request.point1.east,
        request.point1.north,
        request.point1.elevation,
        request.point2.east,
        request.point2.north,
        request.point2.elevation
    )

    elevation_diff = request.point2.elevation - request.point1.elevation

    return DistanceResponse(
        horizontal_distance=round(horizontal, 4),
        inclined_distance=round(inclined, 4),
        elevation_difference=round(elevation_diff, 4)
    )

@router.post("/azimuth", response_model=AzimuthResponse)
async def calculate_azimuth(
    request: AzimuthRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate azimuth (bearing) between two points."""
    calc = SurveyCalculations

    azimuth = calc.azimuth(
        request.point1.east,
        request.point1.north,
        request.point2.east,
        request.point2.north
    )

    bearing = calc.bearing_to_quadrant(azimuth)

    return AzimuthResponse(
        azimuth_degrees=round(azimuth, 4),
        bearing=bearing,
        quadrant=bearing
    )

@router.post("/area", response_model=AreaResponse)
async def calculate_area(
    request: AreaRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate area and perimeter of polygon."""
    calc = SurveyCalculations

    area = calc.polygon_area(request.points)
    perimeter = calc.polygon_perimeter(request.points)

    return AreaResponse(
        area=round(area, 2),
        perimeter=round(perimeter, 4),
        unit="square_units"
    )

@router.post("/slope", response_model=SlopeResponse)
async def calculate_slope(
    request: SlopeRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate slope angle and grade."""
    calc = SurveyCalculations

    angle = calc.slope_angle(
        request.horizontal_distance,
        request.vertical_distance
    )

    grade = calc.grade_percentage(
        request.horizontal_distance,
        request.vertical_distance
    )

    return SlopeResponse(
        angle_degrees=round(angle, 2),
        grade_percentage=round(grade, 2)
    )
