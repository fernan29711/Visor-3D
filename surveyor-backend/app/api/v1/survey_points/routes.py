"""Survey points endpoints."""

from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.survey_points import (
    SurveyPointCreate,
    SurveyPointUpdate,
    SurveyPointResponse,
    SurveyPointListResponse,
    SurveyPointBulkImport,
    ImportResponse,
)
from app.services.survey_service import SurveyService
from app.core.exceptions import http_exception, AppException
from app.api.v1.survey_points.csv_import import CSVImportParser
from app.api.v1.survey_points.csv_export import CSVExporter

router = APIRouter(prefix="/projects/{project_id}/survey-points", tags=["Survey Points"])

@router.post("", response_model=SurveyPointResponse, status_code=status.HTTP_201_CREATED)
async def create_survey_point(
    project_id: str,
    request: SurveyPointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new survey point."""
    try:
        service = SurveyService(db)
        point = service.create(
            project_id,
            str(current_user.organization_id),
            str(current_user.id),
            request
        )
        return point
    except AppException as e:
        raise http_exception(e)

@router.get("", response_model=list[SurveyPointListResponse])
async def list_survey_points(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List survey points for project."""
    try:
        service = SurveyService(db)
        points = service.list_by_project(
            project_id,
            str(current_user.organization_id),
            skip=skip,
            limit=limit
        )
        return points
    except AppException as e:
        raise http_exception(e)

@router.get("/{point_id}", response_model=SurveyPointResponse)
async def get_survey_point(
    project_id: str,
    point_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get survey point details."""
    try:
        service = SurveyService(db)
        point = service.get_by_id(
            point_id,
            project_id,
            str(current_user.organization_id)
        )
        return point
    except AppException as e:
        raise http_exception(e)

@router.patch("/{point_id}", response_model=SurveyPointResponse)
async def update_survey_point(
    project_id: str,
    point_id: str,
    request: SurveyPointUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update survey point."""
    try:
        service = SurveyService(db)
        point = service.update(
            point_id,
            project_id,
            str(current_user.organization_id),
            request
        )
        return point
    except AppException as e:
        raise http_exception(e)

@router.delete("/{point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey_point(
    project_id: str,
    point_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete survey point."""
    try:
        service = SurveyService(db)
        service.delete(point_id, project_id, str(current_user.organization_id))
        return None
    except AppException as e:
        raise http_exception(e)

@router.post("/bulk/import", response_model=ImportResponse)
async def bulk_import_points(
    project_id: str,
    request: SurveyPointBulkImport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk import survey points."""
    try:
        service = SurveyService(db)
        created, errors = service.bulk_create(
            project_id,
            str(current_user.organization_id),
            str(current_user.id),
            request.points
        )

        return ImportResponse(
            imported_count=len(created),
            failed_count=len(errors),
            errors=errors,
            message=f"Imported {len(created)} points successfully"
        )
    except AppException as e:
        raise http_exception(e)

@router.get("/{project_id}/bounds")
async def get_project_bounds(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get bounding box of all points in project."""
    try:
        service = SurveyService(db)
        bounds = service.get_project_bounds(project_id)
        return bounds or {"message": "No points found"}
    except AppException as e:
        raise http_exception(e)

@router.post("/csv/upload", response_model=ImportResponse)
async def upload_csv_file(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and import survey points from CSV file."""
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')

        # Parse CSV
        parser = CSVImportParser()
        points = parser.parse_csv(csv_content)

        # Validate points
        validation = parser.validate_points(points)

        if not validation['valid']:
            return ImportResponse(
                imported_count=0,
                failed_count=validation['error_count'],
                errors=validation['errors'],
                message=f"CSV validation failed: {validation['error_count']} errors"
            )

        # Create SurveyPointCreate objects from valid points
        from app.schemas.survey_points import SurveyPointCreate
        point_creates = [
            SurveyPointCreate(**point) for point in validation['valid_points']
        ]

        # Import points
        service = SurveyService(db)
        created, errors = service.bulk_create(
            project_id,
            str(current_user.organization_id),
            str(current_user.id),
            point_creates
        )

        return ImportResponse(
            imported_count=len(created),
            failed_count=len(errors),
            errors=errors,
            message=f"Imported {len(created)} points from CSV"
        )
    except Exception as e:
        raise http_exception(AppException(str(e)))

@router.get("/csv/export")
async def export_csv(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export survey points to CSV file."""
    try:
        service = SurveyService(db)
        points = service.list_by_project(
            project_id,
            str(current_user.organization_id),
            limit=10000
        )

        # Convert to dictionaries
        point_dicts = [
            {
                'point_number': p.point_number,
                'east': p.east,
                'north': p.north,
                'elevation': p.elevation,
                'pdop': p.pdop,
                'hdop': p.hdop,
                'vdop': p.vdop,
                'satellite_count': p.satellite_count,
                'description': p.description,
            }
            for p in points
        ]

        # Export to CSV
        exporter = CSVExporter()
        csv_content = exporter.export_survey_points(point_dicts)

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=survey_points_{project_id}.csv"}
        )
    except AppException as e:
        raise http_exception(e)

@router.get("/geojson/export")
async def export_geojson(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export survey points to GeoJSON file."""
    try:
        service = SurveyService(db)
        points = service.list_by_project(
            project_id,
            str(current_user.organization_id),
            limit=10000
        )

        # Convert to dictionaries
        point_dicts = [
            {
                'point_number': p.point_number,
                'east': p.east,
                'north': p.north,
                'elevation': p.elevation,
                'pdop': p.pdop,
                'hdop': p.hdop,
                'vdop': p.vdop,
                'satellite_count': p.satellite_count,
                'description': p.description,
            }
            for p in points
        ]

        # Export to GeoJSON
        exporter = CSVExporter()
        geojson_content = exporter.export_geojson(point_dicts)

        return StreamingResponse(
            iter([geojson_content]),
            media_type="application/geo+json",
            headers={"Content-Disposition": f"attachment; filename=survey_points_{project_id}.geojson"}
        )
    except AppException as e:
        raise http_exception(e)
