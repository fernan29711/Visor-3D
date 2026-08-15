"""Quote service."""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import uuid4
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.models import Quote, Client, User, QuoteStatus
from app.core.exceptions import QuoteNotFoundError, ClientNotFoundError, AppException
from app.schemas.quotes import QuoteCreate, QuoteUpdate, QuoteLineItemCreate

class QuoteLineItem:
    """In-memory quote line item."""
    def __init__(self, description: str, quantity: float, unit_price: Decimal, unit: str = "unit"):
        self.id = str(uuid4())
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.unit = unit
        self.subtotal = quantity * unit_price

class QuoteService:
    """Quote service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, org_id: str, user_id: str, request: QuoteCreate) -> dict:
        """Create new quote."""
        # Verify client exists
        client = self.db.query(Client).filter(
            Client.id == request.client_id,
            Client.organization_id == org_id
        ).first()

        if not client:
            raise ClientNotFoundError()

        # Calculate totals
        line_items = []
        subtotal = Decimal(0)

        for item in request.line_items:
            line_item = QuoteLineItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                unit=item.unit
            )
            line_items.append(line_item)
            subtotal += line_item.subtotal

        # Calculate discount and tax
        discount = subtotal * (Decimal(request.discount_percentage) / Decimal(100))
        subtotal_after_discount = subtotal - discount
        tax = subtotal_after_discount * (Decimal(request.tax_percentage) / Decimal(100))
        total = subtotal_after_discount + tax

        # Calculate valid_until date
        valid_until = datetime.utcnow() + timedelta(days=request.valid_days)

        # Create quote in database
        quote = Quote(
            id=str(uuid4()),
            organization_id=org_id,
            code=request.code,
            client_id=request.client_id,
            status=QuoteStatus.DRAFT,
            total=total,
            tax=tax,
            valid_until=valid_until,
            notes=request.notes,
            created_by_user_id=user_id
        )

        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)

        # Return quote with line items
        return {
            "id": quote.id,
            "code": quote.code,
            "client_id": quote.client_id,
            "client_name": client.name,
            "client_email": client.email,
            "status": quote.status,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total": quote.total,
            "valid_until": quote.valid_until,
            "created_at": quote.created_at,
            "notes": quote.notes,
            "line_items": [
                {
                    "id": item.id,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "unit": item.unit,
                    "subtotal": item.subtotal
                }
                for item in line_items
            ]
        }

    def get_by_id(self, quote_id: str, org_id: str) -> Quote:
        """Get quote by ID (must belong to org)."""
        quote = self.db.query(Quote).filter(
            Quote.id == quote_id,
            Quote.organization_id == org_id
        ).first()

        if not quote:
            raise QuoteNotFoundError()

        return quote

    def get_by_code(self, quote_code: str, org_id: str) -> Quote:
        """Get quote by code."""
        quote = self.db.query(Quote).filter(
            Quote.code == quote_code,
            Quote.organization_id == org_id
        ).first()

        if not quote:
            raise QuoteNotFoundError()

        return quote

    def list_by_organization(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 20,
        status: str = None,
        search: str = None
    ):
        """List quotes in organization with optional filters."""
        query = self.db.query(Quote).filter(
            Quote.organization_id == org_id
        )

        if status:
            query = query.filter(Quote.status == status)

        if search:
            query = query.filter(
                Quote.code.ilike(f"%{search}%")
            )

        return query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_client(
        self,
        org_id: str,
        client_id: str,
        skip: int = 0,
        limit: int = 20
    ):
        """List quotes for a specific client."""
        return self.db.query(Quote).filter(
            Quote.organization_id == org_id,
            Quote.client_id == client_id
        ).order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()

    def update_status(self, quote_id: str, org_id: str, new_status: str) -> Quote:
        """Update quote status."""
        quote = self.get_by_id(quote_id, org_id)
        quote.status = new_status
        self.db.commit()
        self.db.refresh(quote)
        return quote

    def update(self, quote_id: str, org_id: str, request: QuoteUpdate) -> Quote:
        """Update quote."""
        quote = self.get_by_id(quote_id, org_id)

        if request.status:
            quote.status = request.status

        if request.notes is not None:
            quote.notes = request.notes

        if request.valid_days:
            quote.valid_until = datetime.utcnow() + timedelta(days=request.valid_days)

        self.db.commit()
        self.db.refresh(quote)
        return quote

    def delete(self, quote_id: str, org_id: str) -> bool:
        """Delete quote."""
        quote = self.get_by_id(quote_id, org_id)
        self.db.delete(quote)
        self.db.commit()
        return True

    def get_quote_summary(self, org_id: str) -> dict:
        """Get quote summary statistics."""
        quotes = self.db.query(Quote).filter(
            Quote.organization_id == org_id
        ).all()

        draft_count = sum(1 for q in quotes if q.status == "draft")
        sent_count = sum(1 for q in quotes if q.status == "sent")
        accepted_count = sum(1 for q in quotes if q.status == "accepted")
        rejected_count = sum(1 for q in quotes if q.status == "rejected")

        total_value = sum(q.total for q in quotes if q.status in ["sent", "accepted"])
        accepted_value = sum(q.total for q in quotes if q.status == "accepted")

        return {
            "total_quotes": len(quotes),
            "draft": draft_count,
            "sent": sent_count,
            "accepted": accepted_count,
            "rejected": rejected_count,
            "total_value": total_value,
            "accepted_value": accepted_value,
            "acceptance_rate": (accepted_count / len(quotes) * 100) if quotes else 0
        }

    def get_quote_with_details(self, quote_id: str, org_id: str) -> dict:
        """Get quote with all details including client info."""
        quote = self.get_by_id(quote_id, org_id)

        client = self.db.query(Client).filter(
            Client.id == quote.client_id
        ).first()

        # For now, return line items as stored data
        # In a real app, you'd have a QuoteLineItem table
        return {
            "id": quote.id,
            "code": quote.code,
            "client_id": quote.client_id,
            "client_name": client.name if client else "Unknown",
            "client_email": client.email if client else "",
            "status": quote.status,
            "total": quote.total,
            "tax": quote.tax,
            "valid_until": quote.valid_until,
            "created_at": quote.created_at,
            "notes": quote.notes
        }
