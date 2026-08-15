"""Survey points service."""

from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List

from app.db.models import SurveyPoint, Project
from app.core.exceptions import ProjectNotFoundError
from app.schemas.survey_points import SurveyPointCreate, SurveyPointUpdate

class SurveyService:
    """Survey points service."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        project_id: str,
        org_id: str,
        user_id: str,
        request: SurveyPointCreate
    ) -> SurveyPoint:
        """Create new survey point."""
        # Verify project exists and belongs to org
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.organization_id == org_id
        ).first()

        if not project:
            raise ProjectNotFoundError()

        # Create point with geometry
        from geoalchemy2.elements import WKTElement
        point = SurveyPoint(
            id=str(uuid4()),
            project_id=project_id,
            point_number=request.point_number,
            east=request.east,
            north=request.north,
            elevation=request.elevation,
            code=request.code,
            description=request.description,
            precision_horizontal=request.precision_horizontal,
            precision_vertical=request.precision_vertical,
            gnss_status=request.gnss_status,
            pdop=request.pdop,
            satellites=request.satellites,
            observations=request.observations,
            created_by_user_id=user_id,
            geometry=WKTElement(f"POINT({request.north} {request.east})", 4326),
        )

        self.db.add(point)
        self.db.commit()
        self.db.refresh(point)
        return point

    def get_by_id(self, point_id: str, project_id: str, org_id: str) -> SurveyPoint:
        """Get survey point by ID."""
        point = self.db.query(SurveyPoint).join(Project).filter(
            SurveyPoint.id == point_id,
            SurveyPoint.project_id == project_id,
            Project.organization_id == org_id
        ).first()

        if not point:
            raise ProjectNotFoundError()

        return point

    def list_by_project(
        self,
        project_id: str,
        org_id: str,
        skip: int = 0,
        limit: int = 100
    ):
        """List survey points for a project."""
        return self.db.query(SurveyPoint).join(Project).filter(
            SurveyPoint.project_id == project_id,
            Project.organization_id == org_id
        ).order_by(SurveyPoint.point_number).offset(skip).limit(limit).all()

    def update(
        self,
        point_id: str,
        project_id: str,
        org_id: str,
        request: SurveyPointUpdate
    ) -> SurveyPoint:
        """Update survey point."""
        point = self.get_by_id(point_id, project_id, org_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(point, field, value)

        self.db.commit()
        self.db.refresh(point)
        return point

    def delete(self, point_id: str, project_id: str, org_id: str) -> bool:
        """Delete survey point."""
        point = self.get_by_id(point_id, project_id, org_id)
        self.db.delete(point)
        self.db.commit()
        return True

    def bulk_create(
        self,
        project_id: str,
        org_id: str,
        user_id: str,
        points: List[SurveyPointCreate]
    ) -> tuple:
        """Bulk create survey points."""
        # Verify project exists
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.organization_id == org_id
        ).first()

        if not project:
            raise ProjectNotFoundError()

        created = []
        errors = []

        from geoalchemy2.elements import WKTElement

        for idx, request in enumerate(points):
            try:
                point = SurveyPoint(
                    id=str(uuid4()),
                    project_id=project_id,
                    point_number=request.point_number,
                    east=request.east,
                    north=request.north,
                    elevation=request.elevation,
                    code=request.code,
                    description=request.description,
                    precision_horizontal=request.precision_horizontal,
                    precision_vertical=request.precision_vertical,
                    gnss_status=request.gnss_status,
                    pdop=request.pdop,
                    satellites=request.satellites,
                    observations=request.observations,
                    created_by_user_id=user_id,
                    geometry=WKTElement(f"POINT({request.north} {request.east})", 4326),
                )
                self.db.add(point)
                created.append(point)
            except Exception as e:
                errors.append({
                    "index": idx,
                    "point_number": request.point_number,
                    "error": str(e)
                })

        self.db.commit()
        return created, errors

    def get_project_point_count(self, project_id: str) -> int:
        """Get number of points in project."""
        return self.db.query(SurveyPoint).filter(
            SurveyPoint.project_id == project_id
        ).count()

    def get_project_bounds(self, project_id: str) -> dict:
        """Get bounding box of all points in project."""
        points = self.db.query(SurveyPoint).filter(
            SurveyPoint.project_id == project_id
        ).all()

        if not points:
            return None

        min_east = min(p.east for p in points)
        max_east = max(p.east for p in points)
        min_north = min(p.north for p in points)
        max_north = max(p.north for p in points)

        return {
            "min_east": min_east,
            "max_east": max_east,
            "min_north": min_north,
            "max_north": max_north,
        }
