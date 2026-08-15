"""Dependency injection for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_user_from_token
from app.core.exceptions import InvalidTokenError, InsufficientPermissionsError
from app.db.models import User
from app.services.auth_service import AuthService

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current user from JWT token."""
    token = credentials.credentials

    user_data = get_user_from_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = user_data.get("user_id")
    auth_service = AuthService(db)

    try:
        user = auth_service.get_current_user(token)
        return user
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

def get_org_id(
    current_user: User = Depends(get_current_user),
) -> str:
    """Get organization ID from current user."""
    return str(current_user.organization_id)

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require user to have admin or superadmin role."""
    from app.db.models import UserRole

    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user

def require_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require user to have superadmin role."""
    from app.db.models import UserRole

    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required",
        )

    return current_user
