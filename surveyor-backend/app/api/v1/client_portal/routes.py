"""Client portal endpoints for client self-service access."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.database import get_db
from app.db.models import User, Quote, Invoice, Project
from app.dependencies import get_current_user
from app.schemas.client_portal import (
    ClientDashboardStatsResponse,
    ClientQuoteListResponse,
    ClientInvoiceListResponse,
    ClientProjectListResponse,
    ClientProjectDetailResponse,
    ClientProfileResponse,
    ClientQuoteDetailResponse,
    ClientInvoiceDetailResponse,
    ClientNotificationResponse,
)
from app.services.permission_service import PermissionService, Permission
from app.core.exceptions import http_exception, AppException, ForbiddenError

router = APIRouter(prefix="/client-portal", tags=["Client Portal"])


@router.get("/profile", response_model=ClientProfileResponse)
async def get_client_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current client profile information."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        return {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "avatar_url": current_user.avatar_url,
            "organization_name": current_user.organization.name if current_user.organization else "",
            "organization_website": current_user.organization.website if current_user.organization else None,
        }
    except AppException as e:
        raise http_exception(e)


@router.get("/dashboard/stats", response_model=ClientDashboardStatsResponse)
async def get_client_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get dashboard statistics for client (their quotes and invoices)."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        client_id = str(current_user.id)
        org_id = str(current_user.organization_id)

        # Quotes statistics
        quotes = db.query(Quote).filter(
            Quote.client_id == client_id,
            Quote.organization_id == org_id
        ).all()

        # Invoices statistics
        invoices = db.query(Invoice).filter(
            Invoice.client_id == client_id,
            Invoice.organization_id == org_id
        ).all()

        # Projects (where client is associated)
        projects = db.query(Project).filter(
            Project.organization_id == org_id,
            Project.client_id == client_id
        ).all()

        # Calculate stats
        total_quotes = len(quotes)
        pending_quotes = sum(1 for q in quotes if q.status in ["draft", "sent"])
        accepted_quotes = sum(1 for q in quotes if q.status == "accepted")

        total_invoices = len(invoices)
        paid_invoices = sum(1 for i in invoices if i.status == "paid")
        pending_invoices = sum(1 for i in invoices if i.status in ["sent", "pending"])
        overdue_invoices = sum(1 for i in invoices if i.status == "overdue")

        total_invoiced = sum(i.total_amount for i in invoices)
        total_paid = sum(i.amount_paid for i in invoices)
        total_pending = total_invoiced - total_paid

        active_projects = sum(1 for p in projects if p.status != "completed")

        return {
            "total_quotes": total_quotes,
            "pending_quotes": pending_quotes,
            "accepted_quotes": accepted_quotes,
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "pending_invoices": pending_invoices,
            "overdue_invoices": overdue_invoices,
            "total_amount_invoiced": total_invoiced,
            "total_amount_paid": total_paid,
            "total_amount_pending": total_pending,
            "active_projects": active_projects,
        }
    except AppException as e:
        raise http_exception(e)


@router.get("/quotes", response_model=list[ClientQuoteListResponse])
async def get_client_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all quotes for the client."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        query = db.query(Quote).filter(
            Quote.client_id == str(current_user.id),
            Quote.organization_id == str(current_user.organization_id)
        )

        if status:
            query = query.filter(Quote.status == status)

        quotes = query.offset(skip).limit(limit).all()

        return [
            {
                "id": q.id,
                "quote_code": q.quote_code,
                "project_name": q.project.project_name if q.project else "N/A",
                "quote_date": q.quote_date,
                "expiration_date": q.expiration_date,
                "status": q.status,
                "total_amount": q.total_amount,
                "discount_amount": q.discount_amount or 0,
                "tax_amount": q.tax_amount or 0,
                "subtotal_amount": q.subtotal_amount,
            }
            for q in quotes
        ]
    except AppException as e:
        raise http_exception(e)


@router.get("/quotes/{quote_id}", response_model=ClientQuoteDetailResponse)
async def get_client_quote(
    quote_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed quote for client."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        quote = db.query(Quote).filter(
            Quote.id == quote_id,
            Quote.client_id == str(current_user.id),
            Quote.organization_id == str(current_user.organization_id)
        ).first()

        if not quote:
            raise ForbiddenError("No tienes acceso a esta cotización")

        return {
            "id": quote.id,
            "quote_code": quote.quote_code,
            "project_name": quote.project.project_name if quote.project else "N/A",
            "description": quote.description,
            "quote_date": quote.quote_date,
            "expiration_date": quote.expiration_date,
            "status": quote.status,
            "items": [],  # Quote items would be fetched separately
            "subtotal_amount": quote.subtotal_amount,
            "discount_amount": quote.discount_amount or 0,
            "discount_percentage": quote.discount_percentage or 0,
            "tax_amount": quote.tax_amount or 0,
            "total_amount": quote.total_amount,
            "notes": quote.notes,
            "terms_and_conditions": quote.terms_and_conditions,
            "pdf_url": f"/api/v1/quotes/{quote.id}/pdf",
        }
    except AppException as e:
        raise http_exception(e)


@router.get("/invoices", response_model=list[ClientInvoiceListResponse])
async def get_client_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all invoices for the client."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        query = db.query(Invoice).filter(
            Invoice.client_id == str(current_user.id),
            Invoice.organization_id == str(current_user.organization_id)
        )

        if status:
            query = query.filter(Invoice.status == status)

        invoices = query.offset(skip).limit(limit).all()

        return [
            {
                "id": i.id,
                "ncf": i.ncf,
                "project_name": i.project.project_name if i.project else "N/A",
                "issue_date": i.issue_date,
                "due_date": i.due_date,
                "status": i.status,
                "subtotal_amount": i.subtotal_amount,
                "tax_amount": i.tax_amount or 0,
                "total_amount": i.total_amount,
                "amount_paid": i.amount_paid or 0,
                "days_overdue": (
                    (db.func.current_date() - i.due_date).days
                    if i.status == "overdue" else 0
                ),
            }
            for i in invoices
        ]
    except AppException as e:
        raise http_exception(e)


@router.get("/invoices/{invoice_id}", response_model=ClientInvoiceDetailResponse)
async def get_client_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed invoice for client."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.client_id == str(current_user.id),
            Invoice.organization_id == str(current_user.organization_id)
        ).first()

        if not invoice:
            raise ForbiddenError("No tienes acceso a esta factura")

        remaining = invoice.total_amount - (invoice.amount_paid or 0)

        return {
            "id": invoice.id,
            "ncf": invoice.ncf,
            "project_name": invoice.project.project_name if invoice.project else "N/A",
            "quote_code": invoice.quote.quote_code if invoice.quote else None,
            "invoice_date": invoice.invoice_date,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "status": invoice.status,
            "items": [],  # Invoice items would be fetched separately
            "subtotal_amount": invoice.subtotal_amount,
            "tax_amount": invoice.tax_amount or 0,
            "total_amount": invoice.total_amount,
            "amount_paid": invoice.amount_paid or 0,
            "remaining_amount": remaining,
            "days_overdue": 0,  # Would be calculated based on due_date
            "payment_methods": [],  # Configured payment methods
            "payment_history": [],  # Historical payments
            "notes": invoice.notes,
            "pdf_url": f"/api/v1/invoices/{invoice.id}/pdf",
        }
    except AppException as e:
        raise http_exception(e)


@router.get("/projects", response_model=list[ClientProjectListResponse])
async def get_client_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all projects for the client."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        projects = db.query(Project).filter(
            Project.client_id == str(current_user.id),
            Project.organization_id == str(current_user.organization_id)
        ).offset(skip).limit(limit).all()

        return [
            {
                "id": p.id,
                "project_name": p.project_name,
                "location": p.location,
                "status": p.status,
                "start_date": p.start_date,
                "estimated_end_date": p.estimated_end_date,
                "total_budget": p.total_budget or 0,
                "total_spent": p.total_spent or 0,
                "progress_percentage": int((p.total_spent or 0) / (p.total_budget or 1) * 100) if p.total_budget else 0,
                "description": p.description,
            }
            for p in projects
        ]
    except AppException as e:
        raise http_exception(e)


@router.get("/projects/{project_id}", response_model=ClientProjectDetailResponse)
async def get_client_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed project for client."""
    try:
        if current_user.role != "client":
            raise ForbiddenError("Solo clientes pueden acceder a este portal")

        project = db.query(Project).filter(
            Project.id == project_id,
            Project.client_id == str(current_user.id),
            Project.organization_id == str(current_user.organization_id)
        ).first()

        if not project:
            raise ForbiddenError("No tienes acceso a este proyecto")

        # Get related quotes and invoices
        quotes = db.query(Quote).filter(
            Quote.project_id == project_id,
            Quote.organization_id == str(current_user.organization_id)
        ).all()

        invoices = db.query(Invoice).filter(
            Invoice.project_id == project_id,
            Invoice.organization_id == str(current_user.organization_id)
        ).all()

        return {
            "id": project.id,
            "project_name": project.project_name,
            "location": project.location,
            "description": project.description,
            "status": project.status,
            "start_date": project.start_date,
            "estimated_end_date": project.estimated_end_date,
            "total_budget": project.total_budget or 0,
            "total_spent": project.total_spent or 0,
            "progress_percentage": int((project.total_spent or 0) / (project.total_budget or 1) * 100) if project.total_budget else 0,
            "quotes_count": len(quotes),
            "invoices_count": len(invoices),
            "related_quotes": [
                {
                    "id": q.id,
                    "quote_code": q.quote_code,
                    "project_name": q.project.project_name if q.project else "N/A",
                    "quote_date": q.quote_date,
                    "expiration_date": q.expiration_date,
                    "status": q.status,
                    "total_amount": q.total_amount,
                    "discount_amount": q.discount_amount or 0,
                    "tax_amount": q.tax_amount or 0,
                    "subtotal_amount": q.subtotal_amount,
                }
                for q in quotes
            ],
            "related_invoices": [
                {
                    "id": i.id,
                    "ncf": i.ncf,
                    "project_name": i.project.project_name if i.project else "N/A",
                    "issue_date": i.issue_date,
                    "due_date": i.due_date,
                    "status": i.status,
                    "subtotal_amount": i.subtotal_amount,
                    "tax_amount": i.tax_amount or 0,
                    "total_amount": i.total_amount,
                    "amount_paid": i.amount_paid or 0,
                    "days_overdue": 0,
                }
                for i in invoices
            ],
        }
    except AppException as e:
        raise http_exception(e)


@router.get("/notifications", response_model=list[ClientNotificationResponse])
async def get_client_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get client notifications."""
    try:
        from app.db.models_notifications import Notification

        notifications = db.query(Notification).filter(
            Notification.user_id == str(current_user.id),
            Notification.organization_id == str(current_user.organization_id)
        ).offset(skip).limit(limit).all()

        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "priority": n.priority,
                "is_read": n.is_read,
                "created_at": n.created_at,
                "related_entity_type": n.related_entity_type,
                "related_entity_id": n.related_entity_id,
                "action_url": n.action_url,
            }
            for n in notifications
        ]
    except AppException as e:
        raise http_exception(e)
