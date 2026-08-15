"""Project endpoints."""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, ProjectDetailResponse
from app.services.project_service import ProjectService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new project."""
    try:
        service = ProjectService(db)
        project = service.create(
            str(current_user.organization_id),
            str(current_user.id),
            request
        )
        return project
    except AppException as e:
        raise http_exception(e)

@router.get("", response_model=list[ProjectListResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List projects in organization."""
    try:
        service = ProjectService(db)
        projects = service.list_by_organization(
            str(current_user.organization_id),
            skip=skip,
            limit=limit,
            status=status,
            search=search
        )
        return projects
    except AppException as e:
        raise http_exception(e)

@router.get("/summary")
async def get_projects_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get projects summary by status."""
    try:
        service = ProjectService(db)
        summary = service.get_project_summary(str(current_user.organization_id))
        return summary
    except AppException as e:
        raise http_exception(e)

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get project details."""
    try:
        from app.services.survey_service import SurveyService
        service = ProjectService(db)
        project = service.get_by_id(project_id, str(current_user.organization_id))

        # Get point count
        survey_service = SurveyService(db)
        point_count = survey_service.get_project_point_count(project_id)

        # Create response with point count
        response = ProjectDetailResponse.model_validate(project)
        response.point_count = point_count
        return response
    except AppException as e:
        raise http_exception(e)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update project."""
    try:
        service = ProjectService(db)
        project = service.update(
            project_id,
            str(current_user.organization_id),
            request
        )
        return project
    except AppException as e:
        raise http_exception(e)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete project."""
    try:
        service = ProjectService(db)
        service.delete(project_id, str(current_user.organization_id))
        return None
    except AppException as e:
        raise http_exception(e)

@router.post("/{project_id}/status/{new_status}")
async def change_project_status(
    project_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change project status."""
    try:
        service = ProjectService(db)
        project = service.change_status(
            project_id,
            str(current_user.organization_id),
            new_status
        )
        return project
    except AppException as e:
        raise http_exception(e)
