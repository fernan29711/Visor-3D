"""Organization endpoints."""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user, require_admin, get_org_id
from app.schemas.organizations import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.services.organization_service import OrganizationService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List organizations (superadmin only)."""
    from app.db.models import UserRole

    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    try:
        service = OrganizationService(db)
        organizations = service.list_all(skip=skip, limit=limit)
        return organizations
    except AppException as e:
        raise http_exception(e)

@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's organization."""
    try:
        service = OrganizationService(db)
        org = service.get_by_id(str(current_user.organization_id))
        return org
    except AppException as e:
        raise http_exception(e)

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get organization by ID (must belong to org or be superadmin)."""
    from app.db.models import UserRole

    if current_user.role != UserRole.SUPERADMIN and str(current_user.organization_id) != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        service = OrganizationService(db)
        org = service.get_by_id(org_id)
        return org
    except AppException as e:
        raise http_exception(e)

@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    request: OrganizationUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update organization (admin only)."""
    if str(current_user.organization_id) != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        service = OrganizationService(db)
        org = service.update(org_id, request)
        return org
    except AppException as e:
        raise http_exception(e)

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete organization (admin only)."""
    from app.db.models import UserRole

    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Superadmin access required")

    try:
        service = OrganizationService(db)
        service.delete(org_id)
        return None
    except AppException as e:
        raise http_exception(e)
