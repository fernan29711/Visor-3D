"""Client service."""

from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.models import Client
from app.core.exceptions import ClientNotFoundError
from app.schemas.clients import ClientCreate, ClientUpdate

class ClientService:
    """Client service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, org_id: str, request: ClientCreate) -> Client:
        """Create new client in organization."""
        client = Client(
            id=str(uuid4()),
            organization_id=org_id,
            name=request.name,
            client_type=request.client_type,
            cedula_rnc=request.cedula_rnc,
            email=request.email,
            phone=request.phone,
            address=request.address,
            municipality=request.municipality,
            province=request.province,
            notes=request.notes,
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_by_id(self, client_id: str, org_id: str) -> Client:
        """Get client by ID (must belong to org)."""
        client = self.db.query(Client).filter(
            Client.id == client_id,
            Client.organization_id == org_id
        ).first()

        if not client:
            raise ClientNotFoundError()

        return client

    def list_by_organization(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 20,
        search: str = None
    ):
        """List clients in organization with optional search."""
        query = self.db.query(Client).filter(
            Client.organization_id == org_id
        )

        if search:
            query = query.filter(
                Client.name.ilike(f"%{search}%") |
                Client.email.ilike(f"%{search}%") |
                Client.cedula_rnc.ilike(f"%{search}%")
            )

        return query.offset(skip).limit(limit).all()

    def update(self, client_id: str, org_id: str, request: ClientUpdate) -> Client:
        """Update client."""
        client = self.get_by_id(client_id, org_id)

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client_id: str, org_id: str) -> bool:
        """Delete client."""
        client = self.get_by_id(client_id, org_id)
        self.db.delete(client)
        self.db.commit()
        return True

    def get_organization_client_count(self, org_id: str) -> int:
        """Get number of clients in organization."""
        return self.db.query(Client).filter(
            Client.organization_id == org_id
        ).count()

    def search(self, org_id: str, query: str) -> list:
        """Search clients by name or email."""
        return self.db.query(Client).filter(
            Client.organization_id == org_id,
            (Client.name.ilike(f"%{query}%")) |
            (Client.email.ilike(f"%{query}%"))
        ).limit(10).all()
