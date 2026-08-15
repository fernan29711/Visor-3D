"""Geospatial API routes for map data."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.db.models import User, Project
from app.services.geospatial_service import GeospatialService
from app.schemas.geospatial import (
    ProjectMapDataResponse, MapBoundsResponse, GeoJSONFeatureCollection
)

router = APIRouter(prefix="/api/v1/geospatial", tags=["geospatial"])


@router.get("/projects/{project_id}/map-data", response_model=ProjectMapDataResponse)
def get_project_map_data(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get complete map data for a project (survey points, parcels, drone coverage)."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    map_data = GeospatialService.get_project_map_data(db, project_id, current_user.organization_id)
    if not map_data:
        raise HTTPException(status_code=404, detail="Map data not found")

    return map_data


@router.get("/projects/{project_id}/bounds", response_model=MapBoundsResponse)
def get_project_bounds(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get map bounds for a project."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    bounds = GeospatialService.get_map_bounds(db, project_id, current_user.organization_id)
    if not bounds:
        raise HTTPException(status_code=404, detail="No geographic data available for project")

    return bounds


@router.get("/projects/{project_id}/survey-points-geojson")
def get_survey_points_geojson(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get survey points as GeoJSON FeatureCollection."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    survey_points = GeospatialService.get_survey_points_for_project(db, project_id, current_user.organization_id)
    geojson = GeospatialService.create_geojson_survey_points(survey_points)
    return geojson


@router.get("/projects/{project_id}/parcels-geojson")
def get_parcels_geojson(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get parcels as GeoJSON FeatureCollection."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    parcels = GeospatialService.get_parcels_for_project(db, project_id, current_user.organization_id)
    geojson = GeospatialService.create_geojson_parcels(parcels)
    return geojson


@router.get("/projects/{project_id}/drone-coverage-geojson")
def get_drone_coverage_geojson(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get drone coverage areas as GeoJSON FeatureCollection."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    coverage = GeospatialService.get_drone_coverage_for_project(db, project_id, current_user.organization_id)
    geojson = GeospatialService.create_geojson_drone_coverage(coverage)
    return geojson


@router.get("/projects/{project_id}/map-features")
def get_all_map_features(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all map features (survey points, parcels, drone coverage) as combined GeoJSON."""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == current_user.organization_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    survey_points = GeospatialService.get_survey_points_for_project(db, project_id, current_user.organization_id)
    parcels = GeospatialService.get_parcels_for_project(db, project_id, current_user.organization_id)
    drone_coverage = GeospatialService.get_drone_coverage_for_project(db, project_id, current_user.organization_id)

    points_geojson = GeospatialService.create_geojson_survey_points(survey_points)
    parcels_geojson = GeospatialService.create_geojson_parcels(parcels)
    coverage_geojson = GeospatialService.create_geojson_drone_coverage(drone_coverage)

    all_features = {
        "survey_points": points_geojson,
        "parcels": parcels_geojson,
        "drone_coverage": coverage_geojson
    }
    return all_features
