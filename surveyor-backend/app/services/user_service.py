"""User service."""

from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.models import User, Organization
from app.core.security import hash_password
from app.core.exceptions import UserNotFoundError, EmailAlreadyExistsError
from app.schemas.users import UserCreate, UserUpdate

class UserService:
    """User service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, org_id: str, request: UserCreate) -> User:
        """Create new user in organization."""
        # Check if email already exists
        existing = self.db.query(User).filter(
            User.email == request.email
        ).first()

        if existing:
            raise EmailAlreadyExistsError()

        user = User(
            id=str(uuid4()),
            organization_id=org_id,
            email=request.email,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            role=request.role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> User:
        """Get user by ID."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise UserNotFoundError()

        return user

    def get_by_email(self, email: str) -> User:
        """Get user by email."""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise UserNotFoundError()

        return user

    def list_by_organization(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        """List users in organization."""
        return self.db.query(User).filter(
            User.organization_id == org_id
        ).offset(skip).limit(limit).all()

    def update(self, user_id: str, request: UserUpdate) -> User:
        """Update user."""
        user = self.get_by_id(user_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        """Delete user."""
        user = self.get_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
        return True

    def get_organization_user_count(self, org_id: str) -> int:
        """Get number of users in organization."""
        return self.db.query(User).filter(
            User.organization_id == org_id
        ).count()
