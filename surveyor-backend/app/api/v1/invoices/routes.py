"""Invoice endpoints."""

from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceDetailResponse,
)
from app.services.invoice_service import InvoiceService
from app.services.pdf_service import PDFService
from app.core.exceptions import http_exception, AppException

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("", response_model=InvoiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    request: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new invoice."""
    try:
        service = InvoiceService(db)
        invoice = service.create(str(current_user.organization_id), request)
        return invoice
    except AppException as e:
        raise http_exception(e)

@router.get("", response_model=list[InvoiceListResponse])
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List invoices in organization."""
    try:
        service = InvoiceService(db)
        invoices = service.list_by_organization(
            str(current_user.organization_id),
            skip=skip,
            limit=limit,
            status=status
        )
        return invoices
    except AppException as e:
        raise http_exception(e)

@router.get("/summary")
async def get_invoices_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoices summary by status."""
    try:
        service = InvoiceService(db)
        summary = service.get_invoice_summary(str(current_user.organization_id))
        return summary
    except AppException as e:
        raise http_exception(e)

@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoice details."""
    try:
        service = InvoiceService(db)
        invoice = service.get_invoice_with_details(invoice_id, str(current_user.organization_id))
        return invoice
    except AppException as e:
        raise http_exception(e)

@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    request: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update invoice."""
    try:
        service = InvoiceService(db)
        invoice = service.update(
            invoice_id,
            str(current_user.organization_id),
            request
        )
        return invoice
    except AppException as e:
        raise http_exception(e)

@router.post("/{invoice_id}/status/{new_status}", response_model=InvoiceResponse)
async def change_invoice_status(
    invoice_id: str,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change invoice status."""
    try:
        service = InvoiceService(db)
        invoice = service.update_status(
            invoice_id,
            str(current_user.organization_id),
            new_status
        )
        return invoice
    except AppException as e:
        raise http_exception(e)

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete invoice."""
    try:
        service = InvoiceService(db)
        service.delete(invoice_id, str(current_user.organization_id))
        return None
    except AppException as e:
        raise http_exception(e)

@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download invoice as PDF."""
    try:
        service = InvoiceService(db)
        invoice_data = service.get_invoice_with_details(invoice_id, str(current_user.organization_id))
        pdf_buffer = PDFService.generate_invoice_pdf(invoice_data)
        ncf = invoice_data.get('ncf', invoice_id)
        return FileResponse(
            pdf_buffer,
            media_type="application/pdf",
            filename=f"factura_{ncf}.pdf"
        )
    except AppException as e:
        raise http_exception(e)

@router.get("/client/{client_id}")
async def get_client_invoices(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoices for a specific client."""
    try:
        service = InvoiceService(db)
        invoices = service.list_by_client(
            str(current_user.organization_id),
            client_id,
            skip=skip,
            limit=limit
        )
        return invoices
    except AppException as e:
        raise http_exception(e)

@router.get("/project/{project_id}")
async def get_project_invoices(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoices for a specific project."""
    try:
        service = InvoiceService(db)
        invoices = service.list_by_project(
            str(current_user.organization_id),
            project_id,
            skip=skip,
            limit=limit
        )
        return invoices
    except AppException as e:
        raise http_exception(e)
