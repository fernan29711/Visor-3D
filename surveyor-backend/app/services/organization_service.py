"""Organization service."""

from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.models import Organization
from app.core.exceptions import OrganizationNotFoundError
from app.schemas.organizations import OrganizationCreate, OrganizationUpdate

class OrganizationService:
    """Organization service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, request: OrganizationCreate) -> Organization:
        """Create new organization."""
        org = Organization(
            id=str(uuid4()),
            name=request.name,
            rnc=request.rnc,
            subscription_plan=request.subscription_plan,
        )
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def get_by_id(self, org_id: str) -> Organization:
        """Get organization by ID."""
        org = self.db.query(Organization).filter(
            Organization.id == org_id
        ).first()

        if not org:
            raise OrganizationNotFoundError()

        return org

    def list_all(self, skip: int = 0, limit: int = 20):
        """List all organizations."""
        return self.db.query(Organization).offset(skip).limit(limit).all()

    def update(self, org_id: str, request: OrganizationUpdate) -> Organization:
        """Update organization."""
        org = self.get_by_id(org_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)

        self.db.commit()
        self.db.refresh(org)
        return org

    def delete(self, org_id: str) -> bool:
        """Delete organization."""
        org = self.get_by_id(org_id)
        self.db.delete(org)
        self.db.commit()
        return True

    def get_total_count(self) -> int:
        """Get total organizations count."""
        return self.db.query(Organization).count()
