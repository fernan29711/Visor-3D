"""Invoice service."""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.models import Invoice, Client, Project
from app.core.exceptions import AppException
from app.schemas.invoices import InvoiceCreate, InvoiceUpdate

class InvoiceService:
    """Invoice service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, org_id: str, request: InvoiceCreate) -> dict:
        """Create new invoice."""
        # Verify client exists
        client = self.db.query(Client).filter(
            Client.id == request.client_id,
            Client.organization_id == org_id
        ).first()

        if not client:
            raise AppException("Client not found")

        # Verify project if provided
        project = None
        if request.project_id:
            project = self.db.query(Project).filter(
                Project.id == request.project_id,
                Project.organization_id == org_id
            ).first()

        # Calculate due_date
        due_date = datetime.utcnow() + timedelta(days=request.due_days)

        # Create invoice
        invoice = Invoice(
            id=str(uuid4()),
            organization_id=org_id,
            ncf=request.ncf,
            project_id=request.project_id,
            client_id=request.client_id,
            status="draft",
            total=request.total,
            tax=request.tax,
            issue_date=datetime.utcnow(),
            due_date=due_date,
        )

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        return {
            "id": invoice.id,
            "ncf": invoice.ncf,
            "project_id": invoice.project_id,
            "client_id": invoice.client_id,
            "client_name": client.name,
            "project_name": project.name if project else None,
            "status": invoice.status,
            "total": invoice.total,
            "tax": invoice.tax,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "created_at": invoice.created_at,
        }

    def get_by_id(self, invoice_id: str, org_id: str) -> Invoice:
        """Get invoice by ID."""
        invoice = self.db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == org_id
        ).first()

        if not invoice:
            raise AppException("Invoice not found")

        return invoice

    def get_by_ncf(self, ncf: str, org_id: str) -> Invoice:
        """Get invoice by NCF."""
        invoice = self.db.query(Invoice).filter(
            Invoice.ncf == ncf,
            Invoice.organization_id == org_id
        ).first()

        if not invoice:
            raise AppException("Invoice not found")

        return invoice

    def list_by_organization(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 20,
        status: str = None
    ):
        """List invoices in organization with optional filters."""
        query = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id
        )

        if status:
            query = query.filter(Invoice.status == status)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_client(
        self,
        org_id: str,
        client_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        """List invoices for a specific client."""
        return self.db.query(Invoice).filter(
            Invoice.organization_id == org_id,
            Invoice.client_id == client_id
        ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_project(
        self,
        org_id: str,
        project_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        """List invoices for a specific project."""
        return self.db.query(Invoice).filter(
            Invoice.organization_id == org_id,
            Invoice.project_id == project_id
        ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, invoice_id: str, org_id: str, new_status: str) -> Invoice:
        """Update invoice status."""
        invoice = self.get_by_id(invoice_id, org_id)
        invoice.status = new_status
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def update(self, invoice_id: str, org_id: str, request: InvoiceUpdate) -> Invoice:
        """Update invoice."""
        invoice = self.get_by_id(invoice_id, org_id)

        if request.status:
            invoice.status = request.status

        if request.notes is not None:
            invoice.notes = request.notes

        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete(self, invoice_id: str, org_id: str) -> bool:
        """Delete invoice."""
        invoice = self.get_by_id(invoice_id, org_id)
        self.db.delete(invoice)
        self.db.commit()
        return True

    def get_invoice_summary(self, org_id: str) -> dict:
        """Get invoice summary statistics."""
        invoices = self.db.query(Invoice).filter(
            Invoice.organization_id == org_id
        ).all()

        draft_count = sum(1 for i in invoices if i.status == "draft")
        sent_count = sum(1 for i in invoices if i.status == "sent")
        paid_count = sum(1 for i in invoices if i.status == "paid")
        pending_count = sum(1 for i in invoices if i.status == "pending")

        total_issued = sum(i.total for i in invoices if i.status in ["sent", "paid", "pending"])
        total_paid = sum(i.total for i in invoices if i.status == "paid")
        total_pending = sum(i.total for i in invoices if i.status == "pending")

        return {
            "total_invoices": len(invoices),
            "draft": draft_count,
            "sent": sent_count,
            "paid": paid_count,
            "pending": pending_count,
            "total_issued": total_issued,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "collection_rate": (total_paid / total_issued * 100) if total_issued > 0 else 0
        }

    def get_invoice_with_details(self, invoice_id: str, org_id: str) -> dict:
        """Get invoice with all details."""
        invoice = self.get_by_id(invoice_id, org_id)

        client = self.db.query(Client).filter(
            Client.id == invoice.client_id
        ).first()

        project = None
        if invoice.project_id:
            project = self.db.query(Project).filter(
                Project.id == invoice.project_id
            ).first()

        return {
            "id": invoice.id,
            "ncf": invoice.ncf,
            "project_id": invoice.project_id,
            "client_id": invoice.client_id,
            "client_name": client.name if client else "Unknown",
            "project_name": project.name if project else None,
            "status": invoice.status,
            "total": invoice.total,
            "tax": invoice.tax,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "created_at": invoice.created_at,
        }
