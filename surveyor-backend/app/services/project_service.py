"""Project service."""

from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.db.models import Project, ProjectStatus
from app.core.exceptions import ProjectNotFoundError
from app.schemas.projects import ProjectCreate, ProjectUpdate

class ProjectService:
    """Project service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, org_id: str, user_id: str, request: ProjectCreate) -> Project:
        """Create new project in organization."""
        # Create location if coordinates provided
        location = None
        if request.latitude is not None and request.longitude is not None:
            from geoalchemy2 import func as gis_func
            location = f"POINT({request.longitude} {request.latitude})"

        project = Project(
            id=str(uuid4()),
            organization_id=org_id,
            code=request.code,
            name=request.name,
            client_id=request.client_id,
            description=request.description,
            status=ProjectStatus.PENDING,
            municipality=request.municipality,
            province=request.province,
            budget=request.budget,
            spent=0,
            responsible_user_id=user_id,
            project_date=datetime.utcnow(),
        )

        # Set location if provided
        if request.latitude is not None and request.longitude is not None:
            from geoalchemy2.elements import WKTElement
            project.location = WKTElement(
                f"POINT({request.longitude} {request.latitude})", 4326
            )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: str, org_id: str) -> Project:
        """Get project by ID (must belong to org)."""
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.organization_id == org_id
        ).first()

        if not project:
            raise ProjectNotFoundError()

        return project

    def get_by_code(self, project_code: str, org_id: str) -> Project:
        """Get project by code."""
        project = self.db.query(Project).filter(
            Project.code == project_code,
            Project.organization_id == org_id
        ).first()

        if not project:
            raise ProjectNotFoundError()

        return project

    def list_by_organization(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 20,
        status: str = None,
        search: str = None
    ):
        """List projects in organization with optional filters."""
        query = self.db.query(Project).filter(
            Project.organization_id == org_id
        )

        if status:
            query = query.filter(Project.status == status)

        if search:
            query = query.filter(
                Project.code.ilike(f"%{search}%") |
                Project.name.ilike(f"%{search}%")
            )

        return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_user(
        self,
        org_id: str,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        """List projects where user is responsible."""
        return self.db.query(Project).filter(
            Project.organization_id == org_id,
            Project.responsible_user_id == user_id
        ).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, project_id: str, org_id: str, request: ProjectUpdate) -> Project:
        """Update project."""
        project = self.get_by_id(project_id, org_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        self.db.commit()
        self.db.refresh(project)
        return project

    def change_status(self, project_id: str, org_id: str, new_status: str) -> Project:
        """Change project status."""
        project = self.get_by_id(project_id, org_id)
        project.status = new_status
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: str, org_id: str) -> bool:
        """Delete project."""
        project = self.get_by_id(project_id, org_id)
        self.db.delete(project)
        self.db.commit()
        return True

    def get_organization_project_count(self, org_id: str, status: str = None) -> int:
        """Get number of projects in organization."""
        query = self.db.query(Project).filter(
            Project.organization_id == org_id
        )
        if status:
            query = query.filter(Project.status == status)
        return query.count()

    def get_project_summary(self, org_id: str) -> dict:
        """Get summary of projects by status."""
        statuses = ["pending", "planned", "in_field", "processing", "in_review", "completed", "delivered", "archived"]
        summary = {}

        for status in statuses:
            count = self.db.query(Project).filter(
                Project.organization_id == org_id,
                Project.status == status
            ).count()
            summary[status] = count

        return summary
