"""User endpoints."""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User, UserRole
from app.dependencies import get_current_user, require_admin, get_org_id
from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.user_service import UserService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create new user in organization (admin only)."""
    try:
        service = UserService(db)
        user = service.create(str(current_user.organization_id), request)
        return user
    except AppException as e:
        raise http_exception(e)

@router.get("", response_model=list[UserListResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List users in organization."""
    try:
        service = UserService(db)
        users = service.list_by_organization(
            str(current_user.organization_id),
            skip=skip,
            limit=limit
        )
        return users
    except AppException as e:
        raise http_exception(e)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user by ID (must be in same org)."""
    try:
        service = UserService(db)
        user = service.get_by_id(user_id)

        if str(user.organization_id) != str(current_user.organization_id):
            if current_user.role != UserRole.SUPERADMIN:
                raise HTTPException(status_code=403, detail="Access denied")

        return user
    except AppException as e:
        raise http_exception(e)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user (admin or self)."""
    if str(user_id) != str(current_user.id) and current_user.role == UserRole.AGRIMENSOR:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        service = UserService(db)
        user = service.update(user_id, request)
        return user
    except AppException as e:
        raise http_exception(e)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete user (admin only)."""
    if str(user_id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    try:
        service = UserService(db)
        service.delete(user_id)
        return None
    except AppException as e:
        raise http_exception(e)
