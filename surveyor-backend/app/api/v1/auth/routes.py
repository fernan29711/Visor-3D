"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshTokenRequest, TokenResponse
from app.services.auth_service import AuthService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user and organization."""
    try:
        auth_service = AuthService(db)
        result = auth_service.register(request)
        return result
    except AppException as e:
        raise http_exception(e)

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    """Login with email and password."""
    try:
        auth_service = AuthService(db)
        result = auth_service.login(request)
        return result
    except AppException as e:
        raise http_exception(e)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService(db)
        result = auth_service.refresh_access_token(request.refresh_token)
        return result
    except AppException as e:
        raise http_exception(e)

@router.post("/logout")
async def logout(
    db: Session = Depends(get_db),
):
    """Logout (token invalidation handled client-side)."""
    return {"message": "Logged out successfully"}
