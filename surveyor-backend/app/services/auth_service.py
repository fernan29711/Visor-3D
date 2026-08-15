"""Authentication service."""

from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from app.db.models import User, Organization, UserRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    UserNotFoundError,
    InvalidTokenError,
)
from app.schemas.auth import LoginRequest, RegisterRequest

class AuthService:
    """Authentication service."""

    def __init__(self, db: Session):
        self.db = db

    def register(self, request: RegisterRequest) -> dict:
        """Register a new user and organization."""
        # Check if email already exists
        existing_user = self.db.query(User).filter(
            User.email == request.email
        ).first()

        if existing_user:
            raise EmailAlreadyExistsError()

        # Create organization
        org_id = str(uuid.uuid4())
        organization = Organization(
            id=org_id,
            name=request.organization_name,
        )
        self.db.add(organization)

        # Create user with admin role for first user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            organization_id=org_id,
            email=request.email,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            role=UserRole.ADMIN,  # First user is admin
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create tokens
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org_id": str(user.organization_id),
                "email": user.email,
                "role": user.role.value,
            }
        )
        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
                "org_id": str(user.organization_id),
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "organization_id": str(user.organization_id),
            },
        }

    def login(self, request: LoginRequest) -> dict:
        """Login user with email and password."""
        # Find user by email
        user = self.db.query(User).filter(
            User.email == request.email
        ).first()

        if not user or not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        # Create tokens
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org_id": str(user.organization_id),
                "email": user.email,
                "role": user.role.value,
            }
        )
        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
                "org_id": str(user.organization_id),
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "organization_id": str(user.organization_id),
            },
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        payload = verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise InvalidTokenError()

        user_id = payload.get("sub")
        org_id = payload.get("org_id")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise UserNotFoundError()

        # Create new access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org_id": str(user.organization_id),
                "email": user.email,
                "role": user.role.value,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800,
        }

    def get_current_user(self, token: str) -> User:
        """Get current user from token."""
        payload = verify_token(token)

        if not payload:
            raise InvalidTokenError()

        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise UserNotFoundError()

        return user

    def logout(self, user_id: str) -> bool:
        """Logout user (currently just returns True)."""
        return True
