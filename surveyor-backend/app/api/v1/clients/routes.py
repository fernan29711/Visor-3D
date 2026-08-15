"""Client endpoints."""

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user, require_admin, get_org_id
from app.schemas.clients import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from app.services.client_service import ClientService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    request: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new client in organization."""
    try:
        service = ClientService(db)
        client = service.create(str(current_user.organization_id), request)
        return client
    except AppException as e:
        raise http_exception(e)

@router.get("", response_model=list[ClientListResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List clients in organization."""
    try:
        service = ClientService(db)
        clients = service.list_by_organization(
            str(current_user.organization_id),
            skip=skip,
            limit=limit,
            search=search
        )
        return clients
    except AppException as e:
        raise http_exception(e)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get client by ID."""
    try:
        service = ClientService(db)
        client = service.get_by_id(client_id, str(current_user.organization_id))
        return client
    except AppException as e:
        raise http_exception(e)

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    request: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update client."""
    try:
        service = ClientService(db)
        client = service.update(client_id, str(current_user.organization_id), request)
        return client
    except AppException as e:
        raise http_exception(e)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete client."""
    try:
        service = ClientService(db)
        service.delete(client_id, str(current_user.organization_id))
        return None
    except AppException as e:
        raise http_exception(e)

@router.get("/{client_id}/projects")
async def get_client_projects(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get projects for a client."""
    try:
        from app.services.project_service import ProjectService
        service = ClientService(db)
        # Verify client exists
        service.get_by_id(client_id, str(current_user.organization_id))

        # Get projects
        project_service = ProjectService(db)
        projects = project_service.list_by_organization(
            str(current_user.organization_id),
            search=None
        )
        projects = [p for p in projects if str(p.client_id) == client_id]
        return projects
    except AppException as e:
        raise http_exception(e)
