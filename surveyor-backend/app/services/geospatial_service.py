"""Geospatial service for map operations using PostGIS."""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_AsGeoJSON, ST_Envelope, ST_ConvexHull, ST_Buffer, ST_Bounds, ST_Transform, ST_Point, ST_SetSRID, ST_AsText
from geoalchemy2 import Geometry
from decimal import Decimal
from datetime import datetime

from app.db.models import Project, SurveyPoint, Parcel, Geometry as GeometryModel
from app.db.models_drone import DroneFlight, DronePhoto
from app.schemas.geospatial import (
    SurveyPointMapResponse, ParcelMapResponse, DroneCoverageResponse,
    ProjectMapDataResponse, MapBoundsResponse, GeoJSONFeature, Point, Polygon, LineString
)


class GeospatialService:
    """Service for geospatial queries and map data generation."""

    @staticmethod
    def get_survey_points_for_project(
        db: Session, project_id: UUID, organization_id: UUID
    ) -> List[SurveyPointMapResponse]:
        """Get all survey points for a project with coordinates."""
        points = db.query(SurveyPoint).filter(
            SurveyPoint.project_id == project_id
        ).all()

        result = []
        for point in points:
            if point.geometry:
                coords = GeospatialService.extract_point_coords(point.geometry)
                result.append(SurveyPointMapResponse(
                    id=point.id,
                    project_id=point.project_id,
                    point_number=point.point_number,
                    coordinates=coords,
                    elevation=point.elevation,
                    code=point.code,
                    description=point.description,
                    precision_horizontal=point.precision_horizontal,
                    created_at=point.created_at
                ))
        return result

    @staticmethod
    def get_parcels_for_project(
        db: Session, project_id: UUID, organization_id: UUID
    ) -> List[ParcelMapResponse]:
        """Get all parcels for a project."""
        parcels = db.query(Parcel).filter(
            Parcel.project_id == project_id
        ).all()

        return [
            ParcelMapResponse(
                id=parcel.id,
                project_id=parcel.project_id,
                parcel_number=parcel.parcel_number,
                owner_name=parcel.owner_name,
                area=parcel.area,
                municipality=parcel.municipality,
                province=parcel.province
            ) for parcel in parcels
        ]

    @staticmethod
    def get_drone_coverage_for_project(
        db: Session, project_id: UUID, organization_id: UUID
    ) -> List[DroneCoverageResponse]:
        """Get drone flight coverage areas for a project."""
        flights = db.query(DroneFlight).filter(
            DroneFlight.project_id == project_id,
            DroneFlight.organization_id == organization_id
        ).all()

        result = []
        for flight in flights:
            photos = db.query(DronePhoto).filter(
                DronePhoto.flight_id == flight.id
            ).all()

            if photos:
                convex_hull = GeospatialService.compute_convex_hull_from_photos(photos)
                result.append(DroneCoverageResponse(
                    flight_id=flight.id,
                    flight_name=flight.flight_name,
                    flight_date=flight.flight_date,
                    altitude_meters=flight.altitude_meters or 0.0,
                    area_coverage_hectares=flight.area_coverage_hectares or 0.0,
                    ground_resolution_cm=flight.ground_resolution_cm or 0.0,
                    photo_count=len(photos),
                    convex_hull_coordinates=convex_hull
                ))

        return result

    @staticmethod
    def get_project_map_data(
        db: Session, project_id: UUID, organization_id: UUID
    ) -> Optional[ProjectMapDataResponse]:
        """Get complete map data for a project."""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.organization_id == organization_id
        ).first()

        if not project:
            return None

        survey_points = GeospatialService.get_survey_points_for_project(db, project_id, organization_id)
        parcels = GeospatialService.get_parcels_for_project(db, project_id, organization_id)
        drone_coverage = GeospatialService.get_drone_coverage_for_project(db, project_id, organization_id)

        project_coords = None
        if project.location:
            project_coords = GeospatialService.extract_point_coords(project.location)

        boundary_coords = GeospatialService.compute_project_boundary(db, project_id)

        return ProjectMapDataResponse(
            project_id=project.id,
            project_name=project.name,
            project_location=project_coords,
            survey_points=survey_points,
            parcels=parcels,
            drone_coverage=drone_coverage,
            boundary_coordinates=boundary_coords
        )

    @staticmethod
    def compute_project_boundary(db: Session, project_id: UUID) -> Optional[List[List[float]]]:
        """Compute convex hull boundary of all survey points and parcels."""
        points = db.query(SurveyPoint).filter(
            SurveyPoint.project_id == project_id,
            SurveyPoint.geometry.isnot(None)
        ).all()

        if not points:
            return None

        coords = [GeospatialService.extract_point_coords(p.geometry) for p in points]
        if len(coords) < 3:
            return None

        return GeospatialService.compute_convex_hull(coords)

    @staticmethod
    def extract_point_coords(geometry) -> List[float]:
        """Extract [longitude, latitude] coordinates from PostGIS geometry."""
        try:
            if hasattr(geometry, 'coords'):
                return list(geometry.coords[0])
            return [0.0, 0.0]
        except:
            return [0.0, 0.0]

    @staticmethod
    def compute_convex_hull_from_photos(photos: List[DronePhoto]) -> Optional[List[List[float]]]:
        """Compute convex hull from drone photo GPS coordinates."""
        coords = []
        for photo in photos:
            if photo.gps_latitude is not None and photo.gps_longitude is not None:
                coords.append([photo.gps_longitude, photo.gps_latitude])

        if len(coords) < 3:
            return None

        return GeospatialService.compute_convex_hull(coords)

    @staticmethod
    def compute_convex_hull(coords: List[List[float]]) -> Optional[List[List[float]]]:
        """Compute convex hull from a list of [lon, lat] coordinates using Graham scan."""
        if len(coords) < 3:
            return None

        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        coords_sorted = sorted(set(map(tuple, coords)))

        if len(coords_sorted) <= 2:
            return None

        lower = []
        for p in coords_sorted:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)

        upper = []
        for p in reversed(coords_sorted):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        hull = lower[:-1] + upper[:-1]
        if len(hull) < 3:
            return None

        hull.append(hull[0])
        return [list(p) for p in hull]

    @staticmethod
    def get_map_bounds(
        db: Session, project_id: UUID, organization_id: UUID
    ) -> Optional[MapBoundsResponse]:
        """Get map bounds (extent) for a project."""
        points = db.query(SurveyPoint).filter(
            SurveyPoint.project_id == project_id
        ).all()

        if not points:
            return None

        lats = []
        lons = []

        for point in points:
            if point.geometry:
                coords = GeospatialService.extract_point_coords(point.geometry)
                lons.append(coords[0])
                lats.append(coords[1])

        if not lats or not lons:
            return None

        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        padding = 0.01
        return MapBoundsResponse(
            north=max_lat + padding,
            south=min_lat - padding,
            east=max_lon + padding,
            west=min_lon - padding
        )

    @staticmethod
    def create_geojson_survey_points(
        survey_points: List[SurveyPointMapResponse]
    ) -> dict:
        """Convert survey points to GeoJSON FeatureCollection."""
        features = []
        for point in survey_points:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": point.coordinates
                },
                "properties": {
                    "id": str(point.id),
                    "point_number": point.point_number,
                    "elevation": float(point.elevation) if point.elevation else None,
                    "code": point.code,
                    "description": point.description,
                    "type": "survey_point"
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    @staticmethod
    def create_geojson_parcels(
        parcels: List[ParcelMapResponse]
    ) -> dict:
        """Convert parcels to GeoJSON FeatureCollection (placeholder for polygon coords)."""
        features = []
        for parcel in parcels:
            feature = {
                "type": "Feature",
                "geometry": None,
                "properties": {
                    "id": str(parcel.id),
                    "parcel_number": parcel.parcel_number,
                    "owner_name": parcel.owner_name,
                    "area": float(parcel.area) if parcel.area else None,
                    "municipality": parcel.municipality,
                    "province": parcel.province,
                    "type": "parcel"
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    @staticmethod
    def create_geojson_drone_coverage(
        drone_coverage: List[DroneCoverageResponse]
    ) -> dict:
        """Convert drone coverage to GeoJSON FeatureCollection."""
        features = []
        for coverage in drone_coverage:
            if coverage.convex_hull_coordinates:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coverage.convex_hull_coordinates]
                    },
                    "properties": {
                        "flight_id": coverage.flight_id,
                        "flight_name": coverage.flight_name,
                        "flight_date": coverage.flight_date.isoformat(),
                        "altitude_meters": coverage.altitude_meters,
                        "area_coverage_hectares": coverage.area_coverage_hectares,
                        "ground_resolution_cm": coverage.ground_resolution_cm,
                        "photo_count": coverage.photo_count,
                        "type": "drone_coverage"
                    }
                }
                features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }
